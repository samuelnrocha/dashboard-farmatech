import paho.mqtt.client as mqtt
import json
import time
import random
import threading
from datetime import datetime

class IOTService:
    def __init__(self, broker="broker.hivemq.com", port=1883, topic="farmtech/sensores"):
        self.broker = broker
        self.port = port
        self.topic = topic
        
        # Histórico de leituras (últimas 50)
        self.history = []
        self.max_history = 50
        
        # Status atual
        self.latest_data = {
            "temperatura": 24.5,
            "umidade": 55.0,
            "luminosidade": 650,
            "bomba_ativa": False,
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
        
        self.lock = threading.Lock()
        self.client = None
        self.connected = False
        self.limiar_umidade = 50.0  # Limiar padrão
        
        # Configurar cliente MQTT (v2.x compatível)
        try:
            self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_message = self.on_message
            
            # Tentar iniciar conexão em segundo plano
            threading.Thread(target=self._connect_and_loop, daemon=True).start()
        except Exception as e:
            print(f"[MQTT] Erro ao instanciar cliente MQTT: {e}")

    def _connect_and_loop(self):
        try:
            print(f"[MQTT] Conectando ao broker {self.broker}:{self.port}...")
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
        except Exception as e:
            print(f"[MQTT] Falha na conexão inicial: {e}")

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print(f"[MQTT] Conectado com sucesso ao broker {self.broker}")
            self.connected = True
            client.subscribe(self.topic)
            print(f"[MQTT] Inscrito no tópico: {self.topic}")
        else:
            print(f"[MQTT] Falha na conexão. Código: {reason_code}")
            self.connected = False

    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        print(f"[MQTT] Desconectado do broker. Código: {reason_code}")
        self.connected = False

    def on_message(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            temp = float(payload.get("temperatura", 25.0))
            umid = float(payload.get("umidade", 50.0))
            lumi = int(payload.get("luminosidade", 500))
            
            self.update_sensor_data(temp, umid, lumi)
        except Exception as e:
            print(f"[MQTT] Erro ao processar mensagem recebida: {e}")

    def update_sensor_data(self, temperatura, umidade, luminosidade):
        with self.lock:
            # Regra de negócio para a bomba:
            # Se a umidade for menor que o limiar definido, a bomba é ligada.
            # Se for maior ou igual ao limiar, a bomba é desligada.
            bomba_ativa = umidade < self.limiar_umidade
            
            self.latest_data = {
                "temperatura": round(temperatura, 1),
                "umidade": round(umidade, 1),
                "luminosidade": int(luminosidade),
                "bomba_ativa": bomba_ativa,
                "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
            
            # Adicionar ao histórico
            self.history.append(self.latest_data.copy())
            if len(self.history) > self.max_history:
                self.history.pop(0)

    def set_limiar_umidade(self, valor):
        with self.lock:
            self.limiar_umidade = valor
            # Reavaliar status da bomba imediatamente
            self.latest_data["bomba_ativa"] = self.latest_data["umidade"] < valor

    def get_latest_data(self):
        with self.lock:
            return self.latest_data.copy()

    def get_history(self):
        with self.lock:
            return list(self.history)

    def publish_data(self, temperatura, umidade, luminosidade):
        """Publica dados simulados ou manuais no broker MQTT."""
        if not self.client or not self.connected:
            # Se estiver desconectado, atualizamos localmente de imediato
            self.update_sensor_data(temperatura, umidade, luminosidade)
            return False
            
        payload = {
            "temperatura": round(temperatura, 1),
            "umidade": round(umidade, 1),
            "luminosidade": int(luminosidade)
        }
        
        try:
            info = self.client.publish(self.topic, json.dumps(payload))
            # Garante que seja publicado mesmo se localmente demorar a receber
            info.wait_for_publish(timeout=1.0)
            return True
        except Exception as e:
            print(f"[MQTT] Erro ao publicar: {e}")
            # Em caso de falha física, atualiza localmente como fallback
            self.update_sensor_data(temperatura, umidade, luminosidade)
            return False

    def simulate_step(self):
        """Gera uma variação realista a partir do último estado e publica."""
        latest = self.get_latest_data()
        
        # Variações pequenas e realistas
        d_temp = random.uniform(-0.5, 0.5)
        d_umid = random.uniform(-1.5, 1.5)
        d_lumi = random.randint(-25, 25)
        
        new_temp = max(15.0, min(45.0, latest["temperatura"] + d_temp))
        
        # Se a bomba estiver ligada, a umidade tende a subir
        if latest["bomba_ativa"]:
            new_umid = max(0.0, min(100.0, latest["umidade"] + random.uniform(1.0, 3.0)))
        else:
            new_umid = max(0.0, min(100.0, latest["umidade"] + d_umid))
            
        new_lumi = max(10, min(1200, latest["luminosidade"] + d_lumi))
        
        self.publish_data(new_temp, new_umid, new_lumi)
