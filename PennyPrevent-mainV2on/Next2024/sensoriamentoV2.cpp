#include <arduino.h>
#include <WiFi.h>
#include <FirebaseESP32.h>
#include "addons/TokenHelper.h"
#include "addons/RTDBHelper.h"

//# variáveis da biblioteca de wifi //
  WiFiClient client;
  const char* url = "https://predito-85975-default-rtdb.firebaseio.com/Dados2";
  const char* apiKey = "AIzaSyD0WLSyVWJRM72-6HRfcDe_m3iLpHglY2s";

//# Dados Firebase //
  FirebaseData dados;
  FirebaseConfig config;
  FirebaseAuth auth;
  String basePath = "/Dados2";

//# variáveis para uso do sensor de temperatura //
  const byte sensorTemperatura = 14;
  float graus;

//# variáveis para uso do sensor infravermelho //
  const byte sensorInfra = 26;
  bool valorInfra;

//# variáveis para uso do sensor de vibração //
  const byte sensorVibracao = 27;
  bool valorVibracao;

//# variáveis sensor de cor //
const byte S0 = 35;
const byte S1 = 34;
const byte S2 = 33;
const byte S3 = 32;
const byte sensorIn = 25;

byte pulsoVermelho = 0;
byte pulsoVerde = 0;
byte pulsoAzul = 0;

//# variáveis para inicialização
  const byte in[] = {sensorTemperatura, sensorInfra, sensorVibracao, sensorIn};
  const byte out[] = {S0, S1, S2, S3};
  
  const byte qntIn = 4;
  const byte qntOut = 4;


//# protótipos
void iniciar();
void temperatura();
void infra();
void vibracao();
void getRedPW();
void getGreenPW();
void getBluePW();


void setup()
{
  iniciar();
}

void loop()
{
  temperatura();
  infra();
  vibracao();
  getRedPW();
  getGreenPW();
  getBluePW();

  if (Firebase.ready())
  {
    //# Temperatura
    if (Firebase.setFloat(dados, basePath+"/Temperatura", graus))
    {
      Serial.println("Temperatura enviada");
      Serial.println(dados.dataPath());
    }
    else
    {
      Serial.println("Erro ao enviar temperatura");
      Serial.println(dados.errorReason());
    }

    //# Infravermelho
    if (Firebase.setBool(dados, basePath+"/Infravermelho", valorInfra))
    {
      Serial.println("Infravermelho enviado");
      Serial.println(dados.dataPath());
    }
    else
    {
      Serial.println("Erro ao enviar infravermelho");
      Serial.println(dados.errorReason());
    }

    //# Vibração
    if (Firebase.setBool(dados, basePath+"/Vibracao", valorVibracao))
    {
      Serial.println("Vibração enviado");
      Serial.println(dados.dataPath());
    }
    else
    {
      Serial.println("Erro ao enviar vibração");
      Serial.println(dados.errorReason());
    }

    //# Cor
    //? vermelho ?//
    if (Firebase.setInt(dados, basePath+"/Cor/Vermelho", pulsoVermelho))
    {
      Serial.println("Pulso vermelho enviado");
      Serial.println(dados.dataPath());
    }
    else
    {
      Serial.println("Erro ao enviar pulso vermelho");
      Serial.println(dados.errorReason());
    }

    //* verde *//
    if (Firebase.setInt(dados, basePath+"/Cor/Verde", pulsoVerde))
    {
      Serial.println("Pulso verde enviado");
      Serial.println(dados.dataPath());
    }
    else
    {
      Serial.println("Erro ao enviar pulso verde");
      Serial.println(dados.errorReason());
    }

    //! azul !//
    if (Firebase.setInt(dados, basePath+"/Cor/Azul", pulsoAzul))
    {
      Serial.println("Pulso azul enviada");
      Serial.println(dados.dataPath());
    }
    else
    {
      Serial.println("Erro ao enviar pulso Azul");
      Serial.println(dados.errorReason());
    }
  }

  Serial.println("Iteração concluída");
  delay(3000);
}


void iniciar()
{
    Serial.begin(9600);

    //# Pins setup //
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

    //# conexão do wifi //
    WiFi.disconnect();
    delay(3000);
    Serial.println("START");
    WiFi.begin("MatRodNet", "11etrinta");
    while ((!(WiFi.status() == WL_CONNECTED)))
    {
      delay(300);
      Serial.print(".");
    }
    Serial.println("Conectado");

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

void temperatura()
{
  graus = analogRead(sensorTemperatura) * 500 / 1023;

  Serial.println("Temperatura: " + String(graus) + "°C");
}

void infra()
{
  valorInfra = digitalRead(sensorInfra);

  Serial.println("Infra: " + String(valorInfra));
}

void vibracao()
{
  valorVibracao = digitalRead(sensorVibracao);

  Serial.println("Vibração: " + String(valorVibracao));
}

// class SensorCor
// {
//   public:
    //? Verificar pulso da cor vermelha ?//
    void getRedPW()
    {
      // Set sensor to read Red only
      digitalWrite(S2,LOW);
      digitalWrite(S3,LOW);
      // Read the output Pulse Width
      pulsoVermelho = pulseIn(sensorIn, LOW);
      // Return the value
      Serial.println("Vermelho: " + String(pulsoVermelho));//.return PW;
    }

    //* Verificar pulso da cor verde *//
    void getGreenPW()
    {
      // Set sensor to read Green only
      digitalWrite(S2,HIGH);
      digitalWrite(S3,HIGH);
      // Read the output Pulse Width
      pulsoVerde = pulseIn(sensorIn, LOW);
      // Return the value
      Serial.println("Verde: " + String(pulsoVerde));//.return PW;
    }

    //! Verificar pulso da cor azul !//
    void getBluePW()
    {
      // Set sensor to read Blue only
      digitalWrite(S2,LOW);
      digitalWrite(S3,HIGH);
      // Read the output Pulse Width
      pulsoAzul = pulseIn(sensorIn, LOW);
      // Return the value
      Serial.println("Azul: " + String(pulsoAzul));//. return PW;
    }
// };


/*
float mapV2()
{
  float map(long x, float in_min, float in_max, float out_min, float out_max)
  {
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
  }
}*/