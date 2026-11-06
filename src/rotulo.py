"""Calcula os atributos do Periodo B, aplica o rotulo e monta os recortes.

A ordem da tabela de rotulo importa: vale a primeira linha verdadeira, entao
FALHA ganha de RISCO e RISCO ganha de OK.

Uso (depois de src/baseline.py):
    python src/rotulo.py
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from baseline import padronizar

RAIZ = Path(__file__).resolve().parent.parent
FEATURES = ["z_robusto", "aumento_pct", "jitter_relativo", "perda_pct",
            "timeout_atual", "n5_timeout", "n5_aumento80", "n5_risco"]
HORIZONTE_S = 12 * 60
TOLERANCIA_S = 60


def calcular_atributos(df, baseline):
    """Compara cada medicao de B com a ficha congelada do proprio fluxo."""
    colunas = ["fluxo_id", "status_baseline", "mediana", "MAD", "IQR", "jitter_tipico"]
    df = df[df["periodo"].eq("B")].merge(baseline[colunas], on="fluxo_id", how="left", validate="many_to_one")
    df = df[df["status_baseline"].eq("baseline_ok")].copy()

    tem_rtt = df["rtt_ms"].notna()
    df["timeout_atual"] = ((~tem_rtt) | df["perda_pct"].eq(100)).astype(int)

    df["aumento_pct"] = np.where(tem_rtt & df["mediana"].gt(0),
                                 (df["rtt_ms"] - df["mediana"]) / df["mediana"] * 100, np.nan)

    desvio = df["rtt_ms"] - df["mediana"]
    denominador_mad_zero = (df["IQR"].fillna(0) / 1.349).clip(lower=1.0)
    df["z_robusto"] = np.select(
        [tem_rtt & df["MAD"].gt(0), tem_rtt & df["MAD"].eq(0) & desvio.eq(0), tem_rtt & df["MAD"].eq(0)],
        [desvio / (1.4826 * df["MAD"]), 0.0, desvio / denominador_mad_zero],
        default=np.nan,
    )

    tem_jitter = df["jitter_ms"].notna() & df["jitter_tipico"].notna()
    df["jitter_relativo"] = np.select(
        [tem_jitter & df["jitter_tipico"].gt(0),
         tem_jitter & df["jitter_tipico"].eq(0) & df["jitter_ms"].eq(0),
         tem_jitter & df["jitter_tipico"].eq(0) & df["jitter_ms"].gt(0)],
        [df["jitter_ms"] / df["jitter_tipico"], 1.0, 3.0],
        default=np.nan,
    )

    df["aumento80_atual"] = (df["aumento_pct"] > 80).astype(int)
    df["criterio_risco_atual"] = (
        (df["z_robusto"].ge(2) & df["z_robusto"].lt(3.5))
        | df["aumento_pct"].between(30, 80, inclusive="both")
        | df["jitter_relativo"].ge(3)
    ).astype(int)

    df = df.sort_values(["fluxo_id", "timestamp_utc"]).reset_index(drop=True)
    # Janela causal: so olha a medicao atual e as 4 anteriores do mesmo fluxo.
    for saida, base in [("n5_timeout", "timeout_atual"), ("n5_aumento80", "aumento80_atual"),
                        ("n5_risco", "criterio_risco_atual")]:
        df[saida] = df.groupby("fluxo_id")[base].transform(lambda s: s.rolling(5, min_periods=1).sum())
    return df


def rotular(df):
    """Tabela de rotulo: para na primeira linha verdadeira."""
    condicoes = [
        df["perda_pct"].ge(10),
        df["n5_timeout"].ge(3),
        df["rtt_ms"].notna() & df["z_robusto"].ge(3.5),
        df["n5_aumento80"].ge(2),
        df["criterio_risco_atual"].eq(1) & df["n5_risco"].ge(2),
    ]
    df = df.copy()
    df["classe"] = np.select(condicoes, ["FALHA", "FALHA", "FALHA", "FALHA", "RISCO"], default="OK")
    df["regra_disparada"] = np.select(
        condicoes,
        ["1: perda_pct >= 10", "2: n5_timeout >= 3", "3: z_robusto >= 3.5", "4: n5_aumento80 >= 2",
         "5: critério de risco atual e n5_risco >= 2"],
        default="6: nenhuma regra anterior",
    )
    return df


def recortar_no_tempo(df):
    """Dentro de cada fluxo: 50% mais antigos, 20% seguintes, 30% mais recentes."""
    partes = []
    for _, grupo in df.groupby("fluxo_id", sort=False):
        grupo = grupo.sort_values("timestamp_utc").reset_index(drop=True)
        n = len(grupo)
        n_treino = int(np.floor(n * 0.50))
        n_valid = int(np.floor(n * 0.20))
        grupo["bloco_temporal"] = "teste"
        grupo.loc[:n_treino - 1, "bloco_temporal"] = "treino"
        grupo.loc[n_treino:n_treino + n_valid - 1, "bloco_temporal"] = "validacao"
        partes.append(grupo)
    return pd.concat(partes, ignore_index=True)


def montar_predicao(df):
    """Pareia cada medicao com o estado do mesmo fluxo perto de t + 12 min."""
    base = df.copy()
    base["status_atual"] = base["classe"]
    partes = []
    for _, grupo in base.groupby("fluxo_id", sort=False):
        atual = grupo.assign(timestamp_alvo_utc=grupo["timestamp_utc"] + pd.Timedelta(seconds=HORIZONTE_S))
        futuro = grupo[["timestamp_utc", "status_atual", "bloco_temporal"]].rename(columns={
            "timestamp_utc": "timestamp_futuro_utc", "status_atual": "status_futuro", "bloco_temporal": "bloco_futuro"})
        partes.append(pd.merge_asof(
            atual.sort_values("timestamp_alvo_utc"), futuro.sort_values("timestamp_futuro_utc"),
            left_on="timestamp_alvo_utc", right_on="timestamp_futuro_utc",
            direction="nearest", tolerance=pd.Timedelta(seconds=TOLERANCIA_S)))
    pares = pd.concat(partes, ignore_index=True)
    # O alvo nao pode faltar nem cair em outro bloco.
    aceitos = pares[pares["status_futuro"].notna() & pares["bloco_temporal"].eq(pares["bloco_futuro"])].copy()
    aceitos["horizonte_real_segundos"] = (aceitos["timestamp_futuro_utc"] - aceitos["timestamp_utc"]).dt.total_seconds()
    aceitos["previsao_persistencia"] = aceitos["status_atual"]
    return aceitos[["fluxo_id", "timestamp_utc", "periodo", "bloco_temporal"] + FEATURES + [
        "status_atual", "timestamp_alvo_utc", "timestamp_futuro_utc", "horizonte_real_segundos",
        "status_futuro", "previsao_persistencia"]]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, default=RAIZ / "data" / "raw")
    parser.add_argument("--saida", type=Path, default=RAIZ / "data" / "processed")
    args = parser.parse_args()

    bruto = pd.read_csv(args.raw / "todos_fluxos_probes_selecionadas.csv", low_memory=False)
    baseline = pd.read_csv(args.saida / "baseline_por_fluxo.csv")
    dados = recortar_no_tempo(rotular(calcular_atributos(padronizar(bruto), baseline)))
    predicao = montar_predicao(dados)

    dados.to_csv(args.saida / "dataset_B_com_recorte_temporal.csv", index=False, encoding="utf-8-sig")
    predicao.to_csv(args.saida / "dataset_predicao.csv", index=False, encoding="utf-8-sig")
    print(dados["classe"].value_counts().to_dict(), dados["bloco_temporal"].value_counts().to_dict())
    print(f"dataset_predicao.csv: {len(predicao)} linhas")


if __name__ == "__main__":
    main()
