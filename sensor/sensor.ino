#include "DHT.h"
#include "WiFiEsp.h" 
#include "SoftwareSerial.h"
#include "ArduinoHttpClient.h"

// https://github.com/bportaluri/WiFiEsp/issues/50


#define DHTPIN 6 
#define DHTTYPE DHT11 

DHT dht(DHTPIN, DHTTYPE);
 
SoftwareSerial Serial1(2, 3); 
 
char ssid[] = ""; 
char pass[] = "";
 
int status = WL_IDLE_STATUS; 
/*
STATUS TEMPORÁRIO ATRIBUÍDO QUANDO O WIFI É INICIALIZADO E PERMANECE ATIVO
ATÉ QUE O NÚMERO DE TENTATIVAS EXPIRE (RESULTANDO EM WL_NO_SHIELD) OU QUE UMA CONEXÃO SEJA ESTABELECIDA
(RESULTANDO EM WL_CONNECTED)
*/

char server[] = "192.168.15.25"; 
char port[] = "8000";

RingBuffer buf(8); 
 
WiFiEspClient client;
//HttpClient http = HttpClient(client, server, port);


void setup(){
  Serial.begin(9600); 
  Serial1.begin(9600); 
  WiFi.init(&Serial1); 
 
  
 }
 
void loop(){
  
  // A leitura da temperatura e umidade pode levar 250ms!
  // O atraso do sensor pode chegar a 2 segundos.
  float h = dht.readHumidity();
  float t = dht.readTemperature(); 


  if(WiFi.status() == WL_NO_SHIELD){
    while (true);
  }
  while(status != WL_CONNECTED){
    status = WiFi.begin(ssid, pass);
  }   
  Serial.println("DHTxx test!");
  dht.begin();

  Serial.println("You're connected to the network");
  
  printWifiStatus();
    if (client.connect(server, 8000)) {
    Serial.println("Connected to server");
    String content = "{\"device_id\":5,\"temperature\":"+String(t)+",\"humidity\":"+String(h)+",\"lat\":22,\"lon\":40}";
    Serial.println(content);
    Serial.println("Making POST Request...");
    client.println("POST /insert_data/ HTTP/1.1");
    client.println("User-Agent: Arduino/1.0");
    client.println("accept: application/json");
    client.println("Content-Length: " + String(content.length()+2));
    client.println("Content-Type: application/json");
    client.println();
    client.println(content);
     delay(5000);
    client.stop();


    }


}
 

void printWifiStatus()
{
  // print the SSID of the network you're attached to
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your WiFi shield's IP address
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print the received signal strength
  long rssi = WiFi.RSSI();
  Serial.print("Signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}