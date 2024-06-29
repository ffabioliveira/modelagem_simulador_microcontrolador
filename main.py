# main_maquina2.py
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
            client.publish("maquina2/to/maquina1", f"Volume atual: {volume_atual:.2f}")
        time.sleep(1)

def on_message(client, userdata, message):
    mensagem_recebida = message.payload.decode()
    print(f"Máquina 2 recebeu: {mensagem_recebida}")

    if mensagem_recebida == "Ligar válvula":
        valvula.abrir()
        sensor.iniciar_medicao()
        mensagem_resposta = "Confirmação: Válvula foi ligada com sucesso."
    elif mensagem_recebida == "Desligar válvula":
        valvula.fechar()
        volume_total = sensor.parar_medicao()
        sensor.zerar_contagem()
        mensagem_resposta = f"Confirmação: Válvula foi desligada com sucesso. Volume total consumido: {volume_total:.2f} litros."
    else:
        mensagem_resposta = f"Aviso: Mensagem desconhecida recebida ({mensagem_recebida})."

    client.publish("maquina2/to/maquina1", mensagem_resposta)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Máquina 2 conectada ao broker!")
        client.subscribe("maquina1/to/maquina2")
    else:
        print(f"Falha na conexão da Máquina 2. Código de retorno: {rc}")

def on_publish(client, userdata, mid):
    pass  # Removendo a impressão do ID da publicação

if __name__ == '__main__':
    broker = '10.0.0.117'
    client = mqtt.Client("maquina2")

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_publish = on_publish

    print("Conectando Máquina 2 ao broker...")
    client.connect(broker)

    # Inicia thread para publicar volume periodicamente
    thread = threading.Thread(target=publicar_volume_periodicamente, args=(client,))
    thread.daemon = True
    thread.start()

    client.loop_forever()
