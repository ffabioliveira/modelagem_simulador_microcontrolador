import paho.mqtt.client as mqtt
from sensor_vazao import SensorVazao, ValvulaSolenoid
import threading
import time

vazao_litros_por_segundo = 1.0 / 15  # 1 litro a cada 15 segundos
sensor = SensorVazao(vazao_litros_por_segundo)
valvula = ValvulaSolenoid()

publicar_volume = False

def publicar_volume_periodicamente(client, tempo_acionamento, intervalo):
    global publicar_volume
    start_time = time.time()
    tempo_acionamento_segundos = tempo_acionamento * 60
    proxima_publicacao = time.time() + 60

    client.publish("microcontrolador/to/borda", "Status: Válvula ligada")
    print("Microcontrolador informou: Status: Válvula ligada")

    while time.time() - start_time < tempo_acionamento_segundos and publicar_volume:
        if valvula.aberta:
            volume_total = sensor.obter_volume_atual()
            if time.time() >= proxima_publicacao:
                client.publish("microcontrolador/to/borda", f"Status: Volume parcial: {volume_total:.2f} litros de água")
                print(f"Microcontrolador informou: Status: Volume parcial: {volume_total:.2f} litros de água")
                proxima_publicacao = time.time() + 60
            time.sleep(1)

    # Calcular o volume dos segundos restantes
    tempo_restante = tempo_acionamento_segundos - (time.time() - start_time)
    volume_restante = sensor.vazao_litros_por_segundo * tempo_restante
    volume_total += volume_restante

    valvula.fechar()

    client.publish("microcontrolador/to/borda", f"Status: Volume total de água na irrigação: {volume_total:.2f} litros")
    print(f"Microcontrolador informou: Status: Volume total de água na irrigação: {volume_total:.2f} litros")

    # Zerar contagem do sensor
    sensor.zerar_contagem()
    client.publish("microcontrolador/to/borda", "Status: Zerar contagem do volume para a próxima irrigação")
    print("Microcontrolador informou: Status: Zerar contagem do volume para a próxima irrigação")

    # Verifica se a contagem foi zerada
    volume_atual = sensor.obter_volume_atual()
    client.publish("microcontrolador/to/borda", f"Status: Volume zerado: {volume_atual:.2f} litros de água")
    print(f"Microcontrolador informou: Status: Volume zerado: {volume_atual:.2f} litros de água")

    client.publish("microcontrolador/to/borda", "Status: Válvula desligada")
    print("Microcontrolador informou: Status: Válvula desligada")

    proximo_acionamento = time.time() + intervalo * 3600
    horas_restantes = int(intervalo)
    minutos_restantes = int((intervalo - horas_restantes) * 60)
    client.publish("microcontrolador/to/borda", f"Status: Próximo acionamento em {horas_restantes:02d}:{minutos_restantes:02d}")
    print(f"Microcontrolador informou: Status: Próximo acionamento em {horas_restantes:02d}:{minutos_restantes:02d}")

    proxima_mensagem_desligada = time.time() + 600
    while time.time() < proximo_acionamento:
        tempo_restante = proximo_acionamento - time.time()
        if time.time() >= proxima_mensagem_desligada:
            horas_restantes = int(tempo_restante // 3600)
            minutos_restantes = int((tempo_restante % 3600) // 60)
            client.publish("microcontrolador/to/borda", f"Status: Próximo acionamento em {horas_restantes:02d}:{minutos_restantes:02d}")
            print(f"Microcontrolador informou: Status: Próximo acionamento em {horas_restantes:02d}:{minutos_restantes:02d}")
            proxima_mensagem_desligada = time.time() + 600
        time.sleep(60)

def on_message(client, userdata, message):
    global publicar_volume
    mensagem_recebida = message.payload.decode()
    print(f"Microcontrolador recebeu: {mensagem_recebida}")

    if "Ciclo:" in mensagem_recebida:
        ciclo_total = int(mensagem_recebida.split("Ciclo:")[1].split(";")[0])
        tempo_acionamento = float(mensagem_recebida.split(";Tempo:")[1].split(";")[0])
        intervalo = float(mensagem_recebida.split(";Intervalo:")[1])
        print(f"Ciclo total da cultura: {ciclo_total} dias")
        print(f"Tempo de acionamento recomendado: {tempo_acionamento:.2f} minutos")
        print(f"Intervalo entre as irrigações recomendado: {intervalo:.2f} horas")

        valvula.abrir()
        sensor.iniciar_medicao()
        publicar_volume = True
        threading.Thread(target=publicar_volume_periodicamente, args=(client, tempo_acionamento, intervalo)).start()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Microcontrolador conectado ao broker!")
        client.subscribe("borda/to/microcontrolador")
        client.publish("microcontrolador/to/borda", "Microcontrolador conectado!")
        print("Microcontrolador informou: Microcontrolador conectado!")
    else:
        print(f"Falha na conexão do Microcontrolador. Código de retorno: {rc}")

if __name__ == '__main__':
    broker = '10.0.0.117'
    client = mqtt.Client("microcontrolador")
    client.on_connect = on_connect
    client.on_message = on_message

    print("Conectando Microcontrolador ao broker...")
    client.connect(broker)

    client.loop_forever()
