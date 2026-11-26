"""Gráficos do projeto 3, com a identidade visual dos projetos 1 e 2 (1080 × 1350 px)."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager

from src import config

# Usa a fonte Inter se ela estiver instalada; senão, a padrão do matplotlib
if any("Inter" in f.name for f in font_manager.fontManager.ttflist):
    plt.rcParams["font.family"] = "Inter"

PASTA = Path("outputs/graficos")
FUNDO, TINTA, TINTA_2, TINTA_FRACA, TRILHO = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#ecebe6"
COR_PAIS = {"Brasil": "#2a78d6", "EUA": "#a3a19a"}
COR_OBRIG, COR_DIF = "#1f5fae", "#9ec5f4"
NOME_CARGO = {"Analista": "Analista\nde Dados", "Cientista": "Cientista\nde Dados",
              "Engenheiro": "Engenheiro\nde Dados", "Todos": "Todos"}


def _ordem_paises(paises) -> list[str]:
    """Brasil sempre primeiro (é o foco); depois os outros, na ordem do config."""
    return [p for p in config.PAISES if p in set(paises)]


def _figura(titulo: str, subtitulo: str, rodape: str):
    fig = plt.figure(figsize=(10.8, 13.5), dpi=100)
    fig.patch.set_facecolor(FUNDO)
    fig.text(0.07, 0.955, titulo, fontsize=26, fontweight="bold", color=TINTA, va="top", wrap=True)
    fig.text(0.07, 0.885, subtitulo, fontsize=14, color=TINTA_2, va="top")
    fig.text(0.07, 0.025, rodape, fontsize=11, color=TINTA_FRACA, va="bottom")
    return fig


def _rodape(paises) -> str:
    fonte = " e ".join(f"Indeed {p}" for p in paises)
    return f"Fonte: vagas públicas do {fonte}, últimos {config.DIAS_ATRAS} dias · Análise: {config.AUTOR}"


def _salvar(fig, nome: str) -> Path:
    PASTA.mkdir(parents=True, exist_ok=True)
    caminho = PASTA / nome
    fig.savefig(caminho, facecolor=FUNDO)
    plt.close(fig)
    print(f"🖼️  {caminho}")
    return caminho


def pede_ia_por_cargo(t: pd.DataFrame) -> Path:
    """Pergunta 1 e 5: % de vagas que pedem IA, por cargo, Brasil × EUA."""
    paises = _ordem_paises(t["pais"])
    cargos = config.CARGOS + ["Todos"]
    fig = _figura("Quantas vagas de dados pedem\nconhecimento em IA?",
                  "% das vagas de cada cargo que pedem IA como requisito, tarefa ou diferencial",
                  _rodape(paises))
    ax = fig.add_axes([0.27, 0.10, 0.63, 0.72])
    ax.set_facecolor(FUNDO)
    altura = 0.8 / len(paises)
    for i, cargo in enumerate(cargos):
        for j, pais in enumerate(paises):
            linha = t[(t["pais"] == pais) & (t["cargo"] == cargo)]
            if linha.empty:
                continue
            v, n = linha["pct_pede_ia"].iloc[0], linha["vagas"].iloc[0]
            y = -i - j * altura
            ax.barh(y, 100, height=altura * 0.8, color=TRILHO)
            ax.barh(y, v, height=altura * 0.8, color=COR_PAIS.get(pais, TINTA_2))
            ax.text(v + 1.5, y, f"{v:.0f}%", va="center", fontsize=17, fontweight="bold", color=TINTA)
            ax.text(101, y, f"{pais} · {n} vagas", va="center", ha="right", fontsize=11, color=TINTA_FRACA)
        ax.text(-3, -i - (len(paises) - 1) * altura / 2, NOME_CARGO[cargo], ha="right", va="center",
                fontsize=17, fontweight="bold" if cargo == "Todos" else "normal", color=TINTA)
    ax.set_xlim(0, 101)
    ax.set_ylim(-len(cargos) + 0.4, 0.6)
    ax.axis("off")
    return _salvar(fig, "pede_ia_por_cargo.png")


def obrigatorio_diferencial(t: pd.DataFrame) -> Path:
    """Pergunta 2: requisito × tarefa do dia a dia × só diferencial."""
    paises = _ordem_paises(t["pais"])
    linhas = t[t["cargo"].isin(config.CARGOS)]
    fig = _figura("Obrigatório ou só diferencial?",
                  "% das vagas de cada cargo, pelo jeito mais forte em que pedem IA", _rodape(paises))
    ax = fig.add_axes([0.27, 0.12, 0.63, 0.68])
    ax.set_facecolor(FUNDO)
    partes = [("pct_requisito", "Requisito", COR_OBRIG, "white"),
              ("pct_tarefa", "Tarefa do dia a dia", "#5b97e0", "white"),
              ("pct_so_diferencial", "Só diferencial", COR_DIF, TINTA)]
    y = 0
    for cargo in config.CARGOS:
        for pais in paises:
            l = linhas[(linhas["pais"] == pais) & (linhas["cargo"] == cargo)]
            if l.empty:
                continue
            ax.barh(y, 100, height=0.6, color=TRILHO)
            esquerda = 0
            for coluna, _, cor, cor_texto in partes:
                v = l[coluna].iloc[0]
                ax.barh(y, v, left=esquerda, height=0.6, color=cor, edgecolor=FUNDO, linewidth=2)
                if v >= 5:
                    ax.text(esquerda + v / 2, y, f"{v:.0f}%", ha="center", va="center", color=cor_texto,
                            fontsize=13, fontweight="bold")
                esquerda += v
            ax.text(esquerda + 1.5, y, f"{esquerda:.0f}%", va="center", fontsize=15, fontweight="bold", color=TINTA)
            rotulo = NOME_CARGO[cargo].replace("\n", " ") + (f"\n{pais}" if len(paises) > 1 else "")
            ax.text(-3, y, rotulo, ha="right", va="center", fontsize=14, color=TINTA)
            y -= 1
        y -= 0.4
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=c) for _, _, c, _ in partes],
              labels=[nome for _, nome, _, _ in partes], loc="lower left", frameon=False, fontsize=13,
              bbox_to_anchor=(0, 1.0), ncol=3, handlelength=1.2)
    ax.set_xlim(0, 100)
    ax.set_ylim(y + 0.6, 0.6)
    ax.axis("off")
    return _salvar(fig, "obrigatorio_diferencial.png")


def junior_senior(t: pd.DataFrame) -> Path | None:
    """Pergunta 3: júnior × sênior, só onde os dois grupos têm vagas suficientes."""
    if t.empty:
        return None
    t = t[t["comparavel"] & t["senioridade"].isin(["Júnior", "Sênior"])]
    if t.empty:
        print("ℹ️  Júnior × sênior: nenhum cargo com vagas suficientes nos dois grupos.")
        return None
    grupos = [(p, c) for p in _ordem_paises(t["pais"]) for c in config.CARGOS
              if ((t["pais"] == p) & (t["cargo"] == c)).any()]
    fig = _figura("A vaga júnior também pede IA?",
                  f"% das vagas que pedem IA, por senioridade (grupos com {config.MIN_VAGAS_GRUPO}+ vagas)",
                  _rodape(_ordem_paises(t["pais"])))
    ax = fig.add_axes([0.30, 0.14, 0.60, 0.66])
    ax.set_facecolor(FUNDO)
    for i, (pais, cargo) in enumerate(grupos):
        g = t[(t["pais"] == pais) & (t["cargo"] == cargo)].set_index("senioridade")
        jr, sr = g.loc["Júnior", "pct_pede_ia"], g.loc["Sênior", "pct_pede_ia"]
        ax.plot([jr, sr], [-i, -i], color=TRILHO, lw=10, solid_capstyle="round", zorder=1)
        ax.scatter([jr], [-i], s=420, color="#9ec5f4", zorder=2)
        ax.scatter([sr], [-i], s=420, color=COR_OBRIG, zorder=2)
        ax.text(jr, -i + 0.12, f"Júnior {jr:.0f}%\n({g.loc['Júnior', 'vagas']} vagas)", ha="center", fontsize=14, color=TINTA_2)
        ax.text(sr, -i - 0.30, f"Sênior {sr:.0f}%\n({g.loc['Sênior', 'vagas']} vagas)", ha="center", fontsize=14, color=TINTA_2)
        ax.text(-4, -i, f"{NOME_CARGO[cargo]}\n{pais}", ha="right", va="center", fontsize=15, color=TINTA)
    ax.set_xlim(0, 100)
    ax.set_ylim(-max(len(grupos), 2.5) + 0.3, 0.8)
    ax.axis("off")
    return _salvar(fig, "junior_senior.png")


def tipos_ia(t: pd.DataFrame) -> Path:
    """Pergunta 4: que IA pedem (entre as vagas que pedem IA, todos os cargos)."""
    t = t[t["cargo"] == "Todos"]
    paises = _ordem_paises(t["pais"])
    generico = list(config.TIPOS_IA)[-1]
    ordem = (t[(t["pais"] == paises[0]) & (t["tipo_ia"] != generico)]
             .sort_values("pct_das_que_pedem_ia", ascending=False)["tipo_ia"].tolist()) + [generico]
    fig = _figura("Que IA as vagas pedem?",
                  "Entre as vagas que pedem IA: % que cita cada tipo (uma vaga pode citar vários)",
                  _rodape(paises))
    ax = fig.add_axes([0.40, 0.10, 0.50, 0.72])
    ax.set_facecolor(FUNDO)
    altura = 0.8 / len(paises)
    for i, tipo in enumerate(ordem):
        for j, pais in enumerate(paises):
            v = t[(t["pais"] == pais) & (t["tipo_ia"] == tipo)]["pct_das_que_pedem_ia"].iloc[0]
            y = -i - j * altura
            ax.barh(y, v, height=altura * 0.8, color=COR_PAIS.get(pais, TINTA_2))
            ax.text(v + 1, y, f"{v:.0f}%" + (f"  {pais}" if len(paises) > 1 else ""), va="center",
                    fontsize=13, color=TINTA)
        ax.text(-2, -i - (len(paises) - 1) * altura / 2, tipo.replace(" (", "\n(").replace(", sem", "\nsem"),
                ha="right", va="center", fontsize=14, color=TINTA)
    ax.set_xlim(0, max(100, t["pct_das_que_pedem_ia"].max() + 15))
    ax.set_ylim(-len(ordem) + 0.4, 0.6)
    ax.axis("off")
    return _salvar(fig, "tipos_ia.png")
