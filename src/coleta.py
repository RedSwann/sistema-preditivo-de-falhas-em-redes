"""Coleta das medicoes de ping na API publica do RIPE Atlas.

Salva a resposta original em JSON (nunca editada) e monta o CSV consolidado
em data/raw. Pode rodar quantas vezes for preciso: a chave
(measurement_id, prb_id, timestamp) impede linha duplicada no arquivo final.

Uso:
    python src/coleta.py
    python src/coleta.py --saida outra/pasta
"""
import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parent.parent
API = "https://atlas.ripe.net/api/v2"
ARQUIVO_FINAL = "todos_fluxos_probes_selecionadas.csv"
CHAVE = ["measurement_id", "prb_id", "timestamp"]

TIMEOUT_S = 120
TENTATIVAS = 3

# Fim exclusivo. Nenhuma medicao pode cair nos dois periodos.
PERIODOS = {
    "A": (datetime(2026, 9, 18, tzinfo=timezone.utc), datetime(2026, 9, 24, tzinfo=timezone.utc)),
    "B": (datetime(2026, 9, 24, tzinfo=timezone.utc), datetime(2026, 9, 30, tzinfo=timezone.utc)),
}

# Mesh de Anchors: 5 destinos e 4 probes de origem para cada um.
FLUXOS = [
    {"destino": "Japao", "measurement_id": 109063401, "anchor": 4220, "origem": "FR",
     "probes": [7202, 7796, 7819, 7825], "referencia": 7557},
    {"destino": "Brasil", "measurement_id": 25259597, "anchor": 1690, "origem": "BR",
     "probes": [6410, 6977, 7113, 7708], "referencia": 6790},
    {"destino": "Canada", "measurement_id": 23846774, "anchor": 2057, "origem": "US",
     "probes": [6811, 6884, 7346, 7809], "referencia": 6719},
    {"destino": "Reino Unido", "measurement_id": 199622940, "anchor": 4790, "origem": "TR",
     "probes": [7150, 7378, 7751, 7817], "referencia": 7789},
    {"destino": "Australia", "measurement_id": 179906321, "anchor": 4685, "origem": "ID",
     "probes": [6521, 6681, 7108, 7423], "referencia": 7767},
]


def buscar_json(url, params=None):
    """GET com timeout e nova tentativa (espera 1 s, depois 2 s)."""
    erro = None
    for tentativa in range(TENTATIVAS):
        try:
            resposta = requests.get(url, params=params, timeout=TIMEOUT_S)
            resposta.raise_for_status()
            return resposta.json()
        except requests.RequestException as e:
            erro = e
            if tentativa + 1 < TENTATIVAS:
                time.sleep(2 ** tentativa)
    raise erro


def coletar_periodo(fluxo, periodo, pasta):
    inicio, fim = PERIODOS[periodo]
    mid = fluxo["measurement_id"]
    dados = buscar_json(
        f"{API}/measurements/{mid}/results/",
        {"start": int(inicio.timestamp()), "stop": int(fim.timestamp()) - 1,
         "probe_ids": ",".join(map(str, fluxo["probes"])), "format": "json"},
    )
    nome = fluxo["destino"].lower().replace(" ", "_")
    with open(pasta / f"periodo_{periodo}_measurement_{mid}_{nome}_resultados_brutos.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False)

    tabela = pd.json_normalize(dados)
    if tabela.empty:
        return tabela
    tabela = tabela[tabela["prb_id"].isin(fluxo["probes"])].copy()
    tabela["measurement_id"] = mid
    tabela["destino_pais_informado"] = fluxo["destino"]
    tabela["anchor_probe_id_informado"] = fluxo["anchor"]
    tabela["pais_origem_esperado"] = fluxo["origem"]
    tabela["probe_referencia_informada"] = fluxo["referencia"]
    tabela["periodo"] = periodo
    # O fluxo e a dupla origem + endereco de destino, nao o nome DNS.
    tabela["fluxo_id"] = tabela["prb_id"].astype(str) + "|" + tabela["dst_addr"].astype(str)
    return tabela


def consolidar(novas, destino):
    """Junta o que ja existe com o que chegou agora, sem repetir medicao."""
    if destino.exists():
        novas = [pd.read_csv(destino, low_memory=False)] + novas
    total = pd.concat(novas, ignore_index=True, sort=False)
    total = total.drop_duplicates(CHAVE, keep="first").sort_values(["fluxo_id", "timestamp"])
    temporario = destino.with_suffix(".tmp")
    total.to_csv(temporario, index=False, encoding="utf-8-sig")
    temporario.replace(destino)
    return total


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saida", type=Path, default=RAIZ / "data" / "raw")
    args = parser.parse_args()
    args.saida.mkdir(parents=True, exist_ok=True)

    partes = []
    for fluxo in FLUXOS:
        for periodo in PERIODOS:
            tabela = coletar_periodo(fluxo, periodo, args.saida)
            print(f"{fluxo['destino']:<12} periodo {periodo}: {len(tabela)} medicoes")
            if not tabela.empty:
                partes.append(tabela)
            time.sleep(0.5)

    total = consolidar(partes, args.saida / ARQUIVO_FINAL)
    print(f"{ARQUIVO_FINAL}: {len(total)} linhas | {total['fluxo_id'].nunique()} fluxos")


if __name__ == "__main__":
    main()
