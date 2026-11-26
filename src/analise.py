"""
Etapa 4: análise. Responde as 5 perguntas do projeto.

1. Quantas vagas de dados pedem conhecimento em IA, por cargo?
2. É requisito obrigatório ou só diferencial?
3. Vaga júnior também pede, ou só a sênior?
4. Que IA pedem (IA generativa, ChatGPT/Copilot, prompt, agentes...)?
5. Como o Brasil se compara com os EUA?

Rode sozinho com:  python -m src.analise
Saídas: outputs/tabelas/*.csv, outputs/tabelas/resumo.md, outputs/graficos/*.png
"""

import math
from pathlib import Path

import pandas as pd

from src import config, graficos

ARQUIVO = Path("data/processed/vagas_limpas.csv")
PASTA = Path("outputs/tabelas")


def wilson(k: int, n: int) -> tuple[float, float]:
    """Intervalo de confiança de 95% para uma proporção (em %)."""
    if n == 0:
        return (float("nan"), float("nan"))
    z, p = 1.96, k / n
    centro = (p + z * z / (2 * n)) / (1 + z * z / n)
    meia = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return round(100 * (centro - meia), 1), round(100 * (centro + meia), 1)


def _linha(grupo: pd.DataFrame, **chaves) -> dict:
    n, k = len(grupo), int(grupo["pede_ia"].sum())
    lo, hi = wilson(k, n)
    pct = lambda nivel: round(100 * (grupo["nivel_ia"] == nivel).sum() / n, 1) if n else None
    return {**chaves, "vagas": n, "pedem_ia": k, "pct_pede_ia": round(100 * k / n, 1) if n else None,
            "ic95_min": lo, "ic95_max": hi,
            "pct_requisito": pct("Requisito"), "pct_tarefa": pct("Tarefa"),
            "pct_so_diferencial": pct("Só diferencial"),
            "pct_menciona_ia": round(100 * grupo["menciona_ia"].mean(), 1) if n else None,
            "pct_cita_ml": round(100 * grupo["cita_ml"].mean(), 1) if n else None}


def por_cargo(df: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for pais, d in df.groupby("pais", sort=False):
        for cargo in config.CARGOS:
            linhas.append(_linha(d[d["cargo"] == cargo], pais=pais, cargo=cargo))
        linhas.append(_linha(d, pais=pais, cargo="Todos"))
    return pd.DataFrame(linhas)


def por_senioridade(df: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for (pais, cargo), d in df.groupby(["pais", "cargo"], sort=False):
        for nivel in ["Júnior", "Pleno", "Sênior"]:
            g = d[d["senioridade"] == nivel]
            if len(g):
                linhas.append(_linha(g, pais=pais, cargo=cargo, senioridade=nivel))
    t = pd.DataFrame(linhas)
    if t.empty:
        return t
    # só mostramos júnior × sênior quando os dois grupos têm vagas suficientes
    ok = (t[t["senioridade"].isin(["Júnior", "Sênior"])]
          .groupby(["pais", "cargo"])["vagas"].agg(lambda s: len(s) == 2 and s.min() >= config.MIN_VAGAS_GRUPO))
    t["comparavel"] = t.set_index(["pais", "cargo"]).index.map(ok).fillna(False)
    return t


def por_tipo(df: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for pais, d in df.groupby("pais", sort=False):
        pedem = d[d["pede_ia"]]
        for cargo in config.CARGOS + ["Todos"]:
            g = pedem if cargo == "Todos" else pedem[pedem["cargo"] == cargo]
            base = d if cargo == "Todos" else d[d["cargo"] == cargo]
            for tipo in config.TIPOS_IA:
                k = int(g["tipos_ia"].fillna("").str.contains(tipo, regex=False).sum())
                linhas.append({"pais": pais, "cargo": cargo, "tipo_ia": tipo, "vagas": k,
                               "pct_das_que_pedem_ia": round(100 * k / len(g), 1) if len(g) else None,
                               "pct_de_todas_as_vagas": round(100 * k / len(base), 1) if len(base) else None})
    return pd.DataFrame(linhas)


def por_modelo(df: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for (pais, modelo), d in df.groupby(["pais", "modelo_trabalho"], sort=False):
        linhas.append(_linha(d, pais=pais, modelo_trabalho=modelo))
    return pd.DataFrame(linhas)


def escrever_resumo(cargo, senior, tipo, modelo, df) -> None:
    def tabela(t):
        return t.to_markdown(index=False) if not t.empty else "_(sem dados)_"
    datas = pd.to_datetime(df["date_posted"], errors="coerce")
    partes = [
        "# Resumo — vagas de dados que pedem conhecimento em IA\n",
        f"Vagas analisadas: {len(df)} ({', '.join(f'{p}: {n}' for p, n in df['pais'].value_counts().items())}). "
        f"Publicadas entre {datas.min():%d/%m/%Y} e {datas.max():%d/%m/%Y}.\n",
        "## 1, 2 e 5. Por cargo e país (requisito × tarefa do dia a dia × só diferencial)\n", tabela(cargo),
        "\n\n## 3. Por senioridade (comparavel = os dois grupos têm "
        f"{config.MIN_VAGAS_GRUPO}+ vagas)\n", tabela(senior),
        "\n\n## 4. Que IA pedem\n", tabela(tipo[tipo["cargo"] == "Todos"]),
        "\n\n## Extra: por modelo de trabalho\n", tabela(modelo),
    ]
    (PASTA / "resumo.md").write_text("\n".join(partes), encoding="utf-8")


def analisar() -> None:
    df = pd.read_csv(ARQUIVO, encoding="utf-8-sig")
    PASTA.mkdir(parents=True, exist_ok=True)
    t_cargo, t_sen, t_tipo, t_mod = por_cargo(df), por_senioridade(df), por_tipo(df), por_modelo(df)
    for nome, t in [("ia_por_cargo", t_cargo), ("ia_por_senioridade", t_sen),
                    ("ia_por_tipo", t_tipo), ("ia_por_modelo_trabalho", t_mod)]:
        t.to_csv(PASTA / f"{nome}.csv", index=False, encoding="utf-8-sig")
    escrever_resumo(t_cargo, t_sen, t_tipo, t_mod, df)

    graficos.pede_ia_por_cargo(t_cargo)
    graficos.obrigatorio_diferencial(t_cargo)
    graficos.junior_senior(t_sen)
    graficos.tipos_ia(t_tipo)

    print("\n🤖 Vagas que pedem conhecimento em IA:")
    print(t_cargo[["pais", "cargo", "vagas", "pct_pede_ia", "ic95_min", "ic95_max",
                   "pct_requisito", "pct_tarefa", "pct_so_diferencial"]].to_string(index=False))
    print(f"\n💾 Tabelas em {PASTA}/  |  gráficos em outputs/graficos/")


if __name__ == "__main__":
    analisar()
