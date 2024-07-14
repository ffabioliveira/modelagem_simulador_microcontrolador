import time
from comunicacao_mqtt import ComunicacaoMQTT
from controle_irrigacao import ControleIrrigacao

class Main:
    def __init__(self, broker, client_id):
        self.comunicacao = ComunicacaoMQTT(broker, client_id)
        self.controle_irrigacao = ControleIrrigacao(self.comunicacao)
        self.comunicacao.inscrever("borda/to/microcontrolador", self.controle_irrigacao.processar_mensagem)

    def iniciar(self):
        self.comunicacao.conectar()

if __name__ == '__main__':
    sistema = Main('10.0.0.117', 'microcontrolador')
    sistema.iniciar()
    try:
        while True:
            time.sleep(1)  # Manter o script rodando
    except KeyboardInterrupt:
        print("Interrompido pelo usuário.")
