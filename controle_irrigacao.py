import threading
import time
from sensor_vazao import SensorVazao
from valvula_solenoid import ValvulaSolenoid

class ControleIrrigacao:
    def __init__(self, comunicacao):
        self.comunicacao = comunicacao
        self.vazao_litros_por_segundo = 1.0 / 15  # 1 litro a cada 15 segundos
        self.sensor = SensorVazao(self.vazao_litros_por_segundo)
        self.valvula = ValvulaSolenoid()
        self.publicar_volume = False

    def processar_mensagem(self, client, userdata, message):
        mensagem_recebida = message.payload.decode()
        print(f"Microcontrolador recebeu: {mensagem_recebida}")

        if mensagem_recebida == "ligar_valvula":
            self.valvula.abrir()
            self.sensor.iniciar_medicao()
            self.publicar_volume = True
            threading.Thread(target=self.monitorar_acao).start()
            self.comunicacao.enviar_mensagem("microcontrolador/to/borda", "Status: Válvula ligada")

        elif mensagem_recebida == "desligar_valvula":
            volume_total = self.sensor.obter_volume_atual()
            self.valvula.fechar()
            self.comunicacao.enviar_mensagem("microcontrolador/to/borda", f"Status: Volume total: {volume_total} litros")
            self.sensor.zerar_contagem()
            self.comunicacao.enviar_mensagem("microcontrolador/to/borda", "Status: Zerar contagem")
            self.comunicacao.enviar_mensagem("microcontrolador/to/borda", "Status: Válvula desligada")
            self.publicar_volume = False

    def monitorar_acao(self):
        while self.publicar_volume:
            time.sleep(10)
