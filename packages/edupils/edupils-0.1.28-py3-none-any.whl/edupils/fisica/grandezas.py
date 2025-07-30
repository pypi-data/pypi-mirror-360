class GrandezaFisica(float):
    unidade = ""

    def __new__(cls, valor):
        return float.__new__(cls, valor)

    def __repr__(self):
        return f"{super().__repr__()} {self.unidade}"

    def __add__(self, outro):
        if isinstance(outro, GrandezaFisica) and self.unidade == outro.unidade:
            return self.__class__(super().__add__(outro))
        else:
            raise TypeError(f"Não é possível somar {self.unidade} com {outro.unidade}")
        
    def __sub__(self, outro):
        if isinstance(outro, GrandezaFisica) and self.unidade == outro.unidade:
            return self.__class__(super().__sub__(outro))
        else:
            raise TypeError(f"Não é possível subtrair {self.unidade} com {outro.unidade}")
        
    def __mul__(self, outro):
        if isinstance(outro, (int, float)) and not isinstance(outro, GrandezaFisica):
            return self.__class__(super().__mul__(outro))
        else:
            raise TypeError(f"Não é possível multiplicar {self.unidade} com {outro.unidade}")
    
    def __rmul__(self, outro):
        if isinstance(outro, (int, float)) and not isinstance(outro, GrandezaFisica):
            return self.__class__(super().__mul__(outro))
        else:
            raise TypeError(f"Não é possível multiplicar {self.unidade} com {outro.unidade}")

    def __truediv__(self, outro):
        if isinstance(outro, (int, float)) and not isinstance(outro, GrandezaFisica):
            return self.__class__(super().__truediv__(outro))
        else:
            raise TypeError(f"Não é possível dividir {self.unidade} por {outro.unidade}")
        
    

class Tempo(GrandezaFisica):
    unidade = "s"

class Posicao(GrandezaFisica):
    unidade = "m"

    def __truediv__(self, outro):
        if isinstance(outro, Tempo):
            return Velocidade(self / outro)
        else:
            return super().__truediv__(outro)


class Velocidade(GrandezaFisica):
    unidade = "m/s"

    def __mul__(self, outro):
        if isinstance(outro, Tempo):
            return Posicao(float(self) * float(outro))
        else:
            return super().__mul__(outro)

    def __rmul__(self, outro):
        if isinstance(outro, Tempo):
            return Posicao(float(self) * float(outro))
        else:
            return super().__rmul__(outro)
        
    def __truediv__(self, outro):
        if isinstance(outro, Tempo):
            return Aceleracao(float(self) / float(outro))
        else:
            return super().__truediv__(outro)


class Aceleracao(GrandezaFisica):
    unidade = "m/s^2"

    def __mul__(self, outro):
        if isinstance(outro, Tempo):
            return Velocidade(float(self) * float(outro))
        else:
            return super().__mul__(outro)
        
    def __rmul__(self, outro):
        if isinstance(outro, Tempo):
            return Velocidade(float(self) * float(outro))
        else:
            return super().__rmul__(outro)
        
    def __truediv__(self, outro):
        if isinstance(outro, Tempo):
            raise TypeError(f"A taxa de variação da aceleração em ({self.unidade}) no tempo em ({outro.unidade}) é uma grandeza física que não usaremos nesta atividade.")
        else:
            return super().__truediv__(outro)

class Massa(GrandezaFisica):
    unidade = "kg"

class Forca(GrandezaFisica):
    unidade = "N"

    def __truediv__(self, outro):
        if isinstance(outro, Massa):
            return Aceleracao(float(self) / float(outro))
        else:
            return super().__truediv__(outro)

class Energia(GrandezaFisica):
    unidade = "J"

if __name__ == "__main__":
    # Somando duas grandezas do mesmo tipo
    tempo1 = Tempo(10)
    tempo2 = Tempo(5)
    print(tempo1 + tempo2)  # 15.0 s

    # Multiplicando velocidade por tempo para obter posição
    velocidade = Velocidade(2)
    tempo = Tempo(3)
    posicao = velocidade * tempo
    print(posicao)  # 6.0 m

    # Multiplicando aceleração por tempo para obter velocidade
    aceleracao = Aceleracao(9.8)
    tempo = Tempo(2)
    velocidade = aceleracao * tempo
    print(velocidade)  # 19.6 m/s