#include <WiFi.h>
#include <FirebaseESP32.h> // Include the Firebase library

// Replace with your WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Replace with your Firebase project details
const char* firebaseProjectId = "YOUR_FIREBASE_PROJECT_ID"; //"predito-85975";
const char* firebaseDatabaseURL = "YOUR_FIREBASE_DATABASE_URL"; //"https://predito-85975-default-rtdb.firebaseio.com/Dados2";
const char* firebaseSecret = "YOUR_FIREBASE_SECRET"; //"";

// Define Firebase data path
const char* dataPath = "random_number";

FirebaseData fbdo;
WiFiClient client;

void setup() {
  Serial.begin(9600);

  // Connect to WiFi network
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.println("Connecting to WiFi..");
    delay(500);
  }
  Serial.println("Connected to WiFi!");

  // Initialize Firebase
  Firebase.begin(firebaseProjectId, firebaseDatabaseURL, firebaseSecret);
  Firebase.reconnectWiFi(true);
  fbdo = Firebase.dataObject();
}

void loop() {
  // Generate a random number
  int randomNumber = random(0, 1024); // Adjust range as needed

  // Set the random number in Firebase
  Firebase.setFloat(&fbdo, dataPath, randomNumber);

  // Check for errors
  if (Firebase.error()) {
    Serial.println("Firebase error:");
    Serial.println(Firebase.errorReason());
  } else {
    Serial.println("Random number sent to Firebase!");
  }

  delay(5000); // Send data every 5 seconds (adjust as needed)
}
