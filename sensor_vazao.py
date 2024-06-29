# sensor_vazao.py
import time

class SensorVazao:
    def __init__(self, vazao_litros_por_segundo):
        self.vazao = vazao_litros_por_segundo
        self.tempo_inicio = None
        self.volume_total_consumido = 0

    def iniciar_medicao(self):
        self.tempo_inicio = time.time()
        print("Iniciando medição.")

    def parar_medicao(self):
        if self.tempo_inicio:
            elapsed_time = time.time() - self.tempo_inicio
            self.volume_total_consumido += elapsed_time * self.vazao
            self.tempo_inicio = None
            print(f"Volume total consumido: {self.volume_total_consumido:.2f} litros")
            return self.volume_total_consumido

    def zerar_contagem(self):
        self.volume_total_consumido = 0
        print("Zerando contagem.")

    def obter_volume_atual(self):
        if self.tempo_inicio:
            elapsed_time = time.time() - self.tempo_inicio
            volume_atual = self.volume_total_consumido + elapsed_time * self.vazao
            return volume_atual
        else:
            return self.volume_total_consumido

class ValvulaSolenoid:
    def __init__(self):
        self.aberta = False

    def abrir(self):
        self.aberta = True
        print("Válvula aberta.")

    def fechar(self):
        self.aberta = False
        print("Válvula fechada.")
