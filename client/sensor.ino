#include "DHT.h"
#include "WiFiEsp.h" //INCLUSÃO DA BIBLIOTECA
#include "SoftwareSerial.h"//INCLUSÃO DA BIBLIOTECA
#include "ArduinoHttpClient.h"

// https://github.com/bportaluri/WiFiEsp/issues/50


#define DHTPIN 6 // pino que estamos conectado
#define DHTTYPE DHT11 // DHT 11

DHT dht(DHTPIN, DHTTYPE);
 
SoftwareSerial Serial1(2, 3); //PINOS QUE EMULAM A SERIAL, ONDE O PINO 2 É O RX E O PINO 3 É O TX
 
char ssid[] = "OLIVEIRA-2G"; //VARIÁVEL QUE ARMAZENA O NOME DA REDE SEM FIO
char pass[] = "55265236";//VARIÁVEL QUE ARMAZENA A SENHA DA REDE SEM FIO
 
int status = WL_IDLE_STATUS; //STATUS TEMPORÁRIO ATRIBUÍDO QUANDO O WIFI É INICIALIZADO E PERMANECE ATIVO
//ATÉ QUE O NÚMERO DE TENTATIVAS EXPIRE (RESULTANDO EM WL_NO_SHIELD) OU QUE UMA CONEXÃO SEJA ESTABELECIDA
//(RESULTANDO EM WL_CONNECTED)

char server[] = "192.168.15.25"; //CONEXÃO REALIZADA NA PORTA 80
char port[] = "8000";

RingBuffer buf(8); //BUFFER PARA AUMENTAR A VELOCIDADE E REDUZIR A ALOCAÇÃO DE MEMÓRIA
 
WiFiEspClient client;
//HttpClient http = HttpClient(client, server, port);


void setup(){
  Serial.begin(9600); //INICIALIZA A SERIAL
  Serial1.begin(9600); //INICIALIZA A SERIAL PARA O ESP8266
  WiFi.init(&Serial1); //INICIALIZA A COMUNICAÇÃO SERIAL COM O ESP8266
 
  //INÍCIO - VERIFICA SE O ESP8266 ESTÁ CONECTADO AO ARDUINO, CONECTA A REDE SEM FIO E INICIA O WEBSERVER
  
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

//  // testa se retorno é valido, caso contrário algo está errado.
//  if (isnan(t) || isnan(h)) 
//  {
//    Serial.println("Failed to read from DHT");
//  }else{
//  if (client.connect(server, 8000)) {
//    Serial.println("Connected to server");
//    String content = "{\"device_id\":5,\"temperature\":25,\"humidity\":30,\"lat\":22,\"lon\":40}";
//    Serial.println("Making POST Request...");
//    client.println("POST /insert_data/ HTTP/1.1");
//    client.println("User-Agent: Arduino/1.0");
//    client.println("Accept: */*");
//    client.println("Content-Length: " + content.length());
//    client.println("Content-Type: application/json");
//    client.println();
//    client.println(content);
//    client.println("Connection: close");
//    }


    
//    String postData = "{\"device_id\":\"5\",\"temperature\":\"25\",\"humidity\":\"30\",\"lat\":\"22\",\"lon\":\"40\"}";
//    http.beginRequest();
//    http.post("/insert_data");
//    http.sendHeader("Content-Type", "application/json");
//    http.sendHeader("Content-Length", postData.length());
//    http.beginBody();
//    http.print(postData);
//    http.endRequest();
//    delay(5000);
//
//  }




}
 
//MÉTODO DE RESPOSTA A REQUISIÇÃO HTTP DO CLIENTE
//void sendHttpResponse(WiFiEspClient client,int t ,int h ){
//  client.println("HTTP/1.1 200 OK"); //ESCREVE PARA O CLIENTE A VERSÃO DO HTTP
//  client.println("Content-Type: text/html"); //ESCREVE PARA O CLIENTE O TIPO DE CONTEÚDO(texto/html)
//  client.println("");
//  client.println("<!DOCTYPE HTML>"); //INFORMA AO NAVEGADOR A ESPECIFICAÇÃO DO HTML
//  client.println("<html>"); //ABRE A TAG "html"
//  client.println("<head>"); //ABRE A TAG "head"
//  client.println("<title>SENSOR 01</title>"); //ESCREVE O TEXTO NA PÁGINA
//  client.println("</head>"); //FECHA A TAG "head"
//  //AS LINHAS ABAIXO CRIAM A PÁGINA HTML
//  client.println("<body>"); //ABRE A TAG "body"
//    client.println("<h3>Temperatura: ");
//    client.println(t);
//    client.println(" *C");
//    client.println("Umidade: ");
//    client.println(h);
//    client.print(" %t");
//    client.println("</h3>");
//    
//    ; //ABRE A TAG "body"
//  client.println("</body>"); //FECHA A TAG "body"
//  client.println("</html>"); //FECHA A TAG "html"
//  delay(1); //INTERVALO DE 1 MILISSEGUNDO
//
//}
//

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