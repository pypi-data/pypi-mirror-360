from vetor import Vetor
import grandezas
#from edupils import desenho
from edupils import constantes
import math
import asyncio

class Simulacao:
    def __init__(
            self, 
            largura=500,
            altura=300,
            raio_max=50,
            pixels_por_metro=10,
            tempo_total=grandezas.Tempo(10),
            tempo_por_frame=grandezas.Tempo(.1),
            plotar_escala=True,
            plotar_trajetoria=False,
            plotar_velocidade=False,
            painel_frente = constantes.NOME_PAINEL_FRENTE,
            painel_fundo = constantes.NOME_PAINEL_FUNDO,
            painel_auxiliar=constantes.NOME_PAINEL_AUXILIAR,
            adicionar_gravidade=True
        ):
        self.largura = largura
        self.altura = altura
        self.velocidade_maxima = min(altura, largura) / 2
        self.raio_maximo = raio_max  # Define o tamanho de cada célula na grade
        
        self.objetos = []  # Lista para armazenar os objetos na simulação
        self.forcas = []

        self.T = tempo_total
        self.dt = tempo_por_frame

    def adicionar_objeto(self, objeto):
        """Adiciona um novo objeto à simulação e o posiciona na grade espacial."""
        assert objeto.raio <= self.raio_maximo
        self.objetos.append(objeto)
    
    def ordenar_objetos(self):
        self.objetos = sorted(self.objetos, key=lambda ob: ob.x)

    def varredura_colisoes(self):
        self.ordenar_objetos()
        colisoes = []
        for i in range(len(self.objetos)-1):
            for j in range(i+1, len(self.objetos)):
                if self.detectar_colisao_entre_objetos(self.objetos[i], self.objetos[j]):
                    colisoes.append((i, j))
                
                if ((self.objetos[i].x + self.raio_maximo) < 
                    (self.objetos[j].x - self.raio_maximo)):
                    break

    def detectar_colisao_entre_objetos(self, objeto1, objeto2):
        """Verifica se há colisão entre dois objetos."""
        dx = objeto1.x - objeto2.x
        dy = objeto1.y - objeto2.y
        distancia = (dx**2 + dy**2)**0.5
        return distancia < (objeto1.raio + objeto2.raio)


    def resolver_colisao(self, objeto1, objeto2):
        """Resolve a colisão ajustando as posições e velocidades dos objetos."""
        normal = (objeto1 - objeto2)
        distancia = normal.norma()
        normal_unitaria = normal.normalizar()
        
        deslocamento = (objeto1.raio + objeto2.raio - distancia) / 2

        tangente = normal.perpendicular()
        
        # Ajustar posições
        objeto1.posicao += normal_unitaria * deslocamento
        objeto2.posicao -= normal_unitaria * deslocamento



    def tratar_colisoes_rigidas(self):
        for objeto in self.objetos:
            if objeto.posicao.x - objeto.raio < 0:
                objeto.posicao.x = objeto.raio
                objeto.velocidade.x = -objeto.velocidade.x
            elif objeto.posicao.x + objeto.raio >  self.largura:
                objeto.posicao.x = self.largura - objeto.raio
                objeto.velocidade.x = -objeto.velocidade.x
            if objeto.posicao.y - objeto.raio < 0:
                objeto.posicao.y = objeto.raio
                objeto.velocidade.y = -objeto.velocidade.y
            elif objeto.posicao.y + objeto.raio > self.altura:
                objeto.posicao.y = self.altura - objeto.raio
                objeto.velocidade.y = -objeto.velocidade.y

    def tratar_colisoes_entre_objetos(self):
        while False:
            self.varredura_colisoes()
        
        pass

    def atualizar_forcas_externas(self):
        pass

    def atualizar_estado(self):
        """Atualiza o estado da simulação."""
        #Objeto simulação atualiza as forças externas dentro de cada objeto cadastrado dentro de sua lista de objetos (pares ação reação, molas, gravitações, magnetismos)
        
        self.atualizar_forcas_externas()

        # Cada objeto internamente atualiza seu estado
        for objeto in self.objetos:
            objeto.atualiza_estado(self.dt)

        # Checar colisões contra corpos imóveis, quiques (paredes apenas, por enquanto) e resolver o quique: Atualizar posiç~ao e atualizar velocidade
        self.tratar_colisoes_rigidas()

        # Checar colisões contra outros objetos por varredura e resolver choque elastico.
        self.tratar_colisoes_entre_objetos()

    def simular(self):
        t = 0

        while t < self.T:
            self.atualizar_estado()
            t += self.dt


    def plotar_eixos():
        pass

    def plotar_velocidades():
        pass

    def plotar_trajetoria():
        pass


class Objeto:
    def __init__(self, x, y, vx, vy, massa=1):
        self.posicao = Vetor(
            grandezas.Posicao(x), 
            grandezas.Posicao(y)
        )
    
        self.velocidade = Vetor(
            grandezas.Velocidade(vx), 
            grandezas.Velocidade(vy)
        )
        self.massa = grandezas.Massa(massa)
        self.forcas = [] # que só dependendem do objeto como gravidade, atrito, arrasto
        self.forcas_externas = {} #que dependem de outros objetos, ação e reação, como molas, magnetismos, 

    def adiciona_forca(self, forca):
        self.forcas.append(forca)
    
    def aceleracao_resultante(self):
        forcas_internas = sum(self.forcas)
        forcas_externas = sum(self.forcas_externas.values)
        forca_resultante = forcas_internas + forcas_externas
        aceleracao_resultante = forca_resultante / self.massa
        return aceleracao_resultante

    def atualiza_estado(self, dt):
        a = self.aceleracao_resultante()
        self.velocidade += a * dt
        self.posicao += self.velocidade * dt

class Circulo(Objeto):
    def __init__(self, x, y, vx, vy, raio, massa=None, cor="roxo"):
        if massa is None:
            massa = raio ** 2
        super().__init__(x, y, vx, vy, massa)
        self.raio = grandezas.Posicao(raio)

    def centro(self):
        return self.posicao
    
    def plotar(self, canvas_id):
        pass
        # desenho.desenhar_arco(
        #     self.posicao.x, 
        #     self.posicao.y, 
        #     self.raio, 
        #     0, 
        #     2 * math.pi, 
        #     canvas_id, 
        #     self.cor
        # )
    
if __name__ == "__main__":
    from forcas import ForcaVetorial
    sim = Simulacao()

    cir = Circulo(5, 15, 5, 0, 1)
    cir.forcas.append(ForcaVetorial(0, -9.8))
    sim.adicionar_objeto(cir)
    sim.simular()