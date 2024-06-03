// variáveis do sensor ultrassônico
  #include <HCSR04.h>

  const byte trigger = 11;
  const byte echo = 10;
  const int maxCm = 405;

  float distance;
  float mudarDistancia;

  UltraSonicDistanceSensor sensorUltrassonico(trigger, echo, maxCm);


// variáveis para uso do sensor de temperatura
  const int sensorTemperatura = A0;
  float graus;
  float mudarGraus;


// variáveis para uso do sensor de 


unsigned int tempo; // variável para acompanhamento do tempo //unsigned long tempo; // até 4294967295



void setup()
{
  iniciar();
}


void loop()
{
  if (tempo % 1000 == 0) // distância & temperatura
    {
      Serial.println("tempo");
      SerialBT.println("Chamando Funções coletoras de dados");
      ultrassonico();
      temperatura();
    }
 
  if (tempo > 65500) // > 65,535)
    {
      tempo = 0;
    }


  // Your existing code for receiving data from the Serial Monitor and sending responses via Bluetooth
  enviarPeloSerial();


  delay(1);
  tempo++;
}



void iniciar()
{
  Serial.begin(9600);
  Serial.print("Serial iniciado");
}

void ultrassonico()
{
  distance = sensorUltrassonico.measureDistanceCm();
  if (distance != mudarDistancia)
  {
    SerialBT.println("U" + String(distance));
    Serial.println("U" + String(distance));


    mudarDistancia = distance;
  }
}

void temperatura()
{
  graus = analogRead(sensorTemperatura) * 500 / 1023;
  if (graus != mudarGraus)
  {
    SerialBT.println("G" + String(graus));
    Serial.println("G" + String(graus));


    mudarGraus = graus;
  }
}

