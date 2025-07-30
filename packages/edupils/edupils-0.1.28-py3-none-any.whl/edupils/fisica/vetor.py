class Vetor:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def norma(self):
        return (self.x**2 + self.y**2)**0.5
    
    def normalizar(self):
        norma = self.norma()
        return self / norma if norma != 0 else Vetor(0, 0)

    def produto_escalar(self, outro):
        return self.x * outro.x + self.y * outro.y

    def projetar(self, outro):
        produto_escalar = self.produto_escalar(outro)
        norma_quadrado = outro.norma()**2
        if norma_quadrado != 0:
            fator = produto_escalar / norma_quadrado
            return Vetor(fator * outro.x, fator * outro.y)
        return Vetor(0, 0)  # Caso o vetor sobre o qual estamos projetando tenha norma 0, retorna um vetor nulo
    
    def perpendicular(self):
        return Vetor(-self.y, self.x)
    
    def aplicar(self, f):
        return Vetor(f(self.x), f(self.y))
    
    def __add__(self, outro):
        return Vetor(self.x + outro.x, self.y + outro.y)

    def __sub__(self, outro):
        return Vetor(self.x - outro.x, self.y - outro.y)
    
    def __repr__(self):
        return f"Vetor({self.x}, {self.y})"
    
    def __mul__(self, escalar):
        if isinstance(escalar, (int, float)):
            return Vetor(self.x * escalar, self.y * escalar)
        else:
            raise TypeError("O operador deve ser um número inteiro ou flutuante")

    def __rmul__(self, escalar):
        # Isso permite a multiplicação escalar tanto à esquerda quanto à direita do vetor
        return self.__mul__(escalar)
    
    def __truediv__(self, escalar):
        if isinstance(escalar, (int, float)):
            return Vetor(self.x / escalar, self.y / escalar)
        else:
            raise TypeError("O operador deve ser um número inteiro ou flutuante")

    def __iter__(self):
        yield self.x
        yield self.y

if __name__ == "__main__":
    from grandezas import Posicao, Velocidade, Tempo

    p = Vetor(
        Posicao(0),
        Posicao(-1),
    )

    v = Vetor(
        Velocidade(-1),
        Velocidade(2)
    )

    print(p + v * Tempo(2))