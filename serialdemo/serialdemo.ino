void setup()
{
  Serial.begin(115200);
  pinMode(33,OUTPUT);
  digitalWrite(33,LOW);
}
void loop() {
  // see if there's incoming serial data:
  if (Serial.available() > 0) {
    // read the oldest byte in the serial buffer:
    int state = Serial.parseInt();
    Serial.println(state);
    
    if (state== 1) {
      digitalWrite(33, HIGH);
      Serial.println("turning on");
      delay(2000);
    }
    else if( state==2 )
    {
      digitalWrite(33, LOW);
      Serial.println("turning off");
    }
    
  }
  else
  {
    Serial.println("No data");
      
  }
  delay(500);
}
