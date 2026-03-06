# Configuración ESP32 para API Flask RFID

## Pasos de Configuración

### 1. **Obtén la IP de tu servidor**
En PowerShell, ejecuta:
```powershell
ipconfig
```
Busca "IPv4 Address" (algo como `192.168.1.100` o `10.0.0.X`)

### 2. **Modifica el código ESP32**
Abre `ESP32_RFID_Client.ino` y cambia:

```cpp
const char* ssid = "Steren_COM-865+";        // Tu red WiFi
const char* password = "Grupoindsaavedra081125";    // Tu contraseña
const char* serverIP = "192.168.1.81";         // Tu IP del servidor
```

### 3. **Instala librerías en Arduino IDE**
Ve a: **Sketch → Include Library → Manage Libraries** y busca:
- **ArduinoJson** (by Benoit Blanchon)
- **HTTPClient** (generalmente incluida)

### 4. **Sube el código a tu ESP32**
1. Selecciona: **Tools → Board → ESP32 Dev Module**
2. Selecciona el puerto COM correcto
3. Click en **Upload** (flecha derecha)

### 5. **Verifica la conexión**
1. Abre **Tools → Serial Monitor** (velocidad: 115200)
2. Deberías ver:
   ```
   Conectando a Wi-Fi: TU_RED
   .......
   ✓ Conectado a Wi-Fi
   IP: 192.168.1.XX
   ```

### 6. **Prototesta enviando datos**
En la consola de Arduino IDE, si tienes un RFID RC522, deberá leer la tarjeta y enviarla automaticamente. 

**Para testear sin RFID:**
Descomenta esta línea en `readRFID()` (alrededor de la línea 130):
```cpp
return "1A2B3C4D";  // UID de prueba
```

### 7. **Verifica en tu API Flask**
1. Asegúrate de que tu Flask está corriendo:
   ```powershell
   python -m app.main
   ```

2. En otra terminal, abre `http://localhost:5000`

3. Ve a **Leer Tarjeta** y deberías ver los datos que envía el ESP32

---

## Problemas Comunes

| Problema | Solución |
|----------|----------|
| **"No se conecta a WiFi"** | Verifica SSID y contraseña exactamente iguales (mayúsculas/minúsculas) |
| **"Error en conexión al servidor"** | Verifica que la IP sea correcta con `ipconfig`. Ambos dispositivos deben estar en la misma red |
| **"Conexión rechazada (refused)"** | Asegúrate que Flask esté ejecutándose en `0.0.0.0:5000` |
| **Puerto 5000 en uso** | Cambia en `app/main.py:134` a otro puerto: `app.run(host='0.0.0.0', port=5001, debug=True)` |
| **No hay respuesta del servidor** | Navega a `http://IP:5000/cards` en tu navegador para verificar que la API trabaja |

---

## Esquema de Datos

### **Enviar tarjeta leída a `/read_rfid`:**
```json
POST /read_rfid
{
  "card_uid": "1A2B3C4D"
}
```

**Respuesta:**
```json
{
  "found": True,
  "card": {
    "id": 1,
    "card_uid": "1A2B3C4D",
    "owner": "Juan",
    "areas": "Oficina,Almacén",
    "info": "Acceso VIP",
    "created_at": "2026-03-04T15:30:00"
  }
}
```

### **Guardar/Actualizar tarjeta en `/save_card`:**
```json
POST /save_card
{
  "card_uid": "1A2B3C4D",
  "owner": "Juan",
  "areas": "Oficina,Almacén",
  "info": "Acceso VIP"
}
```

---

## Usando RC522 RFID

Si tienes un módulo **RC522**, descomenta estas líneas en el archivo `.ino`:

```cpp
// Descomentar estas líneas:
#include <MFRC522.h>
#define SS_PIN 5        // Pin CS del ESP32
#define RST_PIN 17      // Pin RES del ESP32
MFRC522 rfid(SS_PIN, RST_PIN);

// En setup():
SPI.begin();
rfid.PCD_Init();

// En readRFID():
if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
  String uid = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    uid += String(rfid.uid.uidByte[i], HEX);
  }
  return uid;
}
```

**Conexiones RC522 a ESP32:**
```
RC522 -> ESP32
SDA   -> GPIO 5
SCK   -> GPIO 18
MOSI  -> GPIO 23
MISO  -> GPIO 19
GND   -> GND
3.3V  -> 3.3V
RST   -> GPIO 17
IRQ   -> (no conectar)
```

