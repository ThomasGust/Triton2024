//The sole purpose of the arduino is to handle all interaction with the relay board

int state = 0;
int motionstate = 0;

//int ontime = 25;
//int offtime = 75;
int ontime = 50;
int offtime = 75;
bool usestate = false;

void setup() {
  Serial.begin(115200);
  pinMode(6, OUTPUT);
  pinMode(5, OUTPUT);

  digitalWrite(6, HIGH);
  digitalWrite(5, HIGH); 
}
void in(int wt){
  digitalWrite(6, HIGH);
  digitalWrite(5, LOW);
  delay(wt);
}

void stall(int wt){
  digitalWrite(5, HIGH);
  digitalWrite(6, HIGH);
  delay(wt);
}

void out(int wt){
  digitalWrite(6, LOW);
  digitalWrite(5, HIGH);
  delay(wt);
}

void float_profile(){
  all_in();
  stall(15*1000);
  all_out();
}
//66, 73
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