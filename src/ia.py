"""
Detecta se uma vaga PEDE conhecimento em IA ao candidato.

Ideia: uma menção a "IA" na apresentação da empresa ("somos uma empresa focada em IA")
não é um pedido. Por isso a descrição é lida por SEÇÕES:

    Requisitos / qualificações   -> conta (Requisito, ou Diferencial se a frase disser "diferencial")
    Diferenciais / desejável     -> conta (Diferencial)
    Responsabilidades / dia a dia -> conta (Tarefa: a vaga espera que você use IA no trabalho)
    Texto sem seção / "sobre a vaga" -> só conta se a frase tiver palavra de exigência
                                        ("conhecimento", "experiência", "utilizar"...) e não
                                        tiver cara de apresentação da empresa
    Sobre a empresa / benefícios -> não conta

Machine Learning NÃO entra na conta de IA (é marcado à parte, só para referência).
"""

import re
import unicodedata

from src import config

_TIPOS = {nome: re.compile(p) for nome, p in config.TIPOS_IA.items()}
_GENERICO = list(config.TIPOS_IA)[-1]
_ML = re.compile(config.ML)
_SECOES = [(nome, re.compile(p)) for nome, p in config.SECAO]
_EXIG = re.compile(config.PALAVRAS_EXIGENCIA)
_DIF = re.compile(config.PALAVRAS_DIFERENCIAL)
_EMP = re.compile(config.PALAVRAS_EMPRESA)
_EMP_GERAL = re.compile(config.PALAVRAS_EMPRESA_GERAL)
_VERBO = re.compile(config.VERBO_INICIO)
_NAO_CONTA = re.compile(config.NAO_CONTA)
_DADOS_PARA_IA = re.compile(config.DADOS_PARA_IA)
_CONHEC = re.compile(config.PALAVRAS_CONHECIMENTO)


def normalizar(texto) -> str:
    """Minúsculo e sem acento, mas mantendo as quebras de linha e a marcação (para achar seções)."""
    if not isinstance(texto, str):
        return ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c)).lower()
    texto = texto.replace("\\", "")
    texto = re.sub(r"\bi\.a\.?(?=\W)", "ia", texto)                       # "I.A." -> "ia"
    texto = re.sub(r"\b(e|indica|vem|bora|olha) ai\b", " ", texto)              # "E aí, curtiu?" não é IA
    texto = re.sub(r"https?://\S+|www\.\S+|\b[\w-]+\.(ai|io|com|br)\b\S*", " ", texto)  # links e domínios (triggo.ai)
    return texto


def tipos_na_frase(frase: str) -> list[str]:
    achados = [nome for nome, rx in _TIPOS.items() if rx.search(frase)]
    if len(achados) > 1 and _GENERICO in achados:
        achados.remove(_GENERICO)
    return achados


def classificar_secao(titulo: str) -> str:
    titulo = re.sub(r"[^a-z0-9 /&+.,?()-]", " ", titulo).strip()
    for nome, rx in _SECOES:
        if rx.search(titulo):
            return nome
    return "Geral"


_BULLET = re.compile(r"^\s*([*\-•·▪●✓✔➢➤>]|\d+[.)])\s+(?!\*)")
_HEADER_NEGRITO = re.compile(r"^\s*(?:#+\s*)?\*\*\s*([^*]{2,90}?)\s*\*\*\s*:?\s*(.*)$")
_HEADER_HASH = re.compile(r"^\s*#+\s*(.{2,90})$")


def ler_linha(linha: str) -> tuple[str | None, str]:
    """Devolve (titulo_de_secao ou None, conteúdo da linha)."""
    if _BULLET.match(linha):
        return None, linha
    m = _HEADER_NEGRITO.match(linha)
    if m:
        titulo, resto = m.group(1), m.group(2)
        if resto and not titulo.rstrip().endswith(":") and len(resto) > 3 and not linha.split("**")[2].lstrip().startswith(":"):
            return None, linha            # negrito no meio da frase, não é título
        return titulo, resto
    m = _HEADER_HASH.match(linha)
    if m:
        return m.group(1), ""
    limpo = re.sub(r"[*_#`]", "", linha).strip()
    if limpo.endswith(":") and len(limpo) <= 60 and len(limpo.split()) <= 8:
        return limpo, ""
    return None, linha


def frases(texto: str) -> list[str]:
    texto = re.sub(r"[*_#`]", " ", texto)
    partes = re.split(r"(?<=[.;!?])\s+(?=[a-z0-9(])", texto)
    return [re.sub(r"\s+", " ", p).strip() for p in partes if len(p.strip()) > 2]


def detectar(titulo, descricao) -> dict:
    """Resultado por vaga: pede_ia, nivel (Requisito / Tarefa / Só diferencial), tipos, onde, trecho..."""
    ocorrencias = []   # (secao, nivel, tipos, frase)
    menciona = False

    t = normalizar(titulo)
    tipos_t = tipos_na_frase(t)
    if tipos_t:
        menciona = True
        ocorrencias.append(("Título", "Requisito", tipos_t, t))

    secao = "Geral"
    for linha in normalizar(descricao).split("\n"):
        if not linha.strip():
            continue
        titulo_secao, conteudo = ler_linha(linha)
        if titulo_secao is not None:
            secao = classificar_secao(titulo_secao)
            if not conteudo:
                continue
        for f in frases(conteudo):
            tipos = tipos_na_frase(f)
            if not tipos:
                continue
            menciona = True
            if _NAO_CONTA.search(f):
                continue
            if _DADOS_PARA_IA.search(f) and not _CONHEC.search(f):
                continue
            dif = bool(_DIF.search(f))
            if secao == "Requisito":
                ocorrencias.append((secao, "Diferencial" if dif else "Requisito", tipos, f))
            elif secao == "Diferencial":
                ocorrencias.append((secao, "Diferencial", tipos, f))
            elif secao == "Atividade":
                if not _EMP.search(f):
                    ocorrencias.append((secao, "Diferencial" if dif else "Tarefa", tipos, f))
            elif secao == "Geral":
                if (_EXIG.search(f) or _VERBO.search(f)) and not _EMP_GERAL.search(f):
                    ocorrencias.append((secao, "Diferencial" if dif else "Requisito", tipos, f))
            # Empresa/benefícios: não conta

    texto_todo = normalizar(f"{titulo}\n{descricao}")
    tipos_vaga = sorted({tp for _, _, tps, _ in ocorrencias for tp in tps})
    if len(tipos_vaga) > 1 and _GENERICO in tipos_vaga:   # "IA genérico" só fica se a vaga não citar nada específico
        tipos_vaga.remove(_GENERICO)
    niveis = {n for _, n, _, _ in ocorrencias}
    return {
        "menciona_ia": menciona,
        "pede_ia": bool(ocorrencias),
        # Requisito > Tarefa do dia a dia > Só diferencial
        "nivel_ia": ("Requisito" if "Requisito" in niveis else "Tarefa" if "Tarefa" in niveis
                     else "Só diferencial" if niveis else ""),
        "tipos_ia": "|".join(tipos_vaga),
        "secoes_ia": "|".join(sorted({s for s, _, _, _ in ocorrencias})),
        "trecho_ia": ocorrencias[0][3][:300] if ocorrencias else "",
        "n_trechos_ia": len(ocorrencias),
        "cita_ml": bool(_ML.search(texto_todo)),
    }
