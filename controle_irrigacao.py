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

    def publicar_volume_periodicamente(self, tempo_acionamento, intervalo):
        start_time = time.time()
        tempo_acionamento_segundos = tempo_acionamento * 60
        proxima_publicacao = time.time() + 60

        self.comunicacao.enviar_mensagem("microcontrolador/to/borda", "Status: Válvula ligada")
        print("Microcontrolador informou: Status: Válvula ligada")

        while time.time() - start_time < tempo_acionamento_segundos and self.publicar_volume:
            if self.valvula.aberta:
                volume_total = self.sensor.obter_volume_atual()
                if time.time() >= proxima_publicacao:
                    self.comunicacao.enviar_mensagem("microcontrolador/to/borda", f"Status: Volume parcial: {volume_total:.2f} litros de água")
                    print(f"Microcontrolador informou: Status: Volume parcial: {volume_total:.2f} litros de água")
                    proxima_publicacao = time.time() + 60
                time.sleep(1)

        # Calcular o volume dos segundos restantes
        tempo_restante = tempo_acionamento_segundos - (time.time() - start_time)
        volume_restante = self.sensor.vazao_litros_por_segundo * tempo_restante
        volume_total += volume_restante

        self.valvula.fechar()

        self.comunicacao.enviar_mensagem("microcontrolador/to/borda", f"Status: Volume total de água na irrigação: {volume_total:.2f} litros")
        print(f"Microcontrolador informou: Status: Volume total de água na irrigação: {volume_total:.2f} litros")

        # Zerar contagem do sensor
        self.sensor.zerar_contagem()
        self.comunicacao.enviar_mensagem("microcontrolador/to/borda", "Status: Zerar contagem do volume para a próxima irrigação")
        print("Microcontrolador informou: Status: Zerar contagem do volume para a próxima irrigação")

        # Verifica se a contagem foi zerada
        volume_atual = self.sensor.obter_volume_atual()
        self.comunicacao.enviar_mensagem("microcontrolador/to/borda", f"Status: Volume zerado: {volume_atual:.2f} litros de água")
        print(f"Microcontrolador informou: Status: Volume zerado: {volume_atual:.2f} litros de água")

        self.comunicacao.enviar_mensagem("microcontrolador/to/borda", "Status: Válvula desligada")
        print("Microcontrolador informou: Status: Válvula desligada")

        proximo_acionamento = time.time() + intervalo * 3600
        while time.time() < proximo_acionamento:
            tempo_restante = proximo_acionamento - time.time()
            horas_restantes = int(tempo_restante // 3600)
            minutos_restantes = int((tempo_restante % 3600) // 60)
            segundos_restantes = int(tempo_restante % 60)
            self.comunicacao.enviar_mensagem("microcontrolador/to/borda", f"Status: Próximo acionamento em {horas_restantes:02d}:{minutos_restantes:02d}:{segundos_restantes:02d}")
            print(f"Microcontrolador informou: Status: Próximo acionamento em {horas_restantes:02d}:{minutos_restantes:02d}:{segundos_restantes:02d}")
            time.sleep(600)  # Publicar a cada 10 minutos

    def processar_mensagem(self, client, userdata, message):
        mensagem_recebida = message.payload.decode()
        print(f"Microcontrolador recebeu: {mensagem_recebida}")

        if "Ciclo:" in mensagem_recebida:
            ciclo_total = int(mensagem_recebida.split("Ciclo:")[1].split(";")[0])
            tempo_acionamento = float(mensagem_recebida.split(";Tempo:")[1].split(";")[0])
            intervalo = float(mensagem_recebida.split(";Intervalo:")[1])
            print(f"Ciclo total da cultura: {ciclo_total} dias")
            print(f"Tempo de acionamento recomendado: {tempo_acionamento:.2f} minutos")
            print(f"Intervalo entre as irrigações recomendado: {intervalo:.2f} horas")

            self.valvula.abrir()
            self.sensor.iniciar_medicao()
            self.publicar_volume = True
            threading.Thread(target=self.publicar_volume_periodicamente, args=(tempo_acionamento, intervalo)).start()
