#include <LiquidCrystal.h>

LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

const int TRIG_PIN = 7;
const int ECHO_PIN = 6;
const int BUTTON_PIN = 8;
const int BUZZER_PIN = 9;
const int LED_PIN = 10;
const int LDR_PIN = A0;

enum SystemState { OPEN_SEA, ANCHOR_DROPPED, STORM, CHARYBDIS, WRECKED };

SystemState currentState = OPEN_SEA;
SystemState previousState = (SystemState)-1;

bool lastButtonState = HIGH;
unsigned long hazardStartTime = 0;
unsigned long lastBlinkTime = 0;
bool ledState = LOW;

long readDistanceCM() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  long duration = pulseIn(ECHO_PIN, HIGH, 30000);
  return (duration == 0) ? 999 : (duration * 0.0343 / 2);
}

void setup() {
  // defining physical size of lcd scree.
  lcd.begin(16, 2);
  // defining the functions of each of the pins.
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW); // Explicit initialization
}

void loop() {
  // Button toggle detection (Falling Edge)
  bool currentButtonState = digitalRead(BUTTON_PIN);
  if (lastButtonState == HIGH && currentButtonState == LOW) {
    if (currentState == ANCHOR_DROPPED) {
      currentState = OPEN_SEA;
    } else if (currentState != WRECKED) {
      currentState = ANCHOR_DROPPED;
    }
  }
  lastButtonState = currentButtonState;
  long distanceVal = readDistanceCM();
  bool isStormTriggered = (analogRead(LDR_PIN) < 1005);
  bool isCharybdisTriggered = (distanceVal < 100);

  switch (currentState) {
    case OPEN_SEA:
      noTone(BUZZER_PIN);
      digitalWrite(LED_PIN, LOW);

      if (isStormTriggered) {
        currentState = STORM;
        hazardStartTime = millis();
        lastBlinkTime = millis();
        ledState = HIGH;
        digitalWrite(LED_PIN, ledState);
      } else if (isCharybdisTriggered) {
        currentState = CHARYBDIS;
        hazardStartTime = millis();
      }
      break;

    case ANCHOR_DROPPED:
      noTone(BUZZER_PIN);
      digitalWrite(LED_PIN, LOW);
      break;

    case STORM:
      noTone(BUZZER_PIN);
      if (millis() - lastBlinkTime >= 250) {
        lastBlinkTime = millis();
        ledState = !ledState;
        digitalWrite(LED_PIN, ledState);
      }

      if (!isStormTriggered) {
        currentState = OPEN_SEA;
        digitalWrite(LED_PIN, LOW);
      } else if (millis() - hazardStartTime >= 5000) {
        currentState = WRECKED;
        digitalWrite(LED_PIN, LOW);
      }
      break;

    case CHARYBDIS:
      digitalWrite(LED_PIN, LOW);
      tone(BUZZER_PIN, 800);

      if (!isCharybdisTriggered) {
        currentState = OPEN_SEA;
        noTone(BUZZER_PIN);
      } else if (millis() - hazardStartTime >= 5000) {
        currentState = WRECKED;
        noTone(BUZZER_PIN);
      }
      break;

    case WRECKED:
      noTone(BUZZER_PIN);
      digitalWrite(LED_PIN, LOW);
      break;
  }

  // Screen rendering triggered on state transition
  if (currentState != previousState) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("STATE:");
    lcd.setCursor(0, 1);
    
    switch (currentState) {
      case OPEN_SEA:       lcd.print("OPEN SEA"); break;
      case ANCHOR_DROPPED: lcd.print("ANCHOR DROPPED"); break;
      case STORM:          lcd.print("STORM"); break;
      case CHARYBDIS:      lcd.print("CHARYBDIS"); break;
      case WRECKED:        lcd.print("WRECKED"); break;
    }
    previousState = currentState;
  }
}