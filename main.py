import paho.mqtt.client as mqtt
from sensor_vazao import SensorVazao, ValvulaSolenoid
import threading
import time

# Configuração do sensor e válvula
vazao_litros_por_segundo = 1.0 / 15  # 1 litro em 15 segundos
sensor = SensorVazao(vazao_litros_por_segundo)
valvula = ValvulaSolenoid()

def publicar_volume_periodicamente(client):
    while True:
        if valvula.aberta:
            volume_atual = sensor.obter_volume_atual()
            tempo_decorrido = sensor.tempo_decorrido()
            client.publish("maquina2/to/maquina1", f"Status:Volume:{volume_atual:.2f};Tempo:{tempo_decorrido:.2f}")
            print(f"Publicado: Status:Volume:{volume_atual:.2f};Tempo:{tempo_decorrido:.2f}")
        time.sleep(60)  # Envia informações a cada minuto

def on_message(client, userdata, message):
    mensagem_recebida = message.payload.decode()
    print(f"Máquina 2 recebeu: {mensagem_recebida}")

    if "Ciclo:" in mensagem_recebida:
        ciclo_total = int(mensagem_recebida.split("Ciclo:")[1].split(";")[0])
        tempo_acionamento = float(mensagem_recebida.split(";Tempo:")[1].split(";")[0])
        intervalo = float(mensagem_recebida.split(";Intervalo:")[1])
        print(f"Ciclo total da cultura: {ciclo_total} dias")
        print(f"Tempo de acionamento recomendado: {tempo_acionamento:.2f} minutos")
        print(f"Intervalo entre as irrigações recomendado: {intervalo:.2f} horas")

        valvula.abrir()
        sensor.iniciar_medicao()
        client.publish("maquina2/to/maquina1", "Status:Válvula ligada;Volume:0;Tempo:0") 
        print("Publicado: Status:Válvula ligada;Volume:0;Tempo:0") 

        start_time = time.time()
        while time.time() - start_time < tempo_acionamento * 60:
            time.sleep(1)

        valvula.fechar()
        volume_total = sensor.obter_volume_atual()
        sensor.zerar_contagem()

        client.publish("maquina2/to/maquina1", "Status:Válvula desligada")
        client.publish("maquina2/to/maquina1", f"Status:Volume:{volume_total:.2f};Tempo:{tempo_acionamento:.2f}")
        client.publish("maquina2/to/maquina1", f"Status:Próximo acionamento:{intervalo:.2f}")
        print("Publicado: Status:Válvula desligada")
        print(f"Publicado: Status:Volume:{volume_total:.2f};Tempo:{tempo_acionamento:.2f}")
        print(f"Publicado: Status:Próximo acionamento:{intervalo:.2f}")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Máquina 2 conectada ao broker!")
        client.subscribe("maquina1/to/maquina2")
        client.publish("maquina2/to/maquina1", "Máquina 2 conectada!")  # Publica apenas uma vez
    else:
        print(f"Falha na conexão da Máquina 2. Código de retorno: {rc}")

if __name__ == '__main__':
    broker = '10.0.0.117'  # Endereço IP do broker MQTT
    client = mqtt.Client("maquina2")
    client.on_connect = on_connect
    client.on_message = on_message

    print("Conectando Máquina 2 ao broker...")
    client.connect(broker)

    # Inicia thread para publicar volume periodicamente
    thread = threading.Thread(target=publicar_volume_periodicamente, args=(client,))
    thread.daemon = True
    thread.start()

    client.loop_forever()
