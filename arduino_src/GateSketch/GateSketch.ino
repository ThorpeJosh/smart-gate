// vim: filetype=cpp
/*Arduino code to communicate with the RPi over serial.
Information shared with RPi includes analog pin voltages and other inputs that trigger the gate.
All analog readings will be smoothed and converted to voltages (floats)

Serial communication contract as follows:

Handshake:
    Arduino sends 'A', RPi responds with 'A'
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

RH_ASK rf_driver;

void setup()
{
    // Use external analog reference and put a jumper between pins 3.3V and AREF
    analogReference(EXTERNAL);
    // start serial at 115200bps
    Serial.begin(115200);
    serialHandshake();
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
    for(int i=0; i<lengthOfRadioKey; i++)
    {
        Serial.println("Getting key char");
        // Wait for serial packets
        while (Serial.available() <= 0)
        {
            Serial.println("waiting for next char");
            delay(1000);
        }
        secretKey[i] = Serial.read();
    }
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
