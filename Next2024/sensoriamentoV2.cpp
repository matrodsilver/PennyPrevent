#include <arduino.h> // Necessário no PlatformIO

#include <WiFi.h>
#include <FirebaseESP32.h>
#include "addons/TokenHelper.h"
#include "addons/RTDBHelper.h"
#include <OneWire.h>
#include <DallasTemperature.h>


//# variáveis da biblioteca de wifi //
WiFiClient client;
const char* url = "https://<projeto>";
const char* apiKey = "<api>";

//# Dados Firebase //
FirebaseData dados;
FirebaseConfig config;
FirebaseAuth auth;
String basePath = "/<Caminho Padrão De Envio>/"; // caminho de envio dos dados
unsigned int id;

//# variáveis para uso do sensor de temperatura //
const byte ONE_WIRE_BUS = 4; // pino do sensor
// Setup oneWire instance to communicate with any OneWire devices (not just Maxim/Dallas temperature ICs)
OneWire oneWire(ONE_WIRE_BUS);
// Pass oneWire reference to Dallas Temperature.
DallasTemperature sensors(&oneWire);

float graus;

//# variáveis para uso do sensor infravermelho //
const byte sensorInfra = 26;
byte valorInfra;

//# variáveis para uso do sensor de vibração //
const byte sensorVibracao = 27;
byte valorVibracao;

//# variáveis sensor de cor //
const byte S0 = 35;
const byte S1 = 34;
const byte S2 = 33;
const byte S3 = 32;
const byte sensorIn = 25;

byte pulsoVermelho;
byte pulsoVerde;
byte pulsoAzul;
byte maior;

//# variáveis para inicialização //
  const byte in[] = {sensorInfra, sensorVibracao, sensorIn};
  const byte out[] = {S0, S1, S2, S3};
  
  const byte qntIn = 3;
  const byte qntOut = 4;


//# protótipos //
void iniciar();
void temperatura();
void infra();
void vibracao();
void getRedPW();
void getGreenPW();
void getBluePW();
void cores();
void enviarDados();


void setup()
{
  iniciar();
}

void loop()
{
  temperatura();
  infra();
  vibracao();
  cores();

  enviarDados();

  

  Serial.println("Iteração concluída");
  delay(1000);
}


void iniciar()
{
    Serial.begin(9600);

    //# setup pinos //
    for (int i = 0; i < qntIn; i++)
    {
      pinMode(in[i], INPUT);
    }
    for (int i = 0; i < qntOut; i++)
    {
      pinMode(out[i], OUTPUT);
    }

    //# setupt sensor de cor //
    // Set Pulse Width scaling to 20%
    digitalWrite(S0,HIGH);
    digitalWrite(S1,LOW);

    //# setup sensor de temperatura //
    sensors.begin();

    //# conexão do wifi //
    WiFi.disconnect();
    delay(3000);
    Serial.println("START");
    WiFi.begin("<Wifi>", "<Senha>");
    while ((!(WiFi.status() == WL_CONNECTED)))
    {
      delay(300);
      Serial.print(".");
    }
    Serial.println("_—‾C͟o͟n͟e͟c͟t͟a͟d͟o͟‾—_");

    delay(1000);

    //# conexão firebase //
    config.database_url = url;
    config.api_key = apiKey;
    // config.signer.tokens.legacy_token = "<database secret>";

    if (Firebase.signUp(&config, &auth, "", ""))
    {
      Serial.println("Conectado ao Firebase");
    }
    else
    {
      Serial.println("Erro ao conectar ao Firebase");
      Serial.printf("%s\n", config.signer.signupError.message.c_str());
    }

    config.token_status_callback = tokenStatusCallback;
    Firebase.begin(&config, &auth);
    Firebase.reconnectWiFi(true);
}

//# função para coletar a temperatura
void temperatura()
{
  graus = -2;

  sensors.requestTemperatures();

  graus = sensors.getTempCByIndex(0);

  Serial.println("Temperatura: " + String(graus) + "°C");
}

// função para coletar o valor do sensor infravermelho
void infra()
{
  valorInfra = -2;

  valorInfra = !digitalRead(sensorInfra);

  Serial.println("Infra: " + String(valorInfra));
}

//# função para coletar o valor do sensor de vibração
void vibracao()
{
  valorVibracao = -2;

  valorVibracao = !digitalRead(sensorVibracao);

  Serial.println("Vibração: " + String(valorVibracao));
}


//# funções para coletar as cores //

//? verificar pulso da cor vermelha
void getRedPW()
{
  pulsoVermelho = -2;
  
  // Set sensor to read Red only
  digitalWrite(S2,LOW);
  digitalWrite(S3,LOW);
  // Read the output Pulse Width
  pulsoVermelho = pulseIn(sensorIn, LOW);

  Serial.println("Vermelho: " + String(pulsoVermelho));
}

//* verificar pulso da cor verde
void getGreenPW()
{
  pulsoVerde = -2;

  // Set sensor to read Green only
  digitalWrite(S2,HIGH);
  digitalWrite(S3,HIGH);
  // Read the output Pulse Width
  pulsoVerde = pulseIn(sensorIn, LOW);

  Serial.println("Verde: " + String(pulsoVerde));
}

//! verificar pulso da cor azul
void getBluePW()
{
  pulsoAzul = -2;

  // Set sensor to read Blue only
  digitalWrite(S2,LOW);
  digitalWrite(S3,HIGH);
  // Read the output Pulse Width
  pulsoAzul = pulseIn(sensorIn, LOW);

  Serial.println("Azul: " + String(pulsoAzul));
}

//# Determinar a cor mais evidente (Red = 1, Green = 2, Blue = 3)
void cores()
{
  getRedPW();
  getGreenPW();
  getBluePW();

  maior = -2;

  if (pulsoVermelho > pulsoVerde) // R B
  {
    if (pulsoVermelho > pulsoAzul)
    {
      maior = 1; // Red
    }
    else
    {
      maior = 3; // Blue
    }
  }
  else if (pulsoVerde > pulsoVermelho)// G B
  {
    if (pulsoVerde > pulsoAzul)
    {
      maior = 2; // Green
    }
    else
    {
      maior = 3; // Blue
    }
  }
}

//# função para enviar os dados obtidos ao firebase
void enviarDados()
{
  if (Firebase.ready())
  {
    //# Get current index
    if (Firebase.getInt(dados, "/indexAtual"))
    {
      id = 1 + dados.intData();

      Serial.println("Index: " + String(id));
    }
    else
    {
      Serial.println("Erro ao coletar index");
      Serial.println(dados.errorReason());
    }

    //# Temperatura
    if (Firebase.setFloat(dados, basePath + String(id) + "/Temperatura", graus))
    {
      Serial.println("Temperatura enviada");
      //. Serial.println(dados.dataPath());
    }
    else
    {
      Serial.println("Erro ao enviar temperatura");
      Serial.println(dados.errorReason());
    }

    //# Infravermelho
    if (Firebase.setInt(dados, basePath + String(id) + "/Infravermelho", valorInfra))
    {
      Serial.println("Infravermelho enviado");
      //. Serial.println(dados.dataPath());
    }
    else
    {
      Serial.println("Erro ao enviar infravermelho");
      Serial.println(dados.errorReason());
    }

    //# Vibração
    if (Firebase.setInt(dados, basePath + String(id) + "/Vibracao", valorVibracao))
    {
      Serial.println("Vibração enviada");
      //. Serial.println(dados.dataPath());
    }
    else
    {
      Serial.println("Erro ao enviar vibração");
      Serial.println(dados.errorReason());
    }

    //# Cor
    if (Firebase.setInt(dados, basePath + String(id) + "/Cor", maior))
    {
      Serial.println("Cor enviada");
      //. Serial.println(dados.dataPath());
    }
    else
    {
      Serial.println("Erro ao enviar cor");
      Serial.println(dados.errorReason());
    }

    //# Atualizar index
    if (Firebase.setInt(dados, "/indexAtual", id))
    {
      Serial.println("Index atualizado");
      //. Serial.println(dados.dataPath());
    }
    else
    {
      Serial.println("Erro ao atualizar index");
      Serial.println(dados.errorReason());
    }
  }
}

/*
float mapV2()
{
  float map(long x, float in_min, float in_max, float out_min, float out_max)
  {
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
  }
}*/
