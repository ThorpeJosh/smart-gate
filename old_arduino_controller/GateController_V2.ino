//Front Gate code

//pins
const int m1 = 11;
const int m2 = 10;
const int b1 = 2;  //box button
const int b2 = 4;  //outside button
const int b3 = 7;   //inside button
const int shuntPin = A0;

//paramaters
const int shuntThresh = 6;
const int maxTimeToOpen = 60000;
const int maxTimeToClose = 60000;
const int holdOpenSeconds = 20;
const int currentSpike = 800; //ms

//Flags
boolean hitOpen = 0;
boolean hitClose = 0;
boolean timeLapse = 0;

//vars
unsigned long startMillis =0;


void setup() {
  Serial.begin(9600);
  Serial.println("initializing");
  pinMode(m1, OUTPUT);
  pinMode(m2, OUTPUT);
  pinMode(shuntPin, INPUT);
  pinMode(b1,INPUT);
  pinMode(b2,INPUT);
  pinMode(b3,INPUT);
  digitalWrite(m1,HIGH);
  digitalWrite(m2,HIGH);
  digitalWrite(b1,HIGH);
  digitalWrite(b2,HIGH);
  digitalWrite(b3,HIGH);
  closeGate();
  delay(3000);
}

void loop() {
  Serial.println("waiting for button push");
  if(buttonTest()){
    openGate();
    Serial.println("delaying to let car through");
    delay(holdOpenSeconds*1000);
    closeGate();
  }
}

void stopGate(){
  digitalWrite(m1,HIGH);
  digitalWrite(m2,HIGH);
}

void openGate(){
  startMillis = millis();
  //start motor prior to testing the shunt so that stall current isn't detected
  digitalWrite(m1,HIGH);
  digitalWrite(m2,LOW);
  delay(currentSpike);
  while(!hitOpen && !timeLapse){  
    if(getCurrent()> shuntThresh){hitOpen =1;}
    //if(millis() > ((maxTimeToOpen*1000) + startMillis )){timeLapse =1;}
    Serial.print("Opening Gate: hitOpen timeLapse "); Serial.print(hitOpen); Serial.print(timeLapse);Serial.print("  TIME (ms) = ");Serial.println(millis()-startMillis);
  }
  Serial.println("Exiting openGate");
  stopGate();
  flagReset();
}

void closeGate(){
  startMillis = millis();
  timeLapse=0;
  //start motor prior to testing the shunt so that stall current isn't detected
  digitalWrite(m1,LOW);
  digitalWrite(m2,HIGH);
  delay(currentSpike);
  while(!hitClose && !timeLapse){  
    if(getCurrent()> shuntThresh){hitClose =1;}
    //if(millis() > ((maxTimeToOpen*1000) + startMillis )){timeLapse =1;}
    Serial.print("Closeing Gate: hitClose timeLapse "); Serial.print(hitClose); Serial.print(timeLapse);Serial.print("  TIME (ms) = ");Serial.println(millis()-startMillis);
  }
  Serial.println("Exiting closeGate");
  stopGate();
  flagReset();
}

int getCurrent(){
  int shuntVal = 0;
  int n=50;
  int x[n];
  int sum = 0;
  for(int i=0; i<n; i++){
    x[i] = analogRead(shuntPin);
    sum = sum+x[i];
    delay(1);
  }
  shuntVal = sum/n;
  return shuntVal;
}

void flagReset(){
  hitOpen = 0;
  hitClose = 0;
  timeLapse = 0;
}

boolean buttonTest(){
  boolean x = !digitalRead(b1);
  boolean y = !digitalRead(b2);
  boolean z = !digitalRead(b3);
  if(x || y || z){
    Serial.print("b1 = ");
    Serial.println(x);
    Serial.print("b2 = ");
    Serial.println(y);
    Serial.print("b3 = ");
    Serial.println(z);
    return true;
  }
  else{
    return false;
  }
}

