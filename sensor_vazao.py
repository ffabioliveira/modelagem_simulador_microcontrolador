import time

class SensorVazao:
    def __init__(self, vazao_litros_por_segundo):
        self.vazao_litros_por_segundo = vazao_litros_por_segundo
        self.volume = 0.0
        self.start_time = None

    def iniciar_medicao(self):
        self.start_time = time.time()
        self.volume = 0.0

    def parar_medicao(self):
        if self.start_time:
            self.volume += self.vazao_litros_por_segundo * (time.time() - self.start_time)
        return self.volume

    def obter_volume_atual(self):
        if self.start_time:
            tempo_decorrido = time.time() - self.start_time
            self.volume = self.vazao_litros_por_segundo * tempo_decorrido
        return self.volume

    def zerar_contagem(self):
        self.volume = 0.0
        self.start_time = None

    def tempo_decorrido(self):
        if self.start_time:
            return (time.time() - self.start_time) / 60  # Retorna o tempo em minutos
        return 0.0
