import paho.mqtt.client as mqtt
from sensor_vazao import SensorVazao, ValvulaSolenoid
import threading
import time

# Configuração do sensor e válvula (substitua pelos valores reais)
vazao_litros_por_segundo = 1.0 / 15 
sensor = SensorVazao(vazao_litros_por_segundo)
valvula = ValvulaSolenoid()

# Variável de controle para a thread de publicação
publicar_volume = False

def publicar_volume_periodicamente(client, tempo_acionamento, intervalo):
    global publicar_volume
    start_time = time.time()
    tempo_acionamento_segundos = tempo_acionamento * 60 

    while time.time() - start_time < tempo_acionamento_segundos and publicar_volume:
        if valvula.aberta:
            time.sleep(1)
            tempo_decorrido = time.time() - start_time
            volume_atual = sensor.vazao_litros_por_segundo * tempo_decorrido 
            if tempo_decorrido % 15 == 0:
                client.publish("maquina2/to/maquina1", f"Status:Volume:{volume_atual:.2f};Tempo:{tempo_decorrido:.2f}")
                print(f"Publicado: Status:Volume:{volume_atual:.2f};Tempo:{tempo_decorrido:.2f}")

    # Após o tempo de acionamento
    valvula.fechar()
    sensor.zerar_contagem()

    client.publish("maquina2/to/maquina1", "Status:Válvula desligada")
    client.publish("maquina2/to/maquina1", f"Status:Volume:{volume_atual:.2f};Tempo:{tempo_acionamento:.2f}") 
    client.publish("maquina2/to/maquina1", f"Status:Próximo acionamento:{intervalo:.2f}")
    print("Publicado: Status:Válvula desligada")
    print(f"Publicado: Status:Volume:{volume_atual:.2f};Tempo:{tempo_acionamento:.2f}")
    print(f"Publicado: Status:Próximo acionamento:{intervalo:.2f}")

def on_message(client, userdata, message):
    global publicar_volume
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

        publicar_volume = True
        threading.Thread(target=publicar_volume_periodicamente, args=(client, tempo_acionamento, intervalo)).start()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Máquina 2 conectada ao broker!")
        client.subscribe("maquina1/to/maquina2")
        client.publish("maquina2/to/maquina1", "Máquina 2 conectada!")
    else:
        print(f"Falha na conexão da Máquina 2. Código de retorno: {rc}")

if __name__ == '__main__':
    broker = '10.0.0.117'  # Substitua pelo endereço IP do seu broker MQTT
    client = mqtt.Client("maquina2")
    client.on_connect = on_connect
    client.on_message = on_message

    print("Conectando Máquina 2 ao broker...")
    client.connect(broker)

    client.loop_forever()
