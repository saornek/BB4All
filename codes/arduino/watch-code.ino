#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <PulseSensorPlayground.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

#define PULSE_SENSOR_PIN A0
#define BUTTON_PIN 2  // Pin number where the button is connected

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

PulseSensorPlayground pulseSensor;

boolean buttonState = false;
boolean lastButtonState = false;

void setup() {
  // OLED Screen Setup
  if(!display.begin(SSD1306_I2C_ADDRESS, OLED_RESET)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;);
  }
  display.display();
  delay(2000);
  
  // Pulse Sensor Setup
  pulseSensor.begin();
  pulseSensor.attach(PULSE_SENSOR_PIN);
  pulseSensor.setOutputType(OUTPUT_TYPE_SERIAL_PLOTTER);
  
  // Button Setup
  pinMode(BUTTON_PIN, INPUT);
}

void loop() {
  int pulseValue = pulseSensor.getBeatsPerMinute(); // pulse sensor data
  buttonState = digitalRead(BUTTON_PIN); // state of the button

  display.clearDisplay(); // Clear the OLED display

  // Display the pulse value on the OLED screen
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 10);
  display.print("Pulse: ");
  display.print(pulseValue);
  display.print(" BPM");

  if (buttonState == HIGH) {
    display.setTextSize(2);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0, 40);
    display.println("ALERT!");
  }

  display.display();

  /*
  // Uncomment for debugging
  Serial.print("Pulse: ");
  Serial.print(pulseValue);
  Serial.println(" BPM");
  Serial.print("Button State: ");
  Serial.print(buttonState);
  */

  delay(1000);  // Update every 1 second
}
