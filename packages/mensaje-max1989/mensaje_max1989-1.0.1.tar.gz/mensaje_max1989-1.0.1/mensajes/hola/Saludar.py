def saludar():
    print("Hola te saludo desde saludos.saludar()")
    print("Texto adicional")

def prueba():
    return "Esto es una prueba desde la nueva version"

class Saludo:
    def __init__(self):
        print("Hola te saludo dede Saludo.__init__()")

if __name__ == "__main__":
    print(saludar())
