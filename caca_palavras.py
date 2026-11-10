"""
Gerador de Caça-Palavras
------------------------
Duas formas de gerar:
  1) Aleatório: sorteia palavras de um banco por tema.
  2) Personalizado: o usuário digita as palavras.

Recursos:
  - Palavras em 8 direções (horizontal, vertical e diagonais, normais e invertidas)
  - Níveis de dificuldade (fácil, médio, difícil)
  - Remoção de acentos (ÇÃO -> CAO) para caber na grade
  - Exibição do gabarito (palavras destacadas)
  - Exportação para arquivo .txt
"""

import random
import string
import unicodedata
from datetime import datetime

# ---------------------------------------------------------------------------
# Banco de palavras para o modo aleatório
# ---------------------------------------------------------------------------
BANCO_PALAVRAS = {
    "Animais": [
        "GATO", "CACHORRO", "ELEFANTE", "GIRAFA", "LEAO", "TIGRE", "ZEBRA",
        "MACACO", "COBRA", "JACARE", "TUCANO", "ARARA", "BALEIA", "GOLFINHO",
        "TARTARUGA", "CAVALO", "CORUJA", "PINGUIM", "RAPOSA", "LOBO",
    ],
    "Frutas": [
        "BANANA", "MACA", "UVA", "LARANJA", "MANGA", "ABACAXI", "MELANCIA",
        "MORANGO", "KIWI", "PERA", "GOIABA", "CAJU", "ACEROLA", "MARACUJA",
        "LIMAO", "MAMAO", "JACA", "CEREJA", "PITANGA", "CUPUACU",
    ],
    "Programação": [
        "PYTHON", "JAVA", "VARIAVEL", "FUNCAO", "CLASSE", "OBJETO", "LISTA",
        "LOOP", "STRING", "INTEIRO", "BOOLEANO", "COMPILADOR", "ALGORITMO",
        "RECURSAO", "VETOR", "MATRIZ", "PONTEIRO", "DEBUG", "GITHUB", "API",
    ],
    "Países": [
        "BRASIL", "ARGENTINA", "CHILE", "PERU", "MEXICO", "CANADA", "JAPAO",
        "CHINA", "INDIA", "FRANCA", "ITALIA", "ESPANHA", "PORTUGAL",
        "ALEMANHA", "EGITO", "ANGOLA", "GRECIA", "RUSSIA", "COLOMBIA", "CUBA",
    ],
    "Esportes": [
        "FUTEBOL", "VOLEI", "BASQUETE", "TENIS", "NATACAO", "SURFE", "JUDO",
        "BOXE", "CICLISMO", "XADREZ", "HANDEBOL", "ATLETISMO", "GINASTICA",
        "SKATE", "REMO", "ESGRIMA", "GOLFE", "RUGBY", "KARATE", "CORRIDA",
    ],
}

# ---------------------------------------------------------------------------
# Direções possíveis: (delta_linha, delta_coluna)
# ---------------------------------------------------------------------------
DIRECOES_FACIL = [(0, 1), (1, 0)]                       # → ↓
DIRECOES_MEDIO = DIRECOES_FACIL + [(1, 1), (-1, 1)]     # + diagonais ↘ ↗
DIRECOES_DIFICIL = DIRECOES_MEDIO + [                   # + invertidas
    (0, -1), (-1, 0), (-1, -1), (1, -1)
]

NIVEIS = {
    "1": {
        "nome": "Fácil",
        "descricao": "só → e ↓, grade menor, letras de preenchimento aleatórias",
        "direcoes": DIRECOES_FACIL,
        "tamanho": 10,
        "iscas": False,
    },
    "2": {
        "nome": "Médio",
        "descricao": "inclui diagonais ↘ ↗, grade média",
        "direcoes": DIRECOES_MEDIO,
        "tamanho": 12,
        "iscas": False,
    },
    "3": {
        "nome": "Difícil",
        "descricao": "8 direções (inclusive invertidas), grade maior e "
                     "preenchimento com as mesmas letras das palavras",
        "direcoes": DIRECOES_DIFICIL,
        "tamanho": 15,
        "iscas": True,
    },
}


def escolher_nivel():
    print("\nNível de dificuldade:")
    for chave, nivel in NIVEIS.items():
        print(f"  {chave}. {nivel['nome']:<8} — {nivel['descricao']}")
    while True:
        opcao = input("Escolha o nível [padrão 2]: ").strip() or "2"
        if opcao in NIVEIS:
            return NIVEIS[opcao]
        print("  ⚠ Opção inválida.")


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def normalizar(palavra: str) -> str:
    """Remove acentos, espaços e caracteres não alfabéticos; deixa maiúsculo."""
    sem_acento = unicodedata.normalize("NFD", palavra)
    sem_acento = "".join(c for c in sem_acento if unicodedata.category(c) != "Mn")
    return "".join(c for c in sem_acento.upper() if c in string.ascii_uppercase)


def ler_inteiro(mensagem: str, minimo: int, maximo: int, padrao: int) -> int:
    """Lê um inteiro dentro do intervalo; Enter usa o valor padrão."""
    while True:
        entrada = input(f"{mensagem} [{minimo}-{maximo}, padrão {padrao}]: ").strip()
        if entrada == "":
            return padrao
        if entrada.isdigit() and minimo <= int(entrada) <= maximo:
            return int(entrada)
        print(f"  ⚠ Digite um número entre {minimo} e {maximo}.")


# ---------------------------------------------------------------------------
# Classe principal
# ---------------------------------------------------------------------------
class CacaPalavras:
    VAZIO = "."

    def __init__(self, palavras, tamanho=12, direcoes=DIRECOES_DIFICIL,
                 iscas=False, max_tentativas=500, semente=None):
        self.tamanho = tamanho
        self.direcoes = direcoes
        self.iscas = iscas  # preencher com letras das próprias palavras
        self.max_tentativas = max_tentativas
        self.rng = random.Random(semente)

        self.grade = [[self.VAZIO] * tamanho for _ in range(tamanho)]
        self.posicoes = {}          # palavra -> lista de (linha, coluna)
        self.nao_colocadas = []     # palavras que não couberam

        # Palavras maiores primeiro: mais fáceis de encaixar com a grade vazia
        unicas = list(dict.fromkeys(palavras))
        self.palavras = sorted(unicas, key=len, reverse=True)

    # -- Montagem ----------------------------------------------------------
    def _cabe(self, palavra, linha, coluna, dl, dc):
        """Verifica se a palavra cabe a partir de (linha, coluna) na direção."""
        for i, letra in enumerate(palavra):
            l, c = linha + dl * i, coluna + dc * i
            if not (0 <= l < self.tamanho and 0 <= c < self.tamanho):
                return False
            if self.grade[l][c] not in (self.VAZIO, letra):
                return False
        return True

    def _colocar(self, palavra):
        """Tenta posicionar uma palavra; retorna True se conseguiu."""
        for _ in range(self.max_tentativas):
            dl, dc = self.rng.choice(self.direcoes)
            linha = self.rng.randrange(self.tamanho)
            coluna = self.rng.randrange(self.tamanho)
            if self._cabe(palavra, linha, coluna, dl, dc):
                coords = []
                for i, letra in enumerate(palavra):
                    l, c = linha + dl * i, coluna + dc * i
                    self.grade[l][c] = letra
                    coords.append((l, c))
                self.posicoes[palavra] = coords
                return True
        return False

    def gerar(self):
        """Posiciona todas as palavras e preenche o resto com letras aleatórias."""
        for palavra in self.palavras:
            if len(palavra) > self.tamanho or not self._colocar(palavra):
                self.nao_colocadas.append(palavra)

        # No modo "iscas", 75% das letras de preenchimento vêm das próprias
        # palavras, criando falsos inícios e deixando a busca mais difícil.
        letras_palavras = "".join(self.posicoes) or string.ascii_uppercase
        for l in range(self.tamanho):
            for c in range(self.tamanho):
                if self.grade[l][c] == self.VAZIO:
                    if self.iscas and self.rng.random() < 0.75:
                        self.grade[l][c] = self.rng.choice(letras_palavras)
                    else:
                        self.grade[l][c] = self.rng.choice(string.ascii_uppercase)
        return self

    # -- Saída ---------------------------------------------------------------
    def texto_grade(self, gabarito=False):
        """Retorna a grade como texto. No gabarito, letras de fora viram '·'."""
        marcadas = {pos for coords in self.posicoes.values() for pos in coords}
        cabecalho = "    " + " ".join(f"{c + 1:>2}"[-2:] for c in range(self.tamanho))
        linhas = [cabecalho]
        for l in range(self.tamanho):
            celulas = []
            for c in range(self.tamanho):
                if gabarito and (l, c) not in marcadas:
                    celulas.append(" ·")
                else:
                    celulas.append(f" {self.grade[l][c]}")
            linhas.append(f"{l + 1:>2} " + " ".join(celulas))
        return "\n".join(linhas)

    def texto_lista(self, colunas=3):
        """Lista das palavras escondidas em ordem alfabética, em colunas."""
        encontradas = sorted(self.posicoes)
        largura = max((len(p) for p in encontradas), default=0) + 4
        linhas = []
        for i in range(0, len(encontradas), colunas):
            grupo = encontradas[i:i + colunas]
            linhas.append("".join(f"□ {p:<{largura}}" for p in grupo).rstrip())
        return "\n".join(linhas)

    def texto_solucoes(self):
        """Descreve onde cada palavra começa e em que direção segue."""
        nomes = {
            (0, 1): "→", (1, 0): "↓", (1, 1): "↘", (-1, 1): "↗",
            (0, -1): "←", (-1, 0): "↑", (-1, -1): "↖", (1, -1): "↙",
        }
        linhas = []
        for palavra in sorted(self.posicoes):
            coords = self.posicoes[palavra]
            (l0, c0) = coords[0]
            if len(coords) > 1:
                dl, dc = coords[1][0] - l0, coords[1][1] - c0
            else:
                dl, dc = 0, 1
            linhas.append(f"  {palavra:<15} linha {l0 + 1:>2}, coluna {c0 + 1:>2}  {nomes[(dl, dc)]}")
        return "\n".join(linhas)

    def exportar(self, caminho, titulo="CAÇA-PALAVRAS"):
        """Salva o jogo e o gabarito em um arquivo .txt."""
        separador = "=" * (self.tamanho * 3 + 4)
        conteudo = [
            titulo, separador, self.texto_grade(), "",
            "PALAVRAS PARA ENCONTRAR:", self.texto_lista(), "", "",
            "GABARITO", separador, self.texto_grade(gabarito=True), "",
            self.texto_solucoes(), "",
        ]
        with open(caminho, "w", encoding="utf-8") as arq:
            arq.write("\n".join(conteudo))
        return caminho


# ---------------------------------------------------------------------------
# Fluxos do menu
# ---------------------------------------------------------------------------
def escolher_tema():
    temas = list(BANCO_PALAVRAS)
    print("\nTemas disponíveis:")
    for i, tema in enumerate(temas, 1):
        print(f"  {i}. {tema}")
    print(f"  {len(temas) + 1}. Misturar todos")
    opcao = ler_inteiro("Escolha o tema", 1, len(temas) + 1, len(temas) + 1)
    if opcao == len(temas) + 1:
        todas = [p for lista in BANCO_PALAVRAS.values() for p in lista]
        return "Variado", todas
    tema = temas[opcao - 1]
    return tema, BANCO_PALAVRAS[tema]


def modo_aleatorio(tamanho):
    tema, banco = escolher_tema()
    cabem = [p for p in banco if len(p) <= tamanho]
    if not cabem:
        print("Nenhuma palavra do tema cabe nesta grade.")
        return None, None
    qtd = ler_inteiro("Quantas palavras", 1, min(len(cabem), 25), min(10, len(cabem)))
    return f"CAÇA-PALAVRAS — {tema.upper()}", random.sample(cabem, qtd)


def modo_personalizado(tamanho):
    print("\nDigite as palavras separadas por vírgula ou uma por linha.")
    print("Deixe a linha em branco para terminar.")
    palavras = []
    while True:
        linha = input("> ").strip()
        if not linha:
            break
        for bruto in linha.split(","):
            palavra = normalizar(bruto)
            if len(palavra) < 2:
                if bruto.strip():
                    print(f"  ⚠ '{bruto.strip()}' ignorada (precisa ter ao menos 2 letras).")
                continue
            if len(palavra) > tamanho:
                print(f"  ⚠ '{palavra}' ignorada (maior que a grade de {tamanho}).")
                continue
            palavras.append(palavra)
    if not palavras:
        print("Nenhuma palavra válida informada.")
        return None, None
    titulo = input("Título do caça-palavras (Enter para padrão): ").strip()
    return (titulo.upper() or "CAÇA-PALAVRAS"), palavras


def jogar():
    print("=" * 44)
    print("        GERADOR DE CAÇA-PALAVRAS")
    print("=" * 44)
    print("1. Gerar aleatoriamente (por tema)")
    print("2. Informar minhas próprias palavras")
    print("0. Sair")

    modo = input("Opção: ").strip()
    if modo == "0":
        return False
    if modo not in ("1", "2"):
        print("Opção inválida.\n")
        return True

    nivel = escolher_nivel()
    nome_nivel = nivel["nome"]
    tamanho = ler_inteiro("Tamanho da grade", 6, 30, nivel["tamanho"])

    if modo == "1":
        titulo, palavras = modo_aleatorio(tamanho)
    else:
        titulo, palavras = modo_personalizado(tamanho)
    if not palavras:
        return True

    jogo = CacaPalavras(palavras, tamanho, nivel["direcoes"],
                        iscas=nivel["iscas"]).gerar()

    print(f"\n{titulo}  ({nome_nivel}, {tamanho}x{tamanho})\n")
    print(jogo.texto_grade())
    print("\nPALAVRAS:")
    print(jogo.texto_lista())

    if jogo.nao_colocadas:
        print("\n⚠ Não couberam na grade:", ", ".join(jogo.nao_colocadas))
        print("  Dica: aumente o tamanho da grade ou o nível de dificuldade.")

    if input("\nMostrar gabarito? (s/N): ").strip().lower() == "s":
        print("\n" + jogo.texto_grade(gabarito=True))
        print("\n" + jogo.texto_solucoes())

    print("\nSalvar: 1. PDF  2. TXT  3. Ambos  0. Não salvar")
    formato = input("Opção [padrão 0]: ").strip() or "0"
    base = f"caca_palavras_{datetime.now():%Y%m%d_%H%M%S}"
    if formato in ("2", "3"):
        print("Salvo em:", jogo.exportar(base + ".txt", titulo))
    if formato in ("1", "3"):
        try:
            from exportar_pdf import exportar_pdf
        except ImportError:
            print("⚠ Para gerar PDF instale o reportlab: pip install reportlab")
        else:
            print("Salvo em:", exportar_pdf(jogo, base + ".pdf", titulo, nome_nivel))

    print()
    return input("Gerar outro? (s/N): ").strip().lower() == "s"


def main():
    try:
        while jogar():
            print()
    except (KeyboardInterrupt, EOFError):
        pass
    print("\nAté a próxima!")


if __name__ == "__main__":
    main()
