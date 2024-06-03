// variáveis para conexão bluetooth
  #include <SoftwareSerial.h>


  SoftwareSerial SerialBT(8, 9);
  char valorDoBluetooth;




// variáveis do sensor ultrassônico
  #include <HCSR04.h>


  const byte trigger = 11;
  const byte echo = 10;
  const int maxCm = 405;


  float distance;
  float mudarDistancia;


  UltraSonicDistanceSensor sensorUltrassonico(trigger, echo, maxCm);




// variáveis para uso do buzzer
  const byte buzzer = 12;
  int bz = 200;
  bool flagArpegio; // obs: para baixo
  bool flagAtivo;




// variáveis para uso do sensor de temperatura
  const int sensorTemperatura = A0;
  float graus;
  float mudarGraus;




//variáveis para o uso dos motores
  // motor 1
  const byte in1 = 2;
  const byte in2 = 4;
  const byte enA = 3;
  //motor 2
  const byte in3 = 5;
  const byte in4 = 7;
  const byte enB = 6;

  byte velocidade = 100;




const byte led = 13; // variável para uso do led




// variáveis para inicialização dos componentes de OUTPUT
  int componentesOut[] = { in1, in2, enA, in3, in4, enB, led};
  const byte tamanhoListaOut = 7;




unsigned int tempo; // variável para acompanhamento do tempo //unsigned long tempo; // até 4294967295






void setup()
{
  iniciar();
}


void loop()
{
  // Read data from the Bluetooth module
  if (SerialBT.available())
  {
    valorDoBluetooth = SerialBT.read();
    // Process the received data and take appropriate actions


    if (valorDoBluetooth == 'F' || valorDoBluetooth == 'T' || valorDoBluetooth == 'D' || valorDoBluetooth == 'E' || valorDoBluetooth == 'P') // movimento
    {
      movimento();
    }
   
    else if (valorDoBluetooth == 'L') // luz
    {
      luz();
    }


    else if (valorDoBluetooth == 'B') // sirene
    {
      Serial.println("buzzer");
      flagAtivo = !flagAtivo;
    }


    delay(4);
    tempo += 4;


    valorDoBluetooth = '\0'; // Reset the value to null character (or any other default value)
  }


  buzz();


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
  SerialBT.begin(9600);
  Serial.begin(9600);


  for (int n = 0; n < tamanhoListaOut; n++) {
    pinMode(componentesOut[n], OUTPUT);
  }
}




void frente()
{
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  digitalWrite(enA, velocidade);
  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
  digitalWrite(enB, velocidade);
}
void tras()
{
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
  digitalWrite(enA, velocidade);
  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW);
  digitalWrite(enB, velocidade);
}
void direita()
{
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
  digitalWrite(enA, velocidade);
  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
  digitalWrite(enB, velocidade);
}
void esquerda()
{
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  digitalWrite(enA, velocidade);
  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW);
  digitalWrite(enB, velocidade);
}
void parar()
{
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  digitalWrite(enA, velocidade);
  digitalWrite(in3, LOW);
  digitalWrite(in4, LOW);
  digitalWrite(enB, velocidade);
}
void movimento()
{
  if (valorDoBluetooth == 'F')
    {
      Serial.println("Frente");
      frente();
    }
    else if (valorDoBluetooth == 'T')
    {
      Serial.println("Trás");
      tras();
    }
    else if (valorDoBluetooth == 'D')
    {
      Serial.println("Direita");
      direita();
    }
    else if (valorDoBluetooth == 'E')
    {
      Serial.println("Esquerda");
      esquerda();
    }
    else if (valorDoBluetooth == 'P')
    {
      Serial.println("Parar");
      delay(1);
      tempo++;
      parar();
    }
}




void luz()
{
  digitalWrite(led, !digitalRead(led));
  Serial.print("Led ");


  if (digitalRead(led) == 0)
  {
    Serial.println("Desligado");
  }
  else
  {
    Serial.println("Ligado");
  }
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




void buzz()
{
  if (flagAtivo) // == true;
  {
    tone(buzzer, bz);


    if (bz == 3000)
    {
      flagArpegio = true;
      noTone(buzzer);
      Serial.println(bz);
    }
    else if (bz == 200)
    {
      flagArpegio = false;
      noTone(buzzer);
      Serial.println(bz);
    }


    if (flagArpegio)
    {
      bz--;
    }
    else
    {
      bz++;
    }
    delay(1);
    tempo++;
  }
 
  else
  {
    noTone(buzzer);
    delay(1);
    tempo++;
  }
}






void enviarPeloSerial()
{
  if (Serial.available())
  {
    valorDoBluetooth = Serial.read();
    if (valorDoBluetooth == 'A')
    {
      SerialBT.println("salve");
      Serial.println("benvenuto");
    }
    else if (valorDoBluetooth == 'a')
    {
      SerialBT.println("falou");
      Serial.println("ciao");
    }
  }
}
void teste()
{
  if(valorDoBluetooth == 'X')
    {
      Serial.println("PYTHON RECEBEU AS INFORMAÇÕES, ENVIOU UM VALOR AO ARDUINO, QUE PRINTOU ISSO ");  
    }
}

