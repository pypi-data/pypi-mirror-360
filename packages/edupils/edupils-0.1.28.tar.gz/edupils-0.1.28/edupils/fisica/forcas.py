from grandezas import Forca
from vetor import Vetor
from abc import abstractmethod

class ForcaVetorial(Vetor):

    def __init__(self, x, y):
        super().__init__(Forca(x), Forca(y))
    
    @abstractmethod
    def atualizar(self):
        pass

class ForcaAtrito(ForcaVetorial):
    def __init__(self, x, y, coeficiente_atrito=0.1):
        super().__init__(x, y)
    
    def atualizar(self, forca_normal, velocidade):
        pass

class ForcaElastica(ForcaVetorial):
    def __init__(self, x, y, constante_elastica=1, distancia_repouso=1):
        super().__init__(x, y)
        self.constante_elastica = constante_elastica
        self.distancia_repouso = distancia_repouso
    
    def atualizar(self, posicao_atual, posicao_outra_extremidade):
        posicao_relativa = posicao_outra_extremidade - posicao_atual
        deformacao = posicao_relativa.norma() - self.distancia_repouso
        self.x, self.y = (posicao_relativa.normalizar() * self.constante_elastica * deformacao).aplicar(Forca)

class ForcaGravitacao(ForcaVetorial):
    def __init__(self, x, y, constante_gravitacao=1):
        super().__init__(x, y)
        self.constante_gravitacao = constante_gravitacao
    
    def atualizar(self, massa1, massa2, posicao1, posicao2):
        posicao_relativa = posicao2 - posicao1
        self.x, self.y = (posicao_relativa.normalizar() * self.constante_gravitacao * massa1 * massa2 / posicao_relativa.norma()**2).aplicar(Forca)

class ForcaEletromagnetica(ForcaVetorial):
    def __init__(self, x, y, constante_eletromagnetica=1):
        super().__init__(x, y)
        self.constante_eletromagnetica = constante_eletromagnetica
    
    def atualizar(self, carga1, carga2, posicao1, posicao2, velocidade1, velocidade2):
        posicao_relativa = posicao2 - posicao1
        velocidade_relativa = velocidade2 - velocidade1
        self.x, self.y = (posicao_relativa.normalizar() * self.constante_eletromagnetica * carga1 * carga2 / posicao_relativa.norma()**2).aplicar(Forca) + (velocidade_relativa.normalizar() * self.constante_eletromagnetica * carga1 * carga2 / posicao_relativa.norma()**2).aplicar(Forca)


class ForcaArrasto(ForcaVetorial):
    def __init__(self, x, y, coeficiente_arrasto=1):
        super().__init__(x, y)
        self.coeficiente_arrasto = coeficiente_arrasto
    
    def atualizar(self, velocidade):
        self.x, self.y = (velocidade.normalizar() * self.coeficiente_arrasto * velocidade.norma()**2).aplicar(Forca)


if __name__ == "__main__":
    from grandezas import Posicao

    forca = ForcaElastica(1, 1)
    print(forca)  # Vetor(1.0 N, 1.0 N)

    forca.atualizar(Vetor(Posicao(0), Posicao(0)), Vetor(Posicao(1), Posicao(1)))

    print(forca)