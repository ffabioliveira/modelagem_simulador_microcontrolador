class ValvulaSolenoid:
    def __init__(self):
        self.aberta = False

    def abrir(self):
        if not self.aberta:
            self.aberta = True
            print("Válvula aberta.")
        else:
            print("A válvula já está aberta.")

    def fechar(self):
        if self.aberta:
            self.aberta = False
            print("Válvula fechada.")
        else:
            print("A válvula já está fechada.")
