"""Padroniza o bruto e calcula a ficha de baseline de cada fluxo.

A ficha usa somente o Periodo A e fica congelada: o Periodo B nunca entra na
conta. Fluxo com menos de 1.500 RTTs validos fica como baseline_insuficiente,
em vez de ganhar uma mediana inventada.

Uso:
    python src/baseline.py
"""
import argparse
import ast
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
MIN_RTT_VALIDOS_A = 1500

INICIO_A = pd.Timestamp("2026-09-18", tz="UTC")
FIM_A = pd.Timestamp("2026-09-24", tz="UTC")
INICIO_B = pd.Timestamp("2026-09-24", tz="UTC")
FIM_B = pd.Timestamp("2026-09-30", tz="UTC")


def calcular_jitter(resultado):
    """Desvio-padrao amostral dos RTTs da rajada. Precisa de 2 respostas ou mais."""
    if not isinstance(resultado, str):
        return np.nan
    try:
        respostas = ast.literal_eval(resultado)
    except (ValueError, SyntaxError):
        return np.nan
    if not isinstance(respostas, list):
        return np.nan
    rtts = []
    for resposta in respostas:
        if isinstance(resposta, dict):
            rtt = pd.to_numeric(resposta.get("rtt"), errors="coerce")
            if pd.notna(rtt) and rtt >= 0:
                rtts.append(float(rtt))
    return float(np.std(rtts, ddof=1)) if len(rtts) >= 2 else np.nan


def padronizar(bruto):
    """Cria as colunas de trabalho. RTT ausente continua vazio, nunca zero."""
    df = bruto.copy()
    df["timestamp_original"] = df["timestamp"]
    df["timestamp_utc"] = pd.to_datetime(pd.to_numeric(df["timestamp"], errors="coerce"), unit="s", utc=True)
    df["measurement_id_norm"] = pd.to_numeric(df["measurement_id"], errors="coerce")
    df["probe_id_norm"] = pd.to_numeric(df["prb_id"], errors="coerce")

    df["rtt_ms"] = pd.to_numeric(df["avg"], errors="coerce")
    df.loc[df["rtt_ms"] < 0, "rtt_ms"] = np.nan

    enviados = pd.to_numeric(df["sent"], errors="coerce")
    recebidos = pd.to_numeric(df["rcvd"], errors="coerce")
    df["perda_pct"] = np.where(
        (enviados > 0) & (recebidos >= 0) & (recebidos <= enviados),
        (enviados - recebidos) / enviados * 100,
        np.nan,
    )
    df["jitter_ms"] = df["result"].apply(calcular_jitter)
    df["periodo"] = df["periodo"].astype(str).str.strip().str.upper()
    df["fluxo_id"] = df["fluxo_id"].astype(str)

    em_a = df["periodo"].eq("A") & df["timestamp_utc"].ge(INICIO_A) & df["timestamp_utc"].lt(FIM_A)
    em_b = df["periodo"].eq("B") & df["timestamp_utc"].ge(INICIO_B) & df["timestamp_utc"].lt(FIM_B)
    df = df[(em_a | em_b) & df["probe_id_norm"].notna() & df["measurement_id_norm"].notna()]
    return df.sort_values(["fluxo_id", "timestamp_utc"]).reset_index(drop=True)


def mediana_segura(serie):
    serie = pd.to_numeric(serie, errors="coerce").dropna()
    return float(serie.median()) if len(serie) else np.nan


def ficha_do_fluxo(fluxo_id, grupo):
    rtt = grupo["rtt_ms"].dropna()
    n_validos = len(rtt)
    ficha = {
        "fluxo_id": fluxo_id,
        "n_medicoes_A": len(grupo),
        "n_rtt_validos_A": n_validos,
        "status_baseline": "baseline_ok",
        "motivo_exclusao": "",
        "mediana": np.nan, "MAD": np.nan, "IQR": np.nan,
        "jitter_tipico": np.nan, "perda_tipica": np.nan, "prop_resposta": np.nan,
    }
    if n_validos < MIN_RTT_VALIDOS_A:
        ficha["status_baseline"] = "baseline_insuficiente"
        ficha["motivo_exclusao"] = f"Apenas {n_validos} RTTs válidos no período A; mínimo de {MIN_RTT_VALIDOS_A}"
        return ficha
    mediana = float(rtt.median())
    ficha.update({
        "mediana": mediana,
        "MAD": float((rtt - mediana).abs().median()),
        "IQR": float(rtt.quantile(0.75) - rtt.quantile(0.25)),
        "jitter_tipico": mediana_segura(grupo["jitter_ms"]),
        "perda_tipica": mediana_segura(grupo["perda_pct"]),
        "prop_resposta": n_validos / len(grupo),
    })
    return ficha


def calcular_baseline(df):
    fluxos = df["fluxo_id"].drop_duplicates()
    fichas = []
    for fluxo_id in fluxos:
        grupo = df[df["fluxo_id"].eq(fluxo_id) & df["periodo"].eq("A")]
        fichas.append(ficha_do_fluxo(fluxo_id, grupo))
    baseline = pd.DataFrame(fichas)
    medicoes_a = df[df["periodo"].eq("A")].groupby("fluxo_id")["timestamp_utc"].agg(["min", "max"])
    baseline["periodo_baseline"] = "A"
    baseline["inicio_periodo_A_utc"] = INICIO_A.isoformat()
    baseline["fim_periodo_A_exclusivo_utc"] = FIM_A.isoformat()
    baseline["primeira_medicao_A_utc"] = baseline["fluxo_id"].map(medicoes_a["min"])
    baseline["ultima_medicao_A_utc"] = baseline["fluxo_id"].map(medicoes_a["max"])
    baseline["baseline_valido"] = baseline["status_baseline"].eq("baseline_ok")
    baseline["recomendacao_uso"] = np.where(baseline["baseline_valido"], "usar", "nao_usar_baseline_insuficiente")
    return baseline


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, default=RAIZ / "data" / "raw")
    parser.add_argument("--saida", type=Path, default=RAIZ / "data" / "processed")
    args = parser.parse_args()
    args.saida.mkdir(parents=True, exist_ok=True)

    bruto = pd.read_csv(args.raw / "todos_fluxos_probes_selecionadas.csv", low_memory=False)
    df = padronizar(bruto)
    baseline = calcular_baseline(df)
    baseline.to_csv(args.saida / "baseline_por_fluxo.csv", index=False, encoding="utf-8-sig")
    print(f"{len(df)} medicoes | {baseline['baseline_valido'].sum()} fluxos com baseline | "
          f"{(~baseline['baseline_valido']).sum()} excluidos")


if __name__ == "__main__":
    main()
