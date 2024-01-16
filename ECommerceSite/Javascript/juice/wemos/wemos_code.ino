#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>

// Replace these with your WiFi credentials
const char* ssid = "your_wifi_ssid";
const char* password = "your_wifi_password";

const char* serverUrl = "http://192.168.1.100:3000/api/add-to-cart";//Replace 192.168.1.100 with the actual IP address of your server and 3000 with the port your server is listening on.

void setup() {
  Serial.begin(115200);
  connectToWiFi();
}

void loop() {
  // Your main code here
}

void connectToWiFi() {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
}

void sendDataToServer(int juiceId, int quantity) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    // Construct the URL with parameters
    String url = serverUrl;
    url += "?juiceId=";
    url += String(juiceId);
    url += "&quantity=";
    url += String(quantity);

    // Use WiFiClient instead of the obsolete method
    WiFiClient client;
    http.begin(client, url);

    int httpResponseCode = http.GET();
    
    if (httpResponseCode == 200) {
      Serial.println("Data sent successfully");
    } else {
      Serial.print("Error in sending data. HTTP Response code: ");
      Serial.println(httpResponseCode);
    }

    http.end();
  } else {
    Serial.println("Not connected to WiFi");
  }
}
