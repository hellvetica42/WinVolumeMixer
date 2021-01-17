const int volPins[5] = {2, 1, 0, 5, 4}; //first is master
float values[5] = {0,0,0,0,0};
float tolerance = 0.03;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  delay(1000);
}

bool changed(float* v){
  for(int i = 0; i < 5; i++){
    if(v[i] > values[i]+tolerance || v[i] < values[i]-tolerance){
      return true;
    }
  }
  return false;
}

void loop() {
  // put your main code here, to run repeatedly:
  float potValues[5];
  for(int i = 0; i < 5; i++){
    potValues[i] = (float)analogRead(volPins[i])/726.0;
    potValues[i] = ((int)(potValues[i] * 100))/100.0;
    if(i==3){
      potValues[i] = 0;    
    }
  }
  if(changed(potValues)){
    for(int i = 0; i < 5; i++){
      values[i] = potValues[i];
      if(values[i] < tolerance){
        
        values[i] = 0.00;
      }
      if(values[i] > 1.0-tolerance){
        values[i] = 1.00;
      }
      Serial.print(values[i]);
      Serial.print(":");
    }
    Serial.println("");
  }
  delay(50);
  
}
