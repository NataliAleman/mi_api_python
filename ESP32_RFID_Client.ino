// ESP32 RFID Reader - Cliente para API Flask
// Este código se conecta a Wi-Fi y envía datos RFID a tu servidor Flask

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ========== CONFIGURACIÓN Wi-Fi ==========
const char* ssid = "Steren_COM-865+";        // Cambia esto
const char* password = "Grupoindsaavedra081125";    // Cambia esto

// ========== CONFIGURACIÓN DEL SERVIDOR ==========
// Asegúrate de usar la misma IP que tu servidor Flask
const char* serverIP = "192.168.1.133";         // IP de tu PC/servidor (CAMBIAR si cambia)
const int serverPort = 5000;                    // Puerto Flask
// La API de Flask expone /api/rfid y espera un campo "uid" en JSON
const char* readEndpoint = "/api/rfid";
const char* saveEndpoint = "/save_card";  // no usado en este ejemplo

// ========== CONFIGURACIÓN RFID ==========
// Si usas módulo RFID RC522:
#include <MFRC522.h>
#define SS_PIN 5
#define RST_PIN 17
MFRC522 rfid(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\nIniciando ESP32 RFID Client...");
  
  // Inicializar RFID (si lo usas)
  SPI.begin();
  rfid.PCD_Init();
  
  // Conectar a Wi-Fi
  connectToWiFi();
}

void loop() {
  // Verificar conexión Wi-Fi
  if (WiFi.status() != WL_CONNECTED) {
    connectToWiFi();
  }
  
  // Ejemplo: leer UID desde RFID o simulado
  String cardUID = readRFID();  // Tu función para leer RFID
  
  if (!cardUID.isEmpty()) {
    Serial.println("UID leído: " + cardUID);
    sendToServer(cardUID);
  }
  
  delay(1000);
}

// ========== CONECTAR A Wi-Fi ==========
void connectToWiFi() {
  Serial.print("Conectando a Wi-Fi: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✓ Conectado a Wi-Fi");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n✗ Error: No se pudo conectar a Wi-Fi");
  }
}

// ========== ENVIAR TARJETA AL SERVIDOR (LECTURA) ==========
void sendToServer(String cardUID) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("No hay conexión Wi-Fi");
    return;
  }
  
  HTTPClient http;
  String url = String("http://") + serverIP + ":" + serverPort + readEndpoint;
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  
  // Crear JSON con la clave que espera Flask
  StaticJsonDocument<200> doc;
  doc["uid"] = cardUID;
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  Serial.println("Enviando a: " + url);
  Serial.println("JSON: " + jsonString);
  
  // POST request
  int httpResponseCode = http.POST(jsonString);
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.print("Respuesta del servidor (status ");
    Serial.print(httpResponseCode);
    Serial.print("): ");
    Serial.println(response);
    
    // Parsear respuesta si es JSON válido
    StaticJsonDocument<500> responseDoc;
    DeserializationError err = deserializeJson(responseDoc, response);
    if (!err && responseDoc.containsKey("found")) {
      if (responseDoc["found"]) {
        Serial.println("✓ Tarjeta encontrada!");
        Serial.println("Propietario: " + responseDoc["card"]["owner"].as<String>());
        Serial.println("Áreas: " + responseDoc["card"]["areas"].as<String>());
      } else {
        Serial.println("Tarjeta no encontrada en la base de datos");
      }
    }
  } else {
    Serial.print("✗ Error en la conexión. Código: ");
    Serial.println(httpResponseCode);
  }
  
  http.end();
}

// ========== GUARDAR TARJETA EN EL SERVIDOR ==========
void saveCardToServer(String cardUID, String owner, String areas, String info) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("No hay conexión Wi-Fi");
    return;
  }
  
  HTTPClient http;
  String url = String("http://") + serverIP + ":" + serverPort + saveEndpoint;
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  
  // Crear JSON
  StaticJsonDocument<300> doc;
  doc["card_uid"] = cardUID;
  doc["owner"] = owner;
  doc["areas"] = areas;
  doc["info"] = info;
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  Serial.println("Guardando tarjeta...");
  int httpResponseCode = http.POST(jsonString);
  
  if (httpResponseCode == 200) {
    Serial.println("✓ Tarjeta guardada exitosamente");
  } else {
    Serial.print("✗ Error guardando tarjeta. Código: ");
    Serial.println(httpResponseCode);
  }
  
  http.end();
}

// ========== LEER RFID ==========
// REEMPLAZA ESTA FUNCIÓN CON TU CÓDIGO DE LECTURA RFID REAL
String readRFID() {
  // Ejemplo con RC522:
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    String uid = "";
    for (byte i = 0; i < rfid.uid.size; i++) {
      uid += String(rfid.uid.uidByte[i], HEX);
    }
    return uid;
  }
  
  // Para pruebas (simular tarjeta):
  // Descomenta esta línea para enviar un UID de prueba
  // return "1A2B3C4D";
  
  return "";  // Sin tarjeta leída
}
