class ValvulaSolenoid:
    def __init__(self):
        self.aberta = False

    def abrir(self):
        self.aberta = True
        print("Válvula aberta.")

    def fechar(self):
        self.aberta = False
        print("Válvula fechada.")

