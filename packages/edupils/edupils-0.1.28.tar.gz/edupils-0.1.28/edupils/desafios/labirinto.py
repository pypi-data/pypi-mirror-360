import random
from abc import ABC, abstractmethod
#import asyncio
from .. import constantes
from .. import desenho

class Labirinto:
    DIRECOES = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    PAREDE = '@'
    CELULA = '_'
    NAO_VISITADO = '.'

    def __init__(self, altura, largura, aleatorio=True):
        self.altura = altura
        self.largura = largura
        self.labirinto = [[Labirinto.NAO_VISITADO for _ in range(largura)] for _ in range(altura)]
        self.paredes = []
        
        self.entrada = None
        self.saida = None

        if aleatorio:
            self._gerar_labirinto_aleatorio()
        else:
            self._gerar_labirinto_vazio()

        
        self._processamento_pos_geracao()

        self.representacao = None

        self.mostrar()

    def _contar_celulas_adjacentes(self, parede_aleatoria, tipo_posicao):
        celulas_adjacentes = 0
        h, w = parede_aleatoria
        for dH, dW in Labirinto.DIRECOES:
            if self.labirinto[h+dH][w+dW] == tipo_posicao:
                celulas_adjacentes += 1
        return celulas_adjacentes

    def _gerar_posicao_no_meio(self):
        h = int(random.random() * (self.altura - 2)) + 1
        w = int(random.random() * (self.largura - 2)) + 1
        return h, w

    def _gerar_labirinto_aleatorio(self):
        altura_inicial, largura_inicial = self._gerar_posicao_no_meio()
        self.labirinto[altura_inicial][largura_inicial] = Labirinto.CELULA
        for dH, dW in Labirinto.DIRECOES:
            self.paredes.append([altura_inicial + dH, largura_inicial + dW])
            self.labirinto[altura_inicial + dH][largura_inicial + dW] = Labirinto.PAREDE

        while self.paredes:
            parede_aleatoria = self.paredes[int(random.random()*len(self.paredes))-1]

            for h, w in Labirinto.DIRECOES:
                direcao_encontrada = False
                if 0 < parede_aleatoria[0] < self.altura-1 and 0 < parede_aleatoria[1] < self.largura-1:
                    if self.labirinto[parede_aleatoria[0]+h][parede_aleatoria[1]+w] == Labirinto.NAO_VISITADO and self.labirinto[parede_aleatoria[0]-h][parede_aleatoria[1]-w] == Labirinto.CELULA:
                        direcao_encontrada = True
                        celulas_adjacentes = self._contar_celulas_adjacentes(parede_aleatoria, Labirinto.CELULA)
                        if celulas_adjacentes < 2:
                            self.labirinto[parede_aleatoria[0]][parede_aleatoria[1]] = Labirinto.CELULA
                            for h2, w2 in Labirinto.DIRECOES:
                                if (h2, w2) != (-h, -w):
                                    if self.labirinto[parede_aleatoria[0]+h2][parede_aleatoria[1]+w2] != Labirinto.CELULA:
                                        self.labirinto[parede_aleatoria[0]+h2][parede_aleatoria[1]+w2] = Labirinto.PAREDE
                                    if [parede_aleatoria[0]+h2, parede_aleatoria[1]+w2] not in self.paredes:
                                        self.paredes.append([parede_aleatoria[0]+h2, parede_aleatoria[1]+w2])
                        if parede_aleatoria in self.paredes:
                            self.paredes.remove(parede_aleatoria)

                if direcao_encontrada:
                    break

            if parede_aleatoria in self.paredes:
                self.paredes.remove(parede_aleatoria)

    def _gerar_labirinto_vazio(self):
        for i in range(self.altura):
            for j in range(self.largura):
                if ((i == 0) or 
                    (i == self.altura-1) or 
                    (j == 0) or 
                    (j == self.largura-1)):
                    self.labirinto[i][j] = Labirinto.PAREDE
                    self.paredes.append([i, j])
                else:
                    self.labirinto[i][j] = Labirinto.CELULA



    def _processamento_pos_geracao(self):
        # Transformar células não visitadas em paredes
        for i in range(self.altura):
            for j in range(self.largura):
                if self.labirinto[i][j] == Labirinto.NAO_VISITADO:
                    self.labirinto[i][j] = Labirinto.PAREDE

        # Definir entrada e saída
        for i in range(self.largura):
            if self.labirinto[1][i] == Labirinto.CELULA:
                self.labirinto[0][i] = Labirinto.CELULA
                self.entrada = (0, i)
                break

        for i in range(self.largura-1, 0, -1):
            if self.labirinto[self.altura-2][i] == Labirinto.CELULA:
                self.labirinto[self.altura-1][i] = Labirinto.CELULA
                self.saida = (self.altura-1, i)
                break

    def mostrar_labirinto(self):
        for linha in self.labirinto:
            print(' '.join(linha))

    def eh_parede(self, coordenada):
        h, w = coordenada
        return self.labirinto[h][w] == Labirinto.PAREDE
    
    def mostrar(
            self, 
            camada=constantes.NOME_PAINEL_FUNDO,
            largura_do_tile=25,
        ):

        desenho.apagar_painel(camada)

        for i, linha in enumerate(self.labirinto):
            for j, celula in enumerate(linha):
                if celula == Labirinto.PAREDE:
                    desenho.desenhar_retangulo(
                        j * largura_do_tile, 
                        i * largura_do_tile, 
                        largura_do_tile, 
                        largura_do_tile, 
                        camada, 
                        cor_preenchimento=constantes.COR_ESCURA
                    )

        self.desenhar_saida(largura_do_tile)

    def desenhar_saida(self, largura_do_tile):
        h, w = self.saida
        n = 4
        d = largura_do_tile / n
        for i in range(n):
            for j in range(n):
                if (i+j) % 2 == 0:
                    desenho.desenhar_retangulo(
                        (w) * largura_do_tile + i * d, 
                        (h) * largura_do_tile + j * d, 
                        d, 
                        d, 
                        constantes.NOME_PAINEL_FUNDO, 
                        cor_preenchimento=constantes.COR_SECUNDARIA
                    )

    def get_labirinto(self):
        return self.labirinto, self.paredes
    

class Jog(ABC):
    DIRECOES = {
        'cima': (-1, 0),
        'baixo': (1, 0),
        'direita': (0, 1),
        'esquerda': (0, -1)
    }
    DIRECORES_INV = {v:k for k,v in DIRECOES.items()}

    def __init__(self, labirinto):
        self.labirinto = labirinto
        self.posicao = labirinto.entrada
        self.historico = []

    @abstractmethod
    def mover(self):
        pass

    @abstractmethod
    def redondezas_livres(self):
        pass

    def mostrar_jogador_e_labirinto(self):
        for i, linha in enumerate(self.labirinto.labirinto):
            for j, celula in enumerate(linha):
                if (i, j) == self.posicao:
                    print(self.representacao, end=' ')
                else:
                    print(celula, end=' ')
            print()


class Jogador(Jog):
    OPCOES_REPRESENTACAO = {
        'cima': '^',
        'direita': '>',
        'baixo': 'v',
        'esquerda': '<'
    }

    ORIENTACAO_PARA_GRAUS = {
        'cima': 90,
        'direita': 0,
        'baixo': 270,
        'esquerda': 180
    }

    def __init__(self, labirinto):
        super().__init__(labirinto)
        self.orientacao = "baixo"
        self.vetor = Jogador.DIRECOES[self.orientacao]
        self.representacao = Jogador.OPCOES_REPRESENTACAO[self.orientacao]
        self.redondezas_livres()

        self.mostrar()

    def virar(self, direcao): #async
        h, w = self.vetor
        if direcao == 'esquerda':
            self.vetor = (-w, h)
            
        elif direcao == 'direita':
            self.vetor = (w, -h)

        self.orientacao = Jogador.DIRECORES_INV[self.vetor]
        self.representacao = Jogador.OPCOES_REPRESENTACAO[self.orientacao]
        #await asyncio.sleep(0.5)
        self.mostrar()
        self.redondezas_livres()
        
    def mover(self, passos=1): #async 
        dH, dW = self.vetor
        #await asyncio.sleep(0.1)
        for p in range(passos):
            nova_posicao = (self.posicao[0] + dH, self.posicao[1] + dW)
            if not self.labirinto.eh_parede(nova_posicao) and (self.posicao != self.labirinto.saida):
                self.posicao = nova_posicao
                self.historico.append(self.posicao)
                if self.posicao == self.labirinto.saida:
                    self.dar_os_parabens()
                    print("Aeee!")
                else:
                    self.mostrar()
            
        if (self.posicao != self.labirinto.saida):
            self.redondezas_livres()

    def teleportar_para_o_inicio(self):
        self.posicao = self.labirinto.entrada
        self.orientacao = "baixo"
        self.vetor = Jogador.DIRECOES[self.orientacao]
        self.representacao = Jogador.OPCOES_REPRESENTACAO[self.orientacao]
        self.redondezas_livres()

        self.mostrar()
    
    def redondezas_livres(self):
        self.redondezas = {}
        dH, dW = self.vetor
        h, w = self.posicao
        self.redondezas["frente"] = not self.labirinto.eh_parede((h+dH, w+dW))
        self.redondezas["esquerda"] = not self.labirinto.eh_parede((h-dW, w+dH))
        self.redondezas["direita"] = not self.labirinto.eh_parede((h+dW, w-dH))
        self.redondezas["trás"] = not self.labirinto.eh_parede((h-dH, w-dW))
        
        return self.redondezas
    
    def esta_livre(self, direcao):
        if direcao in self.redondezas.keys():
            return self.redondezas[direcao]

    def mostrar(
            self,
            camada=constantes.NOME_PAINEL_FRENTE,
            largura_do_tile=25,
        ):
        desenho.apagar_painel(camada)
        h, w = self.posicao
        desenho.desenhar_triangulo(
            x_baricentro=w * largura_do_tile + largura_do_tile/2, 
            y_baricentro=h * largura_do_tile + largura_do_tile/2, 
            raio_circunscrito=(largura_do_tile-5) /2, 
            cor=constantes.COR_PRIMARIA, 
            id_canvas=camada, 
            angulo=self.ORIENTACAO_PARA_GRAUS[self.orientacao],
        )

    def dar_os_parabens(
            self,
            camada=constantes.NOME_PAINEL_FRENTE,
            largura_do_tile=25,
        ):
        desenho.apagar_painel(camada)
        desenho.escrever_texto(
            "Parabéns!!",
            largura_do_tile,
            largura_do_tile * (self.labirinto.altura // 2),
            camada,
            tamanho=30,
            cor="red"
        )

#class JogadorComBussola(Jog):

#     def __init__(self, labirinto):
#         super().__init__(labirinto)
#         self.representacao = "X"

#     def mover(self, direcao):
#         if direcao in JogadorComBussola.DIRECOES:
#             dH, dW = JogadorComBussola.DIRECOES[direcao]
#             nova_posicao = (self.posicao[0] + dH, self.posicao[1] + dW)

#             if not self.labirinto.eh_parede(nova_posicao):
#                 self.posicao = nova_posicao
#                 self.historico.append(self.posicao)
#                 return True
#         return False
    
#     def redondezas_livres(self):
#         redondezas = []
#         h, w = self.posicao

#         for direcao, (dH, dW) in Jogador.DIRECOES:
#             if not self.labirinto.eh_parede((h+dH, w+dW)):
#                 redondezas.append(direcao)
#         return redondezas

    
def criar_labirinto_e_jogador():
    lab = Labirinto(10,10)
    p = Jogador(lab)
    return lab, p

if __name__ == "__main__":
    lab = Labirinto(10,10)
    p = Jogador(lab)


    for i in range(5):
        redond = p.redondezas_livres()
        if "frente" in redond:
            p.mover()
        else:
            p.virar("esquerda")