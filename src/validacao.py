"""
Etapa 3: amostras para conferir a detecção de IA à mão.

Gera outputs/validacao/amostras_ia.md com, por país:
  - 30 vagas marcadas como "pede IA" (o trecho que fez a vaga contar)  -> procure falsos positivos
  - 20 vagas que CITAM IA mas não foram contadas (todas as frases com IA) -> procure falsos negativos

Rode sozinho com:  python -m src.validacao
"""

from pathlib import Path

import pandas as pd

from src.ia import classificar_secao, frases, ler_linha, normalizar, tipos_na_frase

ARQUIVO = Path("data/processed/vagas_limpas.csv")
SAIDA = Path("outputs/validacao/amostras_ia.md")


def frases_com_ia(descricao: str) -> list[str]:
    secao, saida = "Geral", []
    for linha in normalizar(descricao).split("\n"):
        titulo, conteudo = ler_linha(linha)
        if titulo is not None:
            secao = f"{classificar_secao(titulo)} ({titulo.strip()[:30]})"
        for f in frases(conteudo):
            if tipos_na_frase(f):
                saida.append(f"[{secao}] {f[:220]}")
    return saida


def gerar(semente: int = 42) -> Path:
    df = pd.read_csv(ARQUIVO, encoding="utf-8-sig")
    partes = ["# Amostras para validar a detecção de IA\n",
              "Marque cada linha como certa ou errada. Precisão = certas ÷ total.\n"]
    for pais, d in df.groupby("pais"):
        pos = d[d["pede_ia"]].sample(min(30, int(d["pede_ia"].sum())), random_state=semente)
        partes.append(f"\n## {pais}: vagas contadas como \"pede IA\" ({len(pos)})\n")
        for _, r in pos.iterrows():
            partes.append(f"- **{r['cargo']}** | {r['nivel_ia']} | {r['secoes_ia']} — {r['title']}\n"
                          f"  > {r['trecho_ia']}")
        neg = d[d["menciona_ia"] & ~d["pede_ia"]]
        neg = neg.sample(min(20, len(neg)), random_state=semente)
        partes.append(f"\n## {pais}: citam IA mas NÃO foram contadas ({len(neg)})\n")
        for _, r in neg.iterrows():
            partes.append(f"- **{r['cargo']}** — {r['title']}")
            partes += [f"  > {f}" for f in frases_com_ia(r["description"])[:3]]
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text("\n".join(partes), encoding="utf-8")
    print(f"📝 {SAIDA}")
    return SAIDA


if __name__ == "__main__":
    gerar()
