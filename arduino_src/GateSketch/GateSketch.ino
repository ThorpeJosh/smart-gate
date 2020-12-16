// vim: filetype=cpp
/*Arduino code to communicate with the RPi over serial.
Information shared with RPi includes analog pin voltages and other inputs that trigger the gate.
All analog readings will be smoothed and converted to voltages (floats)

Serial communication contract as follows:

Handshake:
    Arduino sends 'A', RPi responds with 'A'
Button Pin Negotiation:
    Arduino sends 'B', RPi sends pin numbers as chars for each button pin, then 'B' when it's finished.
Analog Voltages:
    RPi sends 'V', Arduino responds with 'V' followed by voltages[] and then a checksum
Gate Trigger:
    Arduino sends 'O', followed by a trigger message, RPi doesn't respond.

*/
#include <SPI.h>
#include <QuickMedianLib.h>
#include <Servo.h>

// Configurable Parameters 
const int noOfAnalogPins = 6;
const int voltageDecimalPlaces = 4;
const int lengthOfRadioKey = 8; //Length of expected secret key to receive over 433MHz radio


// Globals
float voltages[noOfAnalogPins];
float checksum;
byte incomingByte;

// Servo
Servo servo;
byte servoPos;
const int servoPin = 9;

// Button pins are given by RPi, presume less than 10 buttons will be used
int buttonPins[10] = {0};
unsigned long lastButtonPress = 0;
unsigned long debounceDelay = 1000;


void setup()
{
    // Use external analog reference and put a jumper between pins 3.3V and AREF
    analogReference(EXTERNAL);
    servo.attach(servoPin);
    // start serial at 115200bps
    Serial.begin(115200);
    serialHandshake();
    // Get button pins and initialize them
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, LOW);
    getButtonPins();
    for (int i=0; i<10; i++)
    {
        if (buttonPins[i] > 0)
        {
            Serial.print("Initializing input, digital pin number: ");
            Serial.println(buttonPins[i]);
            pinMode(buttonPins[i], INPUT_PULLUP);
        }
    }
}


void loop()
{
    if (Serial.available() > 0)
    {
        incomingByte = Serial.read();
        if (incomingByte == 'V')
        {
            // Read analog pins and send data if requested over serial
            sendAnalogVoltages();
        }
        else if (incomingByte == 'S')
        {
            // RPi is sending a servo position update
            updateServo();
        }
    }
    // Check if buttons have been pressed
    if ((millis() - lastButtonPress) > debounceDelay)
    {
        if (checkButtons())
        {
            lastButtonPress = millis();
            //Toggle led
            digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
        }
    }
}

void flushSerialInputBuffer()
{
    while (Serial.available() > 0)
    {
        Serial.read();
    }
}

void updateServo()
{
    // Wait until we recieve new byte
    while (Serial.available() <= 0)
    {
        Serial.println("Waiting for servo position");
        delay(100);
    }
    servoPos = Serial.read();
    Serial.print("Sending servo to position: ");
    Serial.println(servoPos);

    servo.write(servoPos);
}

void sendAnalogVoltages()
{
    updateAnalogVoltages();
    Serial.println('V');
    for(int i=0; i<noOfAnalogPins; i++)
    {
        Serial.println(voltages[i], voltageDecimalPlaces);
    }
    Serial.println(checksum, voltageDecimalPlaces);
}

void updateAnalogVoltages()
{
    // Update the global voltages array
    
    // Take multiple readings and then apply median
    int noSamples = 21;
    int analogVals[noOfAnalogPins][noSamples];
    
    // Take samples over noSamples*delay() seconds
    for(int s=0; s<noSamples; s++)
    {
        for(int i=0; i<noOfAnalogPins; i++)
        {
            analogVals[i][s] = analogRead(i);
        }
        delay(1);
    }

    // Get median for each pin
    for(int i=0; i<noOfAnalogPins; i++)
    {
        voltages[i] = float(QuickMedian<int>::GetMedian(&analogVals[i][0], noSamples));
    }

    // Multiply by 3.3/1023 to get voltage
    for(int i=0; i<noOfAnalogPins; i++)
    {
        voltages[i] = (voltages[i]) * (3.3 / 1023.0);
    }

    // Calculate the checksum
    checksum = 0.0;
    for(int i=0; i<noOfAnalogPins; i++)
    {
        // Round the voltages to the correct decimal places
        checksum += round(voltages[i]*float(pow(10, voltageDecimalPlaces)))/float(pow(10, voltageDecimalPlaces));
    }
}

void serialHandshake()
{
    // Wait until we recieve a byte
    while (Serial.available() <= 0)
    {
        Serial.println('A');
        delay(200);
    }
    flushSerialInputBuffer();
}

void getButtonPins()
{
    // Send an 'B' to request the button pins
    flushSerialInputBuffer();
    Serial.println('B');
    bool finished_flag = false;
    int buttonNo = 0;
    char incomingChar;
    
    Serial.println("Getting button pins");
    while (buttonNo < 10)
    {
        // Wait for serial packets
        while (Serial.available() <= 0)
        {
            Serial.println("waiting for next pin char");
            delay(1000);
        }
        incomingChar = Serial.read();
        // Check if all pins have been received
        if (incomingChar == 'B')
        {
            Serial.println("Got all pins");
            break;
        }
        // Check if value is valid
        if (incomingChar < '1')
        {
            continue;
        }
        // Convert ascii Char to byte
        byte pinNo = incomingChar - '0';
        Serial.print("Got pin: ");
        Serial.println(pinNo);
        buttonPins[buttonNo] = int(pinNo);
        buttonNo++;
    }
}


bool checkButtons()
{
    bool pressed;
    int noSamples = 50;
    for (int i=0; i<10; i++)
    {
        if (buttonPins[i] > 0)
        {
            pressed = !digitalRead(buttonPins[i]);
            // Check to ensure that this wasn't a false positive
            if (pressed)
            {
                for (int j=0; j<noSamples; j++)
                {
                    if (digitalRead(buttonPins[i]))
                    {
                        // Button is no longer pressed, ignore initial press
                        pressed = false;
                        break;
                    }
                    delay(1);
                }
            }
            if (pressed)
            {
                // Button has been pressed, send capital "O"
                Serial.println("O");
                // Send the pin number to RPi
                Serial.println(buttonPins[i]);
                break;
            }
        }
    }
    return pressed;
}
