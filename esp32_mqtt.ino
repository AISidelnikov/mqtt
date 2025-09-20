#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT11.h>

#define DHT11_PIN    33
#define PHOTORES_PIN 32

const char* ssid = "TP-Link_D6BC";
const char* password = "78GkRR59";
const char* mqtt_server = "192.168.0.103";
WiFiClient espClient;
PubSubClient client(espClient);

#define HUMIDITY_TOPIC       "dht11/humiditi"
#define TEMPERATURE_TOPIC    "dht11/temperature"
#define ILLUMINANCE_TOPIC    "photores/illuminance"
#define MYPY_TOPIC           "python/mypy"

long lastMsg = 0;
char msg[20];

DHT11 dht11(DHT11_PIN);

void receivedCallback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message received: ");
  Serial.println(topic);

  Serial.print("payload: ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}

void mqttconnect() {
  while (!client.connected()) {
    Serial.print("MQTT connecting ...");
    String clientId = "ESP32Client";
    String user = "esp32";
    String pass = "3333";
    if (client.connect(clientId.c_str(), user.c_str(), pass.c_str())) {
      Serial.println("connected");
      client.subscribe(MYPY_TOPIC);
    } else {
      Serial.print("failed, status code =");
      Serial.print(client.state());
      Serial.println("try again in 5 seconds");

      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);

  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.setSleep(false); // Отключаем sleep для стабильности
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  client.setServer(mqtt_server, 1883);
  client.setCallback(receivedCallback);
  client.setKeepAlive(60);     // Увеличиваем keepalive
  client.setBufferSize(2048); // Увеличиваем буфер
}
void loop() {
  if (!client.connected()) {
    mqttconnect();
    client.publish(HUMIDITY_TOPIC, "start");
    client.publish(TEMPERATURE_TOPIC, "start");
    client.publish(ILLUMINANCE_TOPIC, "start");
  }
  client.loop();
  long now = millis();
  if (now - lastMsg > 10000) {
    lastMsg = now;
    int humidity = 0;
    int temperature = 0;
    int result = dht11.readTemperatureHumidity(temperature, humidity);
    
    snprintf (msg, 20, "%d %%", humidity);
    Serial.print("Humidity: ");
    Serial.println(msg);
    client.publish(HUMIDITY_TOPIC, msg);
    
    snprintf (msg, 20, "%d C", temperature);
    Serial.print("Temperature: ");
    Serial.println(msg);
    client.publish(TEMPERATURE_TOPIC, msg);
    
    int analogValue = analogRead(PHOTORES_PIN);
    float voltage = analogValue * (3.3 / 4095.0);
    float resistance = (10000.0 * (3.3 - voltage)) / voltage;
    float illuminance = 1000000.0 / resistance;
    snprintf (msg, 20, "%fl lux", illuminance);
    Serial.print("Illuminance: ");
    Serial.println(msg);
    client.publish(ILLUMINANCE_TOPIC, msg);
  }
}