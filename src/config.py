"""
Configurações do projeto 3: quantas vagas de dados pedem conhecimento em IA?

Os padrões (regex) são aplicados em texto normalizado: minúsculo e SEM acentos.
Por isso escrevemos "inteligencia" e não "inteligência".
"""

# ---------------------------------------------------------------------------
# Coleta (Indeed Brasil e Indeed EUA, mesmos cargos, mesmo código)
# ---------------------------------------------------------------------------
PAISES = {
    "Brasil": {
        "country_indeed": "Brazil",
        "local": "Brazil",
        "vagas_por_termo": 1000,   # máximo que o Indeed devolve por busca
        "termos": {
            "Analista": ["analista de dados", "data analyst", "analista de BI", "business intelligence",
                         "analista de dados junior", "analista de dados pleno", "analista de dados senior"],
            "Cientista": ["cientista de dados", "data scientist",
                          "cientista de dados junior", "cientista de dados pleno", "cientista de dados senior"],
            "Engenheiro": ["engenheiro de dados", "engenheira de dados", "data engineer",
                           "engenheiro de dados junior", "engenheiro de dados pleno", "engenheiro de dados senior"],
        },
    },
    "EUA": {
        "country_indeed": "USA",
        "local": "United States",
        "vagas_por_termo": 300,    # os EUA têm muito mais vagas; 300 por busca já basta
        "termos": {
            "Analista": ["data analyst", "business intelligence analyst", "junior data analyst", "senior data analyst"],
            "Cientista": ["data scientist", "junior data scientist", "senior data scientist"],
            "Engenheiro": ["data engineer", "junior data engineer", "senior data engineer"],
        },
    },
}
DIAS_ATRAS = 90             # janela de publicação pedida ao Indeed (e usada na análise)
PAUSA_ENTRE_BUSCAS = 20     # segundos

# Coletas antigas que também entram (mesma fonte, mesma ferramenta). Só Brasil.
#   projeto 2: os três cargos  |  projeto 1: só vagas classificadas como Analista
PASTA_RAW_PROJETO2 = "../skills-cargos-dados/data/raw"
PASTA_RAW_PROJETO1 = "../skills-analista-dados/data/raw"

CARGOS = ["Analista", "Cientista", "Engenheiro"]

# ---------------------------------------------------------------------------
# Classificação do cargo pelo TÍTULO (mesmas regras do projeto 2; valem em inglês)
# ---------------------------------------------------------------------------
TITULO_HIBRIDO = {
    "Analytics Engineer": r"analytics engineer|engenheir[oa]\S*(?:\s*\(a\))? de analytics|engenharia de analytics",
    "Machine Learning Engineer": r"(machine learning|\bml\b) engineer|engenheir[oa]\S*(?:\s*\(a\))? (de )?(machine learning|aprendizado de maquina|\bml\b)",
    "MLOps": r"\bmlops\b|\bml ops\b",
    "Arquiteto de Dados": r"arquitet[oa]\S* de dados|data architect|arquitetura de dados",
    "AI Engineer": r"\bai engineer|engenheir[oa]\S*(?:\s*\(a\))? de (ia|inteligencia artificial)\b",
}
TITULO_ENGENHEIRO_NOME = r"engenheir[oa]\S*(?:\s*\(a\))? (de )?dados|\beng\.? (de )?dados|data engineer|big data engineer|engenheir[oa]\S* de big data"
TITULO_CIENTISTA_NOME = r"cientista (de )?dados|data scientist"
TITULO_ENGENHEIRO_AREA = r"engenh?[ae]ria de dados|data engineering"
TITULO_CIENTISTA_AREA = r"ciencias? de dados|data science"
TITULO_ANALISTA_INCLUIR = r"analista|analyst|analytics|analise de dados|estagi|\bbi\b|business intel|inteligencia de negocios"
TITULO_ANALISTA_TEMA = r"dado|data|\bbi\b|business intel|analytics|inteligencia de negocios|power bi"
TITULO_OUTRA_AREA = r"desenvolvedor|developer|dba\b|arquitet|architect|engenheir|engineer|cientista|scientist"

# Senioridade (título)
SENIORIDADE = [
    ("Estágio", r"estagi|\bintern\b|internship"),
    ("Júnior", r"junior|\bjr\b|\bi\b$|\bi\s*[-|(,]|trainee|entry[- ]level|\bassociate\b"),
    ("Pleno", r"pleno|\bpl\b|\bii\b|mid[- ]level"),
    ("Sênior", r"senior|\bsr\b|\biii\b|\biv\b|especialista|specialist|\blead\b|lider|\bstaff\b|principal"),
]
SEM_SENIORIDADE = "Não informado"
MIN_VAGAS_GRUPO = 50        # júnior × sênior só é mostrado se os dois grupos tiverem isso

# Modelo de trabalho (igual ao projeto 2, com termos em inglês)
MODELO_TRABALHO = [
    ("Híbrido", r"hibrid|hybrid"),
    ("Remoto", r"remot|home ?office|anywhere|100% online|trabalho a distancia|work from home"),
    ("Presencial", r"presencial|on-?site|in loco|in[- ]office"),
]

# ---------------------------------------------------------------------------
# IA: o que conta como "a vaga pede conhecimento em IA"
# ---------------------------------------------------------------------------
# Tipos de IA. Uma vaga pode ter mais de um tipo. O último ("IA" sem especificar) só fica
# quando a vaga não cita nenhum dos tipos específicos.
TIPOS_IA = {
    "IA generativa / LLMs": r"ia generativa|ias generativas|generative ai|\bgen ?ai\b|\bllms?\b|large language models?|modelos? de linguagem|\bslms?\b|foundation models?",
    "Ferramentas (ChatGPT, Copilot, Gemini, Claude)": r"chat ?gpt|\bopenai\b|\bgpt[- ]?\d|\bgpts?\b|\bcopilot\b|\bgemini\b|\bclaude\b|\bperplexity\b|\bnotebooklm\b",
    "Prompt engineering": r"prompt (engineering|design)|engenharia de prompts?|\bprompting\b|\bprompts\b|criacao de prompts?",
    "Agentes de IA": r"agentes? (de |com )?(ia|ai|inteligencia artificial)\b|\bai agents?\b|\bagentic\b|agentes inteligentes|agentes autonomos|multi-?agent",
    "RAG / LangChain / vetores": r"\brag\b|retrieval[- ]augmented|\blangchain\b|\blanggraph\b|\bllamaindex\b|vector (database|db|store|search)|bancos? (de dados )?vetoria",
    "Só \"IA\", sem especificar": r"inteligencia artificial|artificial intelligence|\bias?\b|\bai\b|\bai/ml\b|\bia/ml\b",
}
# Machine Learning fica FORA da conta de "IA" (é contado à parte, para referência)
ML = r"machine learning|aprendizado de maquina|\bml\b|modelos? preditivos?|predictive model"

# Seções da descrição, reconhecidas pelo título da seção (ordem = prioridade)
SECAO = [
    ("Diferencial", r"diferencia|desejave|nice to have|preferred|bonus|\bplus\b|seria legal|ganha pontos|would be great|ideally"),
    ("Requisito", r"requisit|qualifica|o que (buscamos|esperamos|procuramos)|perfil|conhecimento|competencia|experiencia|"
                  r"o que voce (precisa|deve|traz)|para (se candidatar|essa vaga)|hard skills|habilidade|stack|tecnologias|ferramentas|"
                  r"obrigator|indispensav|necessari|formacao|requirements|qualifications|must have|what you (bring|need|have)|"
                  r"who you are|about you|sobre voce|skills|what we.?re looking for|you have|you bring|you.?ll need|"
                  r"what you.?(ll)? (bring|need|have)|bring to|you.?ll bring"),
    ("Atividade", r"responsabilidad|atribuic|atividade|o que voce (vai|ira) fazer|dia a dia|desafio|missao do cargo|objetivo do cargo|"
                  r"sua (missao|atuacao|rotina)|como voce vai|o que (fara|vai fazer)|voce (vai|ira)|"
                  r"responsibilities|what you.?ll do|the role|your role|duties|day to day|in this role|you will"),
    ("Geral", r"sobre (a|o) (vaga|oportunidade|posicao|funcao|cargo|time|area|projeto)|descricao (da vaga|do cargo|da posicao)|"
              r"job (description|summary|overview)|the opportunity|overview|position summary|summary"),
    ("Empresa/benefícios", r"sobre (a |o |nos|n[oó]s|a empresa|a companhia)|quem somos|beneficio|oferecemos|informacoes adicionais|"
                           r"valores|cultura|diversidade|missao|about (us|the company|the team|[a-z]+)|benefits|perks|compensation|"
                           r"salary|pay range|equal opportunity|eeo|etapas|processo seletivo|remuneracao|local|jornada|horario|"
                           r"modelo de (trabalho|contratacao)|regime|what we offer|why join"),
]

# Fora de seções de requisito/diferencial/atividade, a frase só conta se tiver uma
# palavra de exigência e NÃO tiver cara de apresentação da empresa.
PALAVRAS_EXIGENCIA = (r"conhecimento|experiencia|familiaridade|dominio|vivencia|habilidade|saber (usar|utilizar)|uso d[aeo]|"
                      r"utilizar|utilizacao|aplicar|aplicacao|automatiz|nocoes|interesse (em|por)|usuario de|"
                      r"requisit|diferencia|desejavel|desejaveis|capacidade de|"
                      r"experience|knowledge|familiar|proficien|understanding of|ability to|comfortable|skilled|"
                      r"expertise|required|must|preferred|nice to have|bonus|plus\b|leverag|using|\buse\b|\bapply|exposure")
PALAVRAS_DIFERENCIAL = (r"diferencia|desejavel|desejaveis|nice to have|preferred|bonus|\bplus\b|"
                        r"sera um|e um (diferencial|plus)|ideally|is a plus|a plus|desired|not required|optional")
PALAVRAS_EMPRESA = (r"\bsomos\b|nossa empresa|a empresa|nossos clientes|fundad|lider em|referencia em|nossa missao|"
                    r"transformacao digital|ajudamos|oferecemos|nosso time|nossa plataforma|nossas solucoes|"
                    r"\bwe are\b|\bwe.?re\b|our (company|mission|platform|clients|customers|products?)|founded|"
                    r"\bwe (build|help|use|believe)\b|is a leading|leader in")

# Em texto sem seção, frases que começam com verbo no infinitivo ("Automatizar rotinas com IA",
# "Aplicar IA generativa...") costumam ser tarefas ou requisitos da vaga: também contam.
VERBO_INICIO = r"^[+\-•·]?\s*[a-z]{3,}(ar|er|ir|or)\b"
# Sem seção, a apresentação da empresa costuma usar "nós": essas frases não contam
PALAVRAS_EMPRESA_GERAL = (PALAVRAS_EMPRESA + r"|\bnoss[oa]s?\b|\b(unimos|usamos|criamos|desenvolvemos|entregamos|"
                          r"atuamos|acreditamos|buscamos)\b|anos de (estrada|mercado|historia)|\bour\b|\bwe\b")

# Frases com IA que NUNCA contam, em qualquer seção:
#  - processo seletivo: "o uso de IA na entrevista é proibido", "usamos IA para triar currículos"
#  - curso/formação: "graduação em Ciência da Computação, IA ou áreas afins"
NAO_CONTA = (r"interview|entrevista|hiring (process|decision)|processo seletivo|recrut|recruit|candidate.? (use|usage)|"
             r"ai usage policy|resumes?|curriculo|application process|candidatura|identity verification|"
             r"(degree|graduacao|graduado|bacharel|formacao|formado|mestrado|master|ph\.?d|pos.?graduacao|"
             r"bachelor|curso)[^.;]{0,90}(inteligencia artificial|artificial intelligence|\bai\b|\bia\b)")
# Frases em que a IA é só o DESTINO dos dados ("pipelines que suportam iniciativas de IA",
# "preparar bases para modelos de IA") não pedem conhecimento em IA, a menos que a frase também
# tenha uma palavra de conhecimento/uso.
DADOS_PARA_IA = (r"(support|supporting|enable|enabling|power|powering|fuel|feed|ready for|\bfor\b|"
                 r"suportar|suportam|suporte a|apoiar|apoiando|alimentar|habilitar|viabilizar|\bpara\b)"
                 r"[^.;]{0,80}(\bai\b|\bia\b|inteligencia artificial|artificial intelligence|\bllms?\b|genai)")
PALAVRAS_CONHECIMENTO = (r"conhecimento|experiencia|familiaridade|dominio|vivencia|utilizar|\buso d|usar\b|aplicar|"
                         r"experience|knowledge|familiar|understanding|proficien|\buse\b|using|leverag|\bapply|expertise|"
                         r"desenvolver (solucoes|agentes|modelos|aplicacoes)|build(ing)? (ai|genai|llm|agent)")

# Gráficos
AUTOR = "Gabriel Leonardelli"
