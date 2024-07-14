import paho.mqtt.client as mqtt

class ComunicacaoMQTT:
    def __init__(self, broker, client_id):
        self.client = mqtt.Client(client_id)
        self.broker = broker
        self.on_message_callback = None

    def conectar(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        try:
            self.client.connect(self.broker)
            self.client.loop_start()
        except Exception as e:
            print(f"Erro ao conectar ao broker: {e}")

    def enviar_mensagem(self, topico, mensagem):
        try:
            self.client.publish(topico, mensagem)
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")

    def inscrever(self, topico, callback):
        self.on_message_callback = callback
        self.client.subscribe(topico)
        self.client.message_callback_add(topico, callback)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Microcontrolador conectado ao broker!")
            client.subscribe("borda/to/microcontrolador")
            client.publish("microcontrolador/to/borda", "Microcontrolador conectado!")
            print("Microcontrolador informou: Microcontrolador conectado!")
        else:
            print(f"Falha na conexão do Microcontrolador. Código de retorno: {rc}")

    def on_message(self, client, userdata, message):
        if self.on_message_callback:
            self.on_message_callback(client, userdata, message)
