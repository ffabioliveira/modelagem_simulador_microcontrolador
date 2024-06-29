import paho.mqtt.client as mqtt

class ComunicacaoMQTT:
    def __init__(self, broker, client_id):
        self.client = mqtt.Client(client_id)
        self.broker = broker

    def conectar(self):
        self.client.connect(self.broker)
        self.client.loop_start()

    def enviar_mensagem(self, topico, mensagem):
        self.client.publish(topico, mensagem)

    def inscrever(self, topico, callback):
        self.client.subscribe(topico)
        self.client.message_callback_add(topico, callback)

