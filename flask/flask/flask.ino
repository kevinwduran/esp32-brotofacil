// Bibliotecas
#include <WiFi.h>
#include <HTTPClient.h>
#include "DHT.h"

// Pinos
#define DHTPIN 4       // Pino conectado ao DHT11 (4, neste caso)
#define DHTTYPE DHT11  // Tipo do sensor DHT

DHT dht(DHTPIN, DHTTYPE);

// Credenciais WiFi
const char* ssid = "kevinwduran"; 
const char* password = "crqutczumt956r8";

// URL do servidor Flask
const char* serverName = "http://192.168.170.28:5000/api/enviar_dados";  // Atualize conforme necessário

void setup() {
  Serial.begin(9600);

  // Conectando ao WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Conectando ao WiFi...");
  }
  Serial.println("Conectado ao WiFi.");

  // Inicializa o DHT
  dht.begin();
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    // Fazendo leitura dos dados do DHT11
    float temperatura = dht.readTemperature();
    float umidade = dht.readHumidity();

    // Fazendo leitura do LDR
    int ldrValue = analogRead(35);
    int luminosidade = map(ldrValue, 0, 4095, 100, 0);  // Mapeia o valor para 0 a 100%
    
    // Fazendo leitura do sensor dde umidade do solo
    int sensorUmidadeSolo = analogRead(34);  
    int umidadesolo = map(sensorUmidadeSolo, 700, 3500, 100, 0); 

    if (umidadesolo < 0) {
      umidadesolo = 0;
    }


    if (isnan(temperatura) || isnan(umidade)) {
      Serial.println("Falha ao ler o sensor DHT!");
    } else {
      // Prepara os dados em formato JSON
      String jsonData = "{\"temperatura\":" + String(temperatura) + 
                        ",\"umidade\":" + String(umidade) +
                        ",\"luminosidade\":" + String(luminosidade) +
                        ",\"umidadesolo\":" + String(umidadesolo) + "}";

      // Envia os dados para o servidor Flask
      http.begin(serverName);
      http.addHeader("Content-Type", "application/json");
      int httpResponseCode = http.POST(jsonData);
      
      // Verifica a resposta do servidor
      if (httpResponseCode > 0) {
        String response = http.getString();
        Serial.println(httpResponseCode);
        Serial.println(response);
      } else {
        Serial.print("Erro no envio de dados. Código: ");
        Serial.println(httpResponseCode);
      }
      
      http.end();
    }
  } else {
    Serial.println("Conexão WiFi perdida.");
  }

  // Aguarda 5 segundos antes de enviar novos dados
  delay(5000);
}