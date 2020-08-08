// vim: filetype=cpp 
/* Arduino code to upload to a radio transmitter to remotely open the gate,
when it is within a certain proximity.
Proximity will depend on the quility of the 433MHz transmitter/ receiver pair and their voltages.

Make sure to replace the secret key below with one of your choice (8 characters) and set it for the RPi,
as described in the README */

#include <RH_ASK.h>
#include <SPI.h> // Not actually used but needed to compile

RH_ASK driver;

const char *secretKey = "8CharSec";

void setup()
{
    driver.init();
}

void loop()
{
    driver.send((uint8_t *)secretKey, strlen(secretKey));
    driver.waitPacketSent();
    delay(500);
}
