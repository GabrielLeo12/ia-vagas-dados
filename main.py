"""
Roda o projeto: coleta -> limpeza (com detecção de IA) -> amostras de validação -> análise.

    python main.py                 # tudo (Brasil e EUA)
    python main.py --pais EUA      # coleta só um país e roda o resto
    python main.py --pular-coleta  # usa os CSVs que já estão em data/raw/
"""

import argparse

from src import config
from src.analise import analisar
from src.limpeza import limpar
from src.validacao import gerar as gerar_amostras

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Quantas vagas de dados pedem conhecimento em IA?")
    parser.add_argument("--pular-coleta", action="store_true")
    parser.add_argument("--pais", choices=list(config.PAISES))
    args = parser.parse_args()

    if not args.pular_coleta:
        from src.coleta import coletar
        print("=== 1/4 COLETA ===")
        coletar([args.pais] if args.pais else None)
    print("\n=== 2/4 LIMPEZA E DETECÇÃO DE IA ===")
    limpar()
    print("\n=== 3/4 AMOSTRAS PARA VALIDAÇÃO ===")
    gerar_amostras()
    print("\n=== 4/4 ANÁLISE ===")
    analisar()
    print("\n🎉 Pronto! Veja outputs/")
