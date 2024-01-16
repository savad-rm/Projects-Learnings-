int relayPulp = 2;   // Relay pin for controlling water pump
int relayMixer = 3;  // Relay pin for controlling mixer motor
int relayDispenser = 4;  // Relay pin for controlling juice glass dispenser motor
int irSensorPin = 5;  // IR sensor pin

void setup() {
  Serial.begin(9600);
  pinMode(relayPulp, OUTPUT);
  pinMode(relayMixer, OUTPUT);
  pinMode(relayDispenser, OUTPUT);
  pinMode(irSensorPin, INPUT);
}

void loop() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    processData(data);
  }
}

void processData(String data) {
  // Parse and process the received data
  // Implement logic to control relays, motors, and sensors based on the received data
}

void dispensePulp() {
  // Activate relay to control water pump for dispensing pulp
  digitalWrite(relayPulp, HIGH);
  delay(5000);  // Adjust the delay based on the time required to dispense pulp
  digitalWrite(relayPulp, LOW);
}

void operateMixer() {
  // Activate relay to control mixer motor
  digitalWrite(relayMixer, HIGH);
  // Add milk and rotate the motor for a specified duration
  delay(5000);  // Adjust the delay based on the mixer operation time
  digitalWrite(relayMixer, LOW);
}

void dispenseJuice() {
  // Activate relay to control juice glass dispenser motor
  digitalWrite(relayDispenser, HIGH);
  delay(5000);  // Adjust the delay based on the time to dispense juice
  digitalWrite(relayDispenser, LOW);
}

bool isGlassDetected() {
  // Check the state of the IR sensor to detect the presence of a glass
  return digitalRead(irSensorPin) == HIGH;
}
