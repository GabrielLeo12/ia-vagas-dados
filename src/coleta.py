"""
Etapa 1: coleta no Indeed Brasil e no Indeed EUA, por cargo.

    python -m src.coleta              # os dois países
    python -m src.coleta --pais EUA   # só um

Saída: data/raw/vagas_ia_<pais>_AAAA-MM-DD.csv  (uma linha por vaga encontrada em cada busca)
"""

import argparse
import time
from datetime import date
from pathlib import Path

import pandas as pd
from jobspy import scrape_jobs

from src import config

PASTA_RAW = Path("data/raw")


def coletar_termo(pais: str, cargo: str, termo: str) -> pd.DataFrame:
    p = config.PAISES[pais]
    print(f"\n🔎 [{pais} | {cargo}] '{termo}' ...")
    try:
        df = scrape_jobs(
            site_name=["indeed"],
            search_term=termo,
            location=p["local"],
            country_indeed=p["country_indeed"],
            results_wanted=p["vagas_por_termo"],
            hours_old=config.DIAS_ATRAS * 24,
            description_format="markdown",
            verbose=0,
        )
    except Exception as erro:
        print(f"   ⚠️  Erro: {erro}")
        return pd.DataFrame()
    df["pais"] = pais
    df["cargo_busca"] = cargo
    df["termo_busca"] = termo
    df["data_coleta"] = date.today().isoformat()
    print(f"   ✅ {len(df)} vagas")
    return df


def coletar(paises: list[str] | None = None) -> list[Path]:
    PASTA_RAW.mkdir(parents=True, exist_ok=True)
    paises = paises or list(config.PAISES)
    buscas = [(pais, cargo, termo)
              for pais in paises
              for cargo, termos in config.PAISES[pais]["termos"].items()
              for termo in termos]
    print(f"Serão {len(buscas)} buscas ({', '.join(paises)}). Leva de 30 a 60 minutos.")

    arquivos = []
    for pais in paises:
        minhas = [b for b in buscas if b[0] == pais]
        resultados = []
        for i, (_, cargo, termo) in enumerate(minhas):
            resultados.append(coletar_termo(pais, cargo, termo))
            if i < len(minhas) - 1:
                time.sleep(config.PAUSA_ENTRE_BUSCAS)
        vagas = pd.concat(resultados, ignore_index=True)
        if vagas.empty:
            print(f"\n⚠️  Nenhuma vaga coletada para {pais}.")
            continue
        arquivo = PASTA_RAW / f"vagas_ia_{pais.lower()}_{date.today().isoformat()}.csv"
        vagas.to_csv(arquivo, index=False, encoding="utf-8-sig")
        print(f"\n📦 {pais}: {len(vagas)} vagas brutas")
        print(vagas.groupby("cargo_busca").size().to_string())
        print(f"💾 Salvo em: {arquivo}")
        arquivos.append(arquivo)
    return arquivos


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pais", choices=list(config.PAISES), help="coleta só um país")
    args = parser.parse_args()
    coletar([args.pais] if args.pais else None)
