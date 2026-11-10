# Gerador de Caça-Palavras em Python

Gera caça-palavras no terminal. Usa só a biblioteca padrão; o `reportlab` é necessário apenas para exportar em PDF.

Arquivos: `caca_palavras.py` (programa principal) e `exportar_pdf.py` (geração do PDF) — mantenha os dois na mesma pasta.

## Como rodar

```bash
python caca_palavras.py
```

## Modos

1. **Aleatório**: escolha um tema (Animais, Frutas, Programação, Países, Esportes ou todos misturados) e a quantidade de palavras.
2. **Personalizado**: digite suas palavras (separadas por vírgula ou uma por linha). Acentos e espaços são removidos automaticamente (`Maçã` → `MACA`).

## Níveis de dificuldade

| Nível   | Direções                          | Grade sugerida | Letras de preenchimento |
|---------|-----------------------------------|----------------|--------------------------|
| Fácil   | → ↓                               | 10x10          | aleatórias               |
| Médio   | → ↓ ↘ ↗                           | 12x12          | aleatórias               |
| Difícil | as 8 direções, inclusive invertidas | 15x15        | 75% tiradas das próprias palavras (pistas falsas) |

O tamanho sugerido pode ser alterado (de 6x6 a 30x30).

## Saída

- **Gabarito no terminal**: mostra só as letras das palavras e a posição/direção de cada uma.
- **PDF** (requer `pip install reportlab`): página 1 com o jogo, campos de nome/data e lista com caixinhas;
  página 2 com o gabarito, com cada palavra destacada em uma cor.
- **TXT**: jogo + gabarito em texto simples.

## Usando como módulo

```python
from caca_palavras import CacaPalavras, NIVEIS
from exportar_pdf import exportar_pdf

nivel = NIVEIS["3"]  # Difícil
jogo = CacaPalavras(["PYTHON", "JAVA", "DADOS"], tamanho=10,
                    direcoes=nivel["direcoes"], iscas=nivel["iscas"],
                    semente=42).gerar()
print(jogo.texto_grade())
jogo.exportar("meu_jogo.txt")
exportar_pdf(jogo, "meu_jogo.pdf", "MEU CAÇA-PALAVRAS", nivel["nome"])
```

## Para adicionar temas

Inclua uma nova chave no dicionário `BANCO_PALAVRAS` no início do arquivo.
