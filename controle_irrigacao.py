import threading
import time
import json
from sensor_vazao import SensorVazao
from valvula_solenoid import ValvulaSolenoid

class ControleIrrigacao:
    def __init__(self, comunicacao):
        self.comunicacao = comunicacao
        self.vazao_litros_por_segundo = 1.0 / 15  # 1 litro a cada 15 segundos
        self.sensor = SensorVazao(self.vazao_litros_por_segundo)
        self.valvula = ValvulaSolenoid()
        self.publicar_volume = False
        self.valvula_aberta = False

    def processar_mensagem(self, client, userdata, message):
        mensagem_recebida = message.payload.decode()
        print(f"Microcontrolador recebeu: {mensagem_recebida}")

        try:
            dados = json.loads(mensagem_recebida)
            # Se for um dicionário de dados ambientais
            if 'fase_desenvolvimento' in dados:
                self.atualizar_dados_ambientais(dados)
            elif 'acao' in dados:
                acao = dados['acao']
                if acao == "ligar_valvula":
                    self.ligar_valvula()
                elif acao == "desligar_valvula":
                    self.desligar_valvula()
        except json.JSONDecodeError:
            # Se não for JSON, trata como texto simples
            if mensagem_recebida == "ligar_valvula":
                self.ligar_valvula()
            elif mensagem_recebida == "desligar_valvula":
                self.desligar_valvula()
            else:
                print(f"Mensagem não reconhecida: {mensagem_recebida}")

    def ligar_valvula(self):
        if not self.valvula_aberta:
            self.valvula.abrir()
            self.sensor.iniciar_medicao()
            self.publicar_volume = True
            self.valvula_aberta = True
            threading.Thread(target=self.monitorar_acao).start()
            self.comunicacao.enviar_mensagem("microcontrolador/to/borda", "Status: Válvula ligada")
        else:
            print("A válvula já está aberta.")

    def desligar_valvula(self):
        if self.valvula_aberta:
            volume_total = self.sensor.obter_volume_atual()
            self.valvula.fechar()
            self.comunicacao.enviar_mensagem("microcontrolador/to/borda", f"Status: Volume total: {volume_total:.2f} litros")
            self.sensor.zerar_contagem()
            self.comunicacao.enviar_mensagem("microcontrolador/to/borda", "Status: Zerar contagem de volume")
            self.comunicacao.enviar_mensagem("microcontrolador/to/borda", "Status: Válvula desligada")
            self.publicar_volume = False
            self.valvula_aberta = False
        else:
            print("A válvula já está fechada.")

    def atualizar_dados_ambientais(self, dados):
        # Processar e armazenar os dados ambientais recebidos
        print("Dados ambientais recebidos:")
        print(f"  Fase de Desenvolvimento: {dados['fase_desenvolvimento']}")
        print(f"  Textura do Solo: {dados['textura_solo']}%")
        print(f"  Evapotranspiração: {dados['evapotranspiracao']} mm")
        print(f"  Precipitação: {dados['precipitacao']} mm")
        # Aqui você pode adicionar lógica para usar esses dados conforme necessário

    def monitorar_acao(self):
        while self.publicar_volume:
            time.sleep(10)
            # Adicione aqui a lógica para publicar o volume, se necessário
