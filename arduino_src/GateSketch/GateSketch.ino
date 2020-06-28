
// vim: filetype=cpp
/*Arduino code to send all analog values of serial to RPi
All analog readings will be smoothed and converted to voltages (flaots)
*/

const int noOfAnalogPins = 6;
float voltages[6];

void setup()
{
    // start serial at 250000bps
    Serial.begin(250000);
    serialHandshake();
}


void loop()
{
    // Read analog pins and send data if requested over serial
    if (Serial.available() > 0)
    {
        // Flush input buffer
        Serial.read();
        updateAnalogVoltages();
        for(int i=0; i<noOfAnalogPins; i++)
        {
            Serial.println(voltages[i]);
        }
    }
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

    // Divide by number of samples to get the mean, then multiply by 5/1023 to get voltage
    for(int i=0; i<noOfAnalogPins; i++)
    {
        voltages[i] = (voltages[i] / smoothSamples) * (5.0 / 1023.0);
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
    // Clear buffer
    while (Serial.available() > 0)
    {
        Serial.read();
    }
}
