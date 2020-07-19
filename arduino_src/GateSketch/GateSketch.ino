
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
    Arduino sends 'O', followed trigger message, RPi doesn't respond.

*/

const int noOfAnalogPins = 6;
const int voltageDecimalPlaces = 4;
float voltages[noOfAnalogPins];
float checksum;
byte incomingByte;


void setup()
{
    // Use external analog reference and put a jumper between pins 3.3V and AREF
    analogReference(EXTERNAL);
    // start serial at 115200bps
    Serial.begin(115200);
    serialHandshake();
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
