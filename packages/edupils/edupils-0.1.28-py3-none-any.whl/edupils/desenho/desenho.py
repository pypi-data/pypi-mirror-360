import asyncio
from js import document
import math
from .. import constantes


def desenhar_retangulo(x, y, largura, altura, canvas_id, cor_preenchimento):
    cor_preenchimento_traduzida = constantes.traduzir(cor_preenchimento, constantes.TRADUCAO_CORES)
    
    canvas = document.getElementById(canvas_id)
    ctx = canvas.getContext('2d')
    ctx.fillStyle = cor_preenchimento_traduzida
    ctx.fillRect(x, y, largura, altura)

def converter_graus_para_radianos(graus):
    return graus * math.pi / 180

# Função para rotacionar um ponto em torno do baricentro
def rotacionar_ponto(x, y, x_centro, y_centro, angulo):
    radianos = converter_graus_para_radianos(angulo)
    x_rotacionado =   (x - x_centro) * math.cos(radianos) - (y - y_centro) * math.sin(radianos) + x_centro
    y_rotacionado = - (x - x_centro) * math.sin(radianos) - (y - y_centro) * math.cos(radianos) + y_centro
    return x_rotacionado, y_rotacionado

def desenhar_triangulo(x_baricentro, y_baricentro, raio_circunscrito, cor, id_canvas, angulo=0, proporcao_base=1):
    cor_traduzida = constantes.traduzir(cor, constantes.TRADUCAO_CORES)
    
    canvas = document.getElementById(id_canvas)
    ctx = canvas.getContext('2d')

    largura_base = raio_circunscrito * proporcao_base
    altura = math.sqrt( raio_circunscrito ** 2 - (largura_base / 2) ** 2)
    
    # Calcula os vértices do triângulo antes da rotação, PADRÃO APONTADO PARA DIREITA
    vertices = [
        (x_baricentro - altura , y_baricentro + (largura_base / 2)),  # Vértice inferior esquerdo
        (x_baricentro + raio_circunscrito, y_baricentro),  # Vértice superior
        (x_baricentro - altura , y_baricentro - (largura_base / 2)) # Vértice inferior direito
    ]
    
    # Rotaciona os vértices
    vertices_rotacionados = [rotacionar_ponto(x, y, x_baricentro, y_baricentro, angulo) for x, y in vertices]
    
    # Desenha o triângulo com os vértices rotacionados
    ctx.beginPath()
    ctx.moveTo(*vertices_rotacionados[0])
    for x, y in vertices_rotacionados[1:]:
        ctx.lineTo(x, y)
    ctx.closePath()
    
    ctx.fillStyle = cor_traduzida
    ctx.fill()

# New function to draw a circle
def desenhar_arco(
        x_centro, 
        y_centro, 
        raio, 
        angulo_inicio, 
        angulo_fim, 
        id_canvas, 
        cor_preenchimento,
        cor_contorno,
        largura_contorno
    ):
    cor_preenchimento_traduzida = constantes.traduzir(cor_preenchimento, constantes.TRADUCAO_CORES)
    cor_contorno_traduzida = constantes.traduzir(cor_contorno, constantes.TRADUCAO_CORES)

    canvas = document.getElementById(id_canvas)  # Access the canvas DOM element by its ID.
    ctx = canvas.getContext('2d')  # Get the 2D drawing context of the canvas.
    angulo_inicio_rad = converter_graus_para_radianos(angulo_inicio)
    angulo_fim_rad = converter_graus_para_radianos(angulo_fim)

    ctx.beginPath()  # Begin a new path for the circle.
    ctx.arc(x_centro, y_centro, raio, angulo_inicio_rad, angulo_fim_rad)  # Draw the circle path.
    
    if cor_preenchimento:
        ctx.fillStyle = cor_preenchimento_traduzida
        ctx.fill() 
    if cor_contorno:
        ctx.strokeStyle = cor_contorno_traduzida
        ctx.stroke()
    if largura_contorno:
        ctx.lineWidth = largura_contorno
        ctx.stroke()


def desenhar_linha(inicio_x, inicio_y, fim_x, fim_y, id_canvas=constantes.NOME_PAINEL_FRENTE, cor="black", largura=1, padrao="solid"):

    cor_traduzida = constantes.traduzir(cor, constantes.TRADUCAO_CORES)
    padrao_traduzido = constantes.traduzir(padrao, constantes.TRADUCAO_PADRAO_DE_LINHA)

    canvas = document.getElementById(id_canvas)  # Acessa o elemento canvas do DOM pelo seu ID.
    ctx = canvas.getContext('2d')  # Obtém o contexto de desenho 2D do canvas.

    ctx.beginPath()  # Inicia um novo caminho para a linha.
    ctx.moveTo(inicio_x, inicio_y)  # Move o ponto de início da linha para as coordenadas especificadas.
    ctx.lineTo(fim_x, fim_y)  # Desenha a linha até as coordenadas especificadas.

    ctx.strokeStyle = cor_traduzida  # Define a cor da linha.
    ctx.lineWidth = largura  # Define a largura da linha.

    # Define o padrão da linha.
    if padrao_traduzido == 'dashed':
        ctx.setLineDash([5, 5])  # Define o padrão de linha tracejada.
    elif padrao_traduzido == 'dotted':
        ctx.setLineDash([1, 5])  # Define o padrão de linha pontilhada.
    else:
        ctx.setLineDash([])  # Linha sólida.

    ctx.stroke()  # Aplica o desenho da linha.

def escrever_texto(texto, x, y, id_canvas, cor="black", tamanho=12, fonte="Arial", alinhamento="start", direcao="ltr"):
    cor_traduzida = constantes.traduzir(cor, constantes.TRADUCAO_CORES)
    
    canvas = document.getElementById(id_canvas)  # Acessa o elemento canvas do DOM pelo seu ID.
    ctx = canvas.getContext('2d')  # Obtém o contexto de desenho 2D do canvas.

    ctx.font = f"{tamanho}px {fonte}"  # Define a fonte e o tamanho do texto.
    ctx.fillStyle = cor_traduzida  # Define a cor do texto.
    ctx.textAlign = alinhamento  # Define o alinhamento horizontal do texto.
    ctx.direction = direcao  # Define a direção do texto.
    ctx.fillText(texto, x, y)  # Desenha o texto nas coordenadas especificadas.

async def animate():
    x = 0
    y = 50
    width = 100
    height = 50
    while x < 300:
        canvas = document.getElementById('myCanvas')
        ctx = canvas.getContext('2d')
        ctx.clearRect(0, 0, canvas.width, canvas.height)

        draw_rect(x, y, width, height)  # Draw the rectangle.
        draw_triangle(x + 50, y + 100, 60, 30)  # Example of drawing a triangle.
        draw_circle(x + 50, y - 30, 25)  # Example of drawing a circle.

        x += 5
        await asyncio.sleep(0.1)