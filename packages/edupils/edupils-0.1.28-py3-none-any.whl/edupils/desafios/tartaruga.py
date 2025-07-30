from js import document
import math
from .. import constantes
from .. import desenho

class Tartaruga:
    def __init__(
            self, 
            id_canvas_auxiliar=constantes.NOME_PAINEL_AUXILIAR,
            id_canvas_frente=constantes.NOME_PAINEL_FRENTE, 
            largura_canvas=constantes.LARGURA_PADRAO_CANVAS, 
            altura_canvas=constantes.ALTURA_PADRAO_CANVAS, 
            padrao_linha="solido",
            cor_linha="preto",
            peso_linha=1,
            cor_tartaruga="verde",
            tamanho_tartaruga=10,
        ):
        
        self.id_canvas_auxiliar = id_canvas_auxiliar
        self.id_canvas_frente = id_canvas_frente
        self.x = largura_canvas / 2
        self.y = altura_canvas / 2
        self.theta = 0  # Angulo inicial olhando para a direita
        self.caneta_abaixada = False
        self.largura_canvas = largura_canvas
        self.altura_canvas = altura_canvas

        self.mudar_cor_linha(cor_linha)
        self.mudar_padrao_linha(padrao_linha, peso_linha)
        
        self.tamanho_tartaruga = tamanho_tartaruga
        self.mudar_cor_tartaruga(cor_tartaruga)

    def abaixar_caneta(self):
        self.caneta_abaixada = True

    def levantar_caneta(self):
        self.caneta_abaixada = False

    def virar(self, angulo):
        self.theta += angulo
        self.desenhar_tartaruga()

    def andar(self, distancia):
        x_novo = self.x + math.cos(math.radians(self.theta)) * distancia
        y_novo = self.y - math.sin(math.radians(self.theta)) * distancia
        
        desenho.apagar_painel(self.id_canvas_frente)
        if self.caneta_abaixada:
            desenho.desenhar_linha(
                inicio_x=self.x, 
                inicio_y=self.y, 
                fim_x=x_novo, 
                fim_y=y_novo,
                id_canvas=self.id_canvas_auxiliar,
                cor=self.cor_linha_traduzida,
                largura=1,
                padrao=self.padrao_linha_traduzido,
            )
        
        self.x = x_novo
        self.y = y_novo

        self.desenhar_tartaruga()

    def desenhar_tartaruga(self):
        desenho.apagar_painel(self.id_canvas_frente)
        desenho.desenhar_triangulo(
            x_baricentro=self.x, 
            y_baricentro=self.y, 
            raio_circunscrito=self.tamanho_tartaruga, 
            cor=self.cor_tartaruga_traduzida, 
            id_canvas=self.id_canvas_frente, 
            angulo=self.theta
        )

    def voltar_para_casa(self):
        self.x = self.largura_canvas / 2
        self.y = self.altura_canvas / 2
        self.theta = 0
        desenho.apagar_painel(self.id_canvas_auxiliar)
        self.desenhar_tartaruga()

    def desenhar_linha(self, inicio_x, inicio_y, fim_x, fim_y):
        canvas = document.getElementById(self.id_canvas)
        ctx = canvas.getContext('2d')
        ctx.beginPath()
        ctx.moveTo(inicio_x, inicio_y)
        ctx.lineTo(fim_x, fim_y)
        ctx.stroke()

    def mudar_cor_linha(self, cor):
        self.cor_linha = cor
        cor_traduzida = constantes.traduzir(cor, constantes.TRADUCAO_CORES)
        self.cor_linha_traduzida = cor_traduzida

    def mudar_padrao_linha(self, padrao=None, peso_linha=None):
        if padrao:
            self.padrao_linha = padrao
            padrao_traduzido = constantes.traduzir(padrao, constantes.TRADUCAO_PADRAO_DE_LINHA)
            self.padrao_linha_traduzido = padrao_traduzido
        if peso_linha:
            self.peso_linha = peso_linha

    def mudar_tamanho_tartaruga(self, tamanho):
        self.tamanho_tartaruga = tamanho
        self.desenhar_tartaruga()

    def mudar_cor_tartaruga(self, cor):
        self.cor_tartaruga = cor
        cor_traduzida = constantes.traduzir(cor, constantes.TRADUCAO_CORES)
        self.cor_tartaruga_traduzida = cor_traduzida
        self.desenhar_tartaruga()




# if __name__ == "__main__":
        
    # Exemplo de uso:
    # # Supondo que as constantes de largura e altura do canvas sejam definidas em outro lugar do código.
    # largura_canvas = 500  # Exemplo de largura
    # altura_canvas = 300   # Exemplo de altura
    # tartaruga = Tartaruga(constantes.NOME_PAINEL_AUXILIAR, largura_canvas, altura_canvas)
    # tartaruga.abaixar_caneta()
    # tartaruga.andar(100)
    # tartaruga.virar(90)
    # tartaruga.andar(50)
