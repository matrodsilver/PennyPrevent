#include <arduino.h>
#include <WiFi.h>
#include <Firebase_ESP_Client.h>
#include "addons/TokenHelper.h"
#include "addons/RTDBHelper.h"

//* variáveis da biblioteca de wifi
  WiFiClient client;
  const char* url = "https://predito-85975-default-rtdb.firebaseio.com/Dados2";
  const char* apiKey = "AIzaSyD0WLSyVWJRM72-6HRfcDe_m3iLpHglY2s";

//* Dados Firebase
  FirebaseData dados;
  FirebaseConfig config;
  FirebaseAuth auth;

//* variáveis para uso do sensor de temperatura
  const byte sensorTemperatura = A0;
  float graus;
  float mudarGraus;

//* variáveis para uso do sensor infravermelho
  const byte sensorInfra = 5;
  bool valorInfra;
  byte mudarInfra;

//* variáveis para uso do sensor de vibração
  const byte sensorVibracao = 3;
  bool valorVibracao;
  byte mudarVibracao;

//* variáveis para inicialização
  const byte in = {sensorTemperatura, sensorInfra, sensorVibracao};
  const byte qntIn = 3;


//* protótipos *//
void iniciar();
void temperatura();
void infra();
void vibracao();


void setup()
{
  iniciar();
}

void loop()
{
  temperatura();
  infra();
  vibracao();

  if (Firebase.ready())
  {
    //# Temperatura
    if (Firebase.RTDB.setFloat(&dados, "/Dados2/Temperatura", graus))
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
    if (Firebase.RTDB.setBool(&dados, "/Dados2/Infravermelho", valorInfra))
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
    if (Firebase.RTDB.setBool(&dados, "/Dados2/Vibração", valorVibracao))
    {
      Serial.println("Vibração enviado");
      Serial.println(dados.dataPath());
    }
    else
    {
      Serial.println("Erro ao enviar vibração");
      Serial.println(dados.errorReason());
    }
  }

  delay(500);
}


void iniciar()
{
    Serial.begin(9600);

    // INPUT pins setup //
    for (int i = 0; i < qntIn; i++)
    {
      pinMode(in[i], INPUT);
    }

    // conexão do wifi //
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

    // conexão firebase //
    config.api_key = apiKey;
    config.database_url = url;

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
  graus = 36.6;//analogRead(sensorTemperatura) * 500 / 1023;

  //. Serial.print("Temperatura: " + String(graus) + "°C");
}

void infra()
{
  valorInfra = true;//digitalRead(sensorInfra);

  //. Serial.print("Infra: " + String(valorInfra));
}

void vibracao()
{
  valorVibracao = true;//digitalRead(sensorVibracao);

  //. Serial.print("Vibração: " + String(valorVibracao));
}