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
#include <RH_ASK.h>
#include <SPI.h>

// Configurable Parameters 
const int noOfAnalogPins = 6;
const int voltageDecimalPlaces = 4;
const int lengthOfRadioKey = 8; //Length of expected secret key to receive over 433MHz radio


// Globals
float voltages[noOfAnalogPins];
float checksum;
byte incomingByte;
uint8_t secretKey[lengthOfRadioKey]; 
uint8_t secretKeyLen = sizeof(secretKey);

// Button pins are given by RPi, presume less than 10 buttons will be used
int buttonPins[10] = {0};
unsigned long lastButtonPress = 0;
unsigned long debounceDelay = 1000;

RH_ASK rf_driver;

void setup()
{
    // Use external analog reference and put a jumper between pins 3.3V and AREF
    analogReference(EXTERNAL);
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
    // Initialize the ASK receiver
    rf_driver.init();
    // Get the radio receiver secret key from the RPi
    getRadioKey();
}


void loop()
{
    // Read analog pins and send data if requested over serial
    if (Serial.available() > 0)
    {
        incomingByte = Serial.read();
        if(incomingByte == 'V')
        {
            sendAnalogVoltages();
        }
    }
    // Check if radio message has been received
    // Set buffer to size of expected message
    uint8_t buf[lengthOfRadioKey];
    uint8_t bufLen = sizeof(buf);
    if (rf_driver.recv(buf, &bufLen))
    {
        if (compareKeys(&secretKey[0], &buf[0], lengthOfRadioKey))
        {
            Serial.println('O'); // Send capital 'O' to rpi to open the gate
            Serial.println("Radio received correct passphrase");
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
    int smoothSamples = 20;

    // Set all Analog values to zero
    for(int i=0; i<noOfAnalogPins; i++)
    {
        voltages[i] = 0.0;
    }

    // Get mean of analog readings
    for(int s=0; s<smoothSamples; s++)
    {
        for(int i=0; i<noOfAnalogPins; i++)
        {
            voltages[i] += analogRead(i);
        }
        delay(1);
    }

    // Divide by number of samples to get the mean, then multiply by 3.3/1023 to get voltage
    for(int i=0; i<noOfAnalogPins; i++)
    {
        voltages[i] = (voltages[i] / smoothSamples) * (3.3 / 1023.0);
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


void getRadioKey()
{
    // Send an 'R' to request the secret key
    flushSerialInputBuffer();
    Serial.println('R');
    int i=0;
    while (i<lengthOfRadioKey)
    {
        Serial.println("Getting key char");
        // Wait for serial packets
        while (Serial.available() <= 0)
        {
            Serial.println("waiting for next char");
            delay(1000);
        }
        incomingByte = Serial.read();
        // Check byte is a valid character
        if (incomingByte < '0')
        {
            continue;
        }
        else
        {
            secretKey[i] = incomingByte;
            i++;
        }
        
    }
    Serial.print("Received the radio key: ");
    for(int i=0; i<lengthOfRadioKey; i++){Serial.print(char(secretKey[i]));}
    Serial.println();
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
    for (int i=0; i<10; i++)
    {
        if (buttonPins[i] > 0)
        {
            pressed = !digitalRead(buttonPins[i]);
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


bool compareKeys(uint8_t key1[], uint8_t key2[], int keys_length)
{
    for (int i=0; i<keys_length; i++)
    {
        if (key1[i] == key2[i])
        {
            continue;
        }
        else
        {
            return false;
        }
    }
    return true;
}
