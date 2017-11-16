#include <Servo.h>

// Check this for reference - especially about calibration
// https://dronesandrovs.wordpress.com/2012/11/24/how-to-control-a-brushless-motor-esc-with-arduino/

Servo f_esc, f_servo, r_esc, r_servo;
int compile_test_var = 0;

int incoming[2];

void setup() {
  f_esc.attach(compile_test_var);
  f_servo.attach(compile_test_var);
  r_esc.attach(compile_test_var);
  r_servo.attach(compile_test_var);
  Serial.begin(9600);
}

void loop() {
  // Get two values
  while(Serial.available() > 3)
    for(int i = 0; i < 2; i++){
      // This will need to be calibrated
      incoming[i] = map(Serial.read(), -100, 100, 0, 179);
    }
    // Check these
    f_esc.write(incoming[0]);
    r_esc.write(map(incoming[0], 0, 179, 179, 0));
    f_servo.write(incoming[1]);
    r_servo.write(map(incoming[1], 0, 179, 179, 0));
}
