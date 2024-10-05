
// Bibliotecas
#include <WiFi.h>
#include <HTTPClient.h>
#include "DHT.h"

// Pinos
#define DHTPIN 4        // Pino conectado ao DHT11 (4, neste caso)
#define DHTTYPE DHT11   // Tipo do sensor DHT

DHT dht(DHTPIN, DHTTYPE);

// Credenciais WiFi
// Credenciais WiFi
const char* ssid = "kevinwduran"; 
const char* password = "crqutczumt956r8";
// const char* ssid = "ALHN-E1B0"; 
// const char* password = "WC8f4s-mAx";

// URL do servidor Flask
const char* serverName = "http://http:/192.168.170.28:5000/api/enviar_dados"; // Alterar para o IP do seu servidor Flask
// const char* serverName = "http://http://192.168.1.11:5000/api/enviar_dados";


void setup() {
  Serial.begin(9600);
  
  // Conectando ao WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Conectando ao WiFi...");
  }
  Serial.println("Conectado ao WiFi.");

  dht.begin();
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    // Fazendo leitura dos dados
    float temperatura = dht.readTemperature();
    float umidade = dht.readHumidity();

    if (isnan(temperatura) || isnan(umidade)) {
      Serial.println("Falha ao ler o sensor DHT!");
    } else {
      // Prepara os dados em formato JSON
      String jsonData = "{\"temperatura\":" + String(temperatura) + ",\"umidade\":" + String(umidade) + "}";
      
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

  // Aguarda 10 segundos antes de enviar novos dados
  delay(10000);
}
