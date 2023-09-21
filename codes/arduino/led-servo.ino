/* Servo */
#include <Servo.h>
Servo neckServo;

/* Leds */
#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
 #include <avr/power.h> // Required for 16 MHz Adafruit Trinket
#endif

// Which pin on the Arduino is connected to the NeoPixels?
#define LED_PIN    6
#define PIN        6 

// How many NeoPixels are attached to the Arduino?
#define LED_COUNT 32
#define NUMPIXELS 32 

// Declare our NeoPixel strip object:
Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);




#define DELAYVAL 500 // Time (in milliseconds) to pause between pixels
char Incoming_value = 0; //Variable for storing Incoming_value



void setup() {
  // These lines are specifically to support the Adafruit Trinket 5V 16 MHz.
  // Any other board, you can remove this part (but no harm leaving it):
#if defined(__AVR_ATtiny85__) && (F_CPU == 16000000)
  clock_prescale_set(clock_div_1);
#endif
  // END of Trinket-specific code.

  strip.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip.show();            // Turn OFF all pixels ASAP
  strip.setBrightness(50); // Set BRIGHTNESS to about 1/5 (max = 255)

  pixels.begin();

  Serial.begin(9600);         //Sets the data rate in bits per second for the serial data transmission with Rpi,
  neckServo.attach(9);
}

void loop() {
  if(Serial.available() > 0)  
  {
    Incoming_value = Serial.read();      //Read the incoming data and store it into variable Incoming_value
    Serial.print(Incoming_value);        //Print Value of Incoming_value in Serial monitor
    Serial.print("\n");        //New line 
    if(Incoming_value == 'G'){ //Checks whether value of Incoming_value is equal to G
      pixels.clear();
      theaterChase(strip.Color(0,   250,   0), 100);
      Serial.print("Mouth Colour Change to Good Mode");
    }
    else if(Incoming_value == 'B'){ //Checks whether value of Incoming_value is equal to B
      pixels.clear();
      theaterChase(strip.Color(127,   0,   0), 150);
      Serial.print("Mouth Colour Change to Bad Mode");
    }
    else if(Incoming_value == 'N'){ //Checks whether value of Incoming_value is equal to N
      pixels.clear();
      neutralmode();
      Serial.print("Mouth Colour Change to Neutral Mode");
    }   
    else if(Incoming_value == 'R'){ //Checks whether value of Incoming_value is equal to R
      pixels.clear();
      rainbow();
      Serial.print("Mouth Colour Change to Rainbow Mode");
    }
    else if(Incoming_value == 'M'){     
    pixels.clear();
    motorMode();
    Serial.print("Mouth Colour Change to Moving Mode");
    }
    else if(Incoming_value == 'L'){
    motorMode();
    neckServo.write(0);      
    Serial.print("Neck turned left. / Mouth Colour Change to moving mode.");
    }
    else if(Incoming_value == 'A'){
    motorMode();
    neckServo.write(90);      
    Serial.print("Neck turned right. / Mouth Colour Change to moving mode.");
    }
    else if(Incoming_value == 'Z') {
    neutralmode();
    neckServo.write(45);      
    Serial.print("Neck turned to zero. / Mouth Colour Change neutral.");
    }
}
}

void rainbow() {
  // Hue of first pixel runs 5 complete loops through the color wheel.
  // Color wheel has a range of 65536 but it's OK if we roll over, so
  // just count from 0 to 5*65536. Adding 256 to firstPixelHue each time
  // means we'll make 5*65536/256 = 1280 passes through this outer loop:
  for(long firstPixelHue = 0; firstPixelHue < 5*65536; firstPixelHue += 256) {
    for(int i=0; i<strip.numPixels(); i++) { // For each pixel in strip...
      // Offset pixel hue by an amount to make one full revolution of the
      // color wheel (range of 65536) along the length of the strip
      // (strip.numPixels() steps):
      int pixelHue = firstPixelHue + (i * 65536L / strip.numPixels());
      // strip.ColorHSV() can take 1 or 3 arguments: a hue (0 to 65535) or
      // optionally add saturation and value (brightness) (each 0 to 255).
      // Here we're using just the single-argument hue variant. The result
      // is passed through strip.gamma32() to provide 'truer' colors
      // before assigning to each pixel:
      strip.setPixelColor(i, strip.gamma32(strip.ColorHSV(pixelHue)));
    }
    strip.show(); // Update strip with new contents
  }
}

void theaterChase(uint32_t color, int wait) {
  for(int a=0; a<10; a++) {  // Repeat 10 times...
    for(int b=0; b<3; b++) { //  'b' counts from 0 to 2...
      strip.clear();         //   Set all pixels in RAM to 0 (off)
      // 'c' counts up from 'b' to end of strip in steps of 3...
      for(int c=b; c<strip.numPixels(); c += 3) {
        strip.setPixelColor(c, color); // Set pixel 'c' to value 'color'
      }
      strip.show(); // Update strip with new contents
      delay(wait);  // Pause for a moment
    }
  }
}

void neutralmode() {
  pixels.clear(); // Set all pixel colors to 'off'

  // The first NeoPixel in a strand is #0, second is 1, all the way up
  // to the count of pixels minus one.
  for(int i=0; i<NUMPIXELS; i++) { // For each pixel...

    // pixels.Color() takes RGB values, from 0,0,0 up to 255,255,255
    // Here we're using a moderately bright green color:
    pixels.setPixelColor(i, pixels.Color(0, 0, 0));

    pixels.show();   // Send the updated pixel colors to the hardware.

    delay(DELAYVAL); // Pause before next pass through loop
  }
}

void motorMode() {
  theaterChase(strip.Color(255, 255, 0), 100);
  theaterChase(strip.Color(25,   25,   25), 100);
  theaterChase(strip.Color(255, 255, 0), 100);
  theaterChase(strip.Color(25,   25,   25), 100);  
}
 