"""
Exportação do caça-palavras para PDF (requer: pip install reportlab).

Página 1: o jogo (grade + lista de palavras com caixinhas para marcar).
Página 2: o gabarito (palavras destacadas na grade + posição de cada uma).
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

LARGURA, ALTURA = A4
MARGEM = 50

# Cores dos destaques no gabarito (uma por palavra, em ciclo)
CORES_DESTAQUE = [
    "#F4A261", "#2A9D8F", "#E76F51", "#8AB17D", "#E9C46A",
    "#6D9DC5", "#C77DFF", "#F28482", "#84A59D", "#B5838D",
]

NOMES_DIRECAO = {
    (0, 1): "para a direita", (1, 0): "para baixo",
    (1, 1): "diagonal descendo à direita", (-1, 1): "diagonal subindo à direita",
    (0, -1): "para a esquerda", (-1, 0): "para cima",
    (-1, -1): "diagonal subindo à esquerda", (1, -1): "diagonal descendo à esquerda",
}


def _cabecalho(pdf, titulo, subtitulo):
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawCentredString(LARGURA / 2, ALTURA - MARGEM - 10, titulo)
    pdf.setFont("Helvetica", 10)
    pdf.setFillColor(colors.grey)
    pdf.drawCentredString(LARGURA / 2, ALTURA - MARGEM - 28, subtitulo)
    pdf.setFillColor(colors.black)
    return ALTURA - MARGEM - 50  # y onde o conteúdo começa


def _desenhar_grade(pdf, jogo, topo, celula, apagar_fora=False):
    """Desenha a grade com o canto superior esquerdo em (x0, topo)."""
    n = jogo.tamanho
    lado = n * celula
    x0 = (LARGURA - lado) / 2
    marcadas = {pos for coords in jogo.posicoes.values() for pos in coords}

    # Moldura
    pdf.setStrokeColor(colors.HexColor("#333333"))
    pdf.setLineWidth(1.5)
    pdf.roundRect(x0 - 6, topo - lado - 6, lado + 12, lado + 12, 8)

    # Letras
    pdf.setFont("Helvetica-Bold", celula * 0.55)
    for l in range(n):
        for c in range(n):
            if apagar_fora and (l, c) not in marcadas:
                pdf.setFillColor(colors.HexColor("#C8C8C8"))
            else:
                pdf.setFillColor(colors.black)
            cx = x0 + c * celula + celula / 2
            cy = topo - l * celula - celula / 2 - celula * 0.19
            pdf.drawCentredString(cx, cy, jogo.grade[l][c])
    pdf.setFillColor(colors.black)
    return x0, topo - lado - 6  # x inicial e base da grade


def _destacar_palavras(pdf, jogo, x0, topo, celula):
    """Desenha 'cápsulas' coloridas sobre cada palavra (gabarito)."""
    pdf.saveState()
    pdf.setLineCap(1)  # pontas arredondadas
    pdf.setLineWidth(celula * 0.78)
    pdf.setStrokeAlpha(0.45)
    for i, palavra in enumerate(sorted(jogo.posicoes)):
        (l1, c1), (l2, c2) = jogo.posicoes[palavra][0], jogo.posicoes[palavra][-1]
        pdf.setStrokeColor(colors.HexColor(CORES_DESTAQUE[i % len(CORES_DESTAQUE)]))
        pdf.line(x0 + c1 * celula + celula / 2, topo - l1 * celula - celula / 2,
                 x0 + c2 * celula + celula / 2, topo - l2 * celula - celula / 2)
    pdf.restoreState()


def _lista_palavras(pdf, palavras, y, colunas=3, caixinha=True):
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(MARGEM, y, "Palavras para encontrar:")
    y -= 22
    largura_col = (LARGURA - 2 * MARGEM) / colunas
    pdf.setFont("Helvetica", 11)
    for i, palavra in enumerate(palavras):
        col, lin = i % colunas, i // colunas
        x = MARGEM + col * largura_col
        yy = y - lin * 18
        if caixinha:
            pdf.rect(x, yy - 1, 9, 9)
            x += 15
        pdf.drawString(x, yy, palavra)


def exportar_pdf(jogo, caminho, titulo="CAÇA-PALAVRAS", nivel=""):
    """Gera o PDF com o jogo e o gabarito. Retorna o caminho do arquivo."""
    pdf = canvas.Canvas(caminho, pagesize=A4)
    pdf.setTitle(titulo)

    n = jogo.tamanho
    celula = min((LARGURA - 2 * MARGEM) / n, 34)
    palavras = sorted(jogo.posicoes)
    info = f"Nível {nivel}  •  Grade {n}x{n}  •  {len(palavras)} palavras".strip()
    if not nivel:
        info = info.replace("Nível   •  ", "")

    # ---------------- Página 1: jogo ----------------
    topo = _cabecalho(pdf, titulo, info)
    pdf.setFont("Helvetica", 10)
    pdf.drawString(MARGEM, topo, "Nome: " + "_" * 45)
    pdf.drawRightString(LARGURA - MARGEM, topo, "Data: ___/___/______")
    _, base = _desenhar_grade(pdf, jogo, topo - 25, celula)
    _lista_palavras(pdf, palavras, base - 30)
    pdf.showPage()

    # ---------------- Página 2: gabarito ----------------
    topo = _cabecalho(pdf, "GABARITO", titulo) - 10
    lado = n * celula
    x0 = (LARGURA - lado) / 2
    _destacar_palavras(pdf, jogo, x0, topo, celula)
    _, base = _desenhar_grade(pdf, jogo, topo, celula, apagar_fora=True)

    y = base - 30
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(MARGEM, y, "Posição de cada palavra (linha, coluna):")
    y -= 20
    pdf.setFont("Helvetica", 10)
    for i, palavra in enumerate(palavras):
        coords = jogo.posicoes[palavra]
        (l0, c0) = coords[0]
        direcao = (coords[1][0] - l0, coords[1][1] - c0) if len(coords) > 1 else (0, 1)
        cor = colors.HexColor(CORES_DESTAQUE[i % len(CORES_DESTAQUE)])
        coluna = i % 2
        linha = i // 2
        x = MARGEM + coluna * (LARGURA - 2 * MARGEM) / 2
        yy = y - linha * 16
        if yy < MARGEM:  # evita estourar a página em listas muito longas
            break
        pdf.setFillColor(cor)
        pdf.circle(x + 4, yy + 3.5, 4, stroke=0, fill=1)
        pdf.setFillColor(colors.black)
        pdf.drawString(x + 14, yy, f"{palavra} — ({l0 + 1}, {c0 + 1}), {NOMES_DIRECAO[direcao]}")

    pdf.showPage()
    pdf.save()
    return caminho
