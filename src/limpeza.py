"""
Etapa 2: limpeza, classificação e detecção de IA.

1. Junta as coletas deste projeto com as dos projetos 1 e 2 (só Brasil)
2. Remove repetidas por país: mesmo link, ou mesmo título + empresa
3. Classifica o cargo pelo título (mesmas regras do projeto 2)
4. Exige descrição e mantém só vagas publicadas nos últimos DIAS_ATRAS dias da coleta
5. Classifica senioridade e modelo de trabalho
6. Detecta se a vaga pede conhecimento em IA (src/ia.py)

Rode sozinho com:  python -m src.limpeza
Saídas: data/processed/vagas_limpas.csv, outputs/tabelas/funil.csv
"""

import re
import unicodedata
from pathlib import Path

import pandas as pd

from src import config
from src.ia import detectar

PASTA_RAW = Path("data/raw")
ARQUIVO_SAIDA = Path("data/processed/vagas_limpas.csv")
PASTA_TABELAS = Path("outputs/tabelas")


def normalizar(texto) -> str:
    if not isinstance(texto, str):
        return ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c)).lower()
    texto = re.sub(r"[*_#`>\[\]\\]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def classificar_cargo(t: str) -> str:
    if re.search(config.TITULO_ENGENHEIRO_NOME, t):
        return "Engenheiro"
    if re.search(config.TITULO_CIENTISTA_NOME, t):
        return "Cientista"
    if any(re.search(p, t) for p in config.TITULO_HIBRIDO.values()):
        return "Híbrido (excluído)"
    if re.search(config.TITULO_ENGENHEIRO_AREA, t):
        return "Engenheiro"
    if re.search(config.TITULO_CIENTISTA_AREA, t):
        return "Cientista"
    if (re.search(config.TITULO_ANALISTA_INCLUIR, t) and re.search(config.TITULO_ANALISTA_TEMA, t)
            and not re.search(config.TITULO_OUTRA_AREA, t)):
        return "Analista"
    return "Outra área"


def classificar_senioridade(t: str) -> str:
    for nivel, padrao in config.SENIORIDADE:
        if re.search(padrao, t):
            return nivel
    return config.SEM_SENIORIDADE


def classificar_modelo(linha) -> str:
    texto = f"{linha['titulo_norm']} {normalizar(linha.get('location'))}"
    for nome, padrao in config.MODELO_TRABALHO:
        if re.search(padrao, texto):
            return nome
    if str(linha.get("is_remote")).lower() == "true":
        return "Remoto"
    return "Não informado"


def _ler(arq: Path, origem: str, pais: str | None = None) -> pd.DataFrame:
    d = pd.read_csv(arq, encoding="utf-8-sig", low_memory=False)
    d["origem"] = origem
    if pais:
        d["pais"] = pais
    if "data_coleta" not in d:
        d["data_coleta"] = arq.stem.split("_")[-1]
    return d


def carregar_brutos() -> pd.DataFrame:
    partes = [_ler(a, "projeto3") for a in sorted(PASTA_RAW.glob("vagas_ia_*.csv"))]
    p2, p1 = Path(config.PASTA_RAW_PROJETO2), Path(config.PASTA_RAW_PROJETO1)
    partes += [_ler(a, "projeto2", "Brasil") for a in sorted(p2.glob("*.csv"))] if p2.exists() else []
    partes += [_ler(a, "projeto1", "Brasil") for a in sorted(p1.glob("*.csv"))] if p1.exists() else []
    if not partes:
        raise SystemExit("Nenhum CSV encontrado. Rode a coleta: python -m src.coleta")
    print(f"📂 {len(partes)} arquivo(s): projeto 3 = {len(list(PASTA_RAW.glob('vagas_ia_*.csv')))}, "
          f"projeto 2 = {p2.exists()}, projeto 1 = {p1.exists()}")
    return pd.concat(partes, ignore_index=True)


def limpar() -> pd.DataFrame:
    df = carregar_brutos()
    funil = []
    add = lambda etapa, d: funil.extend((p, etapa, int((d["pais"] == p).sum())) for p in config.PAISES)
    add("Vagas coletadas (com repetidas)", df)

    # a coleta mais nova vem primeiro: na deduplicação, é a versão que fica
    df = df.sort_values(["data_coleta", "origem"], ascending=False)
    df["titulo_norm"] = df["title"].map(normalizar)
    df["empresa_norm"] = df["company"].map(normalizar)
    df = df.drop_duplicates(subset=["pais", "job_url"])
    df = df.drop_duplicates(subset=["pais", "titulo_norm", "empresa_norm"])
    add("Sem repetidas", df)

    df["cargo"] = df["titulo_norm"].map(classificar_cargo)
    # do projeto 1, só Analista (as outras vieram de buscas por "analista")
    df = df[~((df["origem"] == "projeto1") & (df["cargo"] != "Analista"))]
    df = df[df["cargo"].isin(config.CARGOS)].copy()
    add("Dos 3 cargos (pelo título)", df)

    df = df[df["description"].map(normalizar).str.len() >= 200]
    add("Com descrição", df)

    publicada = pd.to_datetime(df["date_posted"], errors="coerce")
    coleta = pd.to_datetime(df["data_coleta"], errors="coerce")
    df = df[publicada.isna() | (publicada >= coleta - pd.Timedelta(days=config.DIAS_ATRAS))].copy()
    add(f"Publicadas até {config.DIAS_ATRAS} dias antes da coleta", df)

    df["senioridade"] = df["titulo_norm"].map(classificar_senioridade)
    df["modelo_trabalho"] = df.apply(classificar_modelo, axis=1)

    print("🤖 Detectando IA nas descrições...")
    ia = pd.DataFrame([detectar(t, d) for t, d in zip(df["title"], df["description"])], index=df.index)
    df = pd.concat([df, ia], axis=1)

    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    PASTA_TABELAS.mkdir(parents=True, exist_ok=True)
    colunas = ["pais", "cargo", "senioridade", "modelo_trabalho", "title", "company", "location",
               "date_posted", "data_coleta", "origem", "job_url", "pede_ia", "nivel_ia", "tipos_ia",
               "secoes_ia", "trecho_ia", "n_trechos_ia", "menciona_ia", "cita_ml", "description"]
    df[colunas].to_csv(ARQUIVO_SAIDA, index=False, encoding="utf-8-sig")
    f = pd.DataFrame(funil, columns=["pais", "etapa", "vagas"])
    f.to_csv(PASTA_TABELAS / "funil.csv", index=False, encoding="utf-8-sig")

    print("\n🧹 Funil:")
    print(f.pivot_table(index="etapa", columns="pais", values="vagas", sort=False).to_string())
    print("\n📊 Vagas por cargo:")
    print(pd.crosstab(df["cargo"], df["pais"]).to_string())
    print(f"\n💾 {ARQUIVO_SAIDA}")
    return df


if __name__ == "__main__":
    limpar()
