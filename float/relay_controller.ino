//The sole purpose of the arduino is to handle all interaction with the relay board

int state = 0;
int motionstate = 0;

//int ontime = 25;
//int offtime = 75;
int ontime = 50;
int offtime = 75;
bool usestate = false;
int pin1 = 3;
int pin2 = 4;

void setup() {
  Serial.begin(115200);

  pinMode(pin1, OUTPUT);
  pinMode(pin2, OUTPUT);

  digitalWrite(pin1, HIGH);
  digitalWrite(pin2, HIGH); 
}
void in(int wt){
  digitalWrite(pin1, HIGH);
  digitalWrite(pin2, LOW);
  delay(wt);
}

void stall(int wt){
  digitalWrite(pin2, HIGH);
  digitalWrite(pin1, HIGH);
  delay(wt);
}

void out(int wt){
  digitalWrite(pin1, LOW);
  digitalWrite(pin2, HIGH);
  delay(wt);
}

void float_profile(){
  all_in();
  stall(15*1000);
  all_out();
}
//6pin1, 73
void handle_state(int ton, int toff){
  if (usestate == true){
    int _ton = ton*10;
    int _toff = toff*10;
    if (state == 0){
      stall(100);
    }
    if (state == 1){
      if (motionstate == 0){
        out(_ton);
        motionstate = 1;
      }
      if (motionstate == 1){
        stall(_toff);
        motionstate = 0;
      }
    }
    
    if (state == 2){
      if (motionstate == 0){
        in(_ton);
        motionstate = 1;
      }
      if (motionstate == 1){
        stall(_toff);
        motionstate = 0;
      }
    }
  }
}

void all_in(){
  for (int i=0; i<=54; i++){
    state = 2;
    handle_state(ontime, offtime);
  }
}

void all_out(){
  for (int i=0; i<=54; i++){
    state = 1;
    handle_state(ontime, offtime);
  }
}

void stutter_in(){
  state = 2;
  handle_state(ontime, offtime);
}

void stutter_out(){
  state = 1;
  handle_state(ontime, offtime);
}

void loop(){
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    Serial.print("You sent me: ");
    Serial.println(data);

    if (data == "s"){
      usestate=false;
      stall(0);
    }
    if (data == "o"){
      usestate = true;
      state = 1;
    }
    if (data == "i"){
      usestate = true;
      state = 2;
    }
    if (data == "u"){
      usestate=false;
      all_out();
    }
    if (data == "d"){
      usestate=false;
      all_in();
    }
    if (data == "p"){
      usestate=false;
      float_profile();
    }
    if (data == "d"){
      usestate=false;
      out(0);
    }
    if (data == "a"){
      usestate=false;
      in(0);
    }
  }
  handle_state(ontime, offtime);
}