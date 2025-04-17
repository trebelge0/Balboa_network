#include <Servo.h>
#include <Balboa32U4.h>
#include <PololuRPiSlave.h>
#include <Arduino.h>
#include <HardwareSerial.h>

#define SERIAL_PORT Serial1 // Modifier si besoin
#define BAUD_RATE 115200

/* This example program shows how to make the Balboa 32U4 balancing
 * robot into a Raspberry Pi I2C slave.  The RPi and Balboa can
 * exchange data bidirectionally, allowing each device to do what it
 * does best: high-level programming can be handled in a language such
 * as Python on the RPi, while the Balboa takes charge of motor
 * control, analog inputs, and other low-level I/O.
 *
 * The example and libraries are available for download at:
 *
 * https://github.com/pololu/pololu-rpi-slave-arduino-library
 *
 * You will need the corresponding Raspberry Pi code, which is
 * available in that repository under the pi/ subfolder.  The Pi code
 * sets up a simple Python-based web application as a control panel
 * for your Raspberry Pi robot.
 */

// Custom data structure that we will use for interpreting the buffer.
// We recommend keeping this under 64 bytes total.  If you change the
// data format, make sure to update the corresponding code in
// a_star.py on the Raspberry Pi.

struct Data
{
  bool red, yellow, green;
  bool buttonA, buttonB, buttonC;

  int16_t leftMotor, rightMotor;
  uint16_t batteryMillivolts;
  uint16_t analog[6];

  bool playNotes;
  char notes[14];

  int16_t leftEncoder, rightEncoder;

  uint16_t distance;
  int16_t x, y, z;
};

PololuRPiSlave<struct Data,20> slave;
PololuBuzzer buzzer;
Balboa32U4Motors motors;
Balboa32U4ButtonA buttonA;
Balboa32U4ButtonB buttonB;
Balboa32U4ButtonC buttonC;
Balboa32U4Encoders encoders;

int32_t current_time = millis();
int32_t begin_loop_time = millis();
int DWM_REFRESH_RATE_MS = 1000; 

void setup()
{
  // Set up the slave at I2C address 20.
  slave.init(20);
  Serial.begin(115200);
  SERIAL_PORT.begin(BAUD_RATE);
  // Play startup sound.
  buzzer.play("v10>>g16>>>c16");
  SERIAL_PORT.setTimeout(30);  // Each time DWM is read, the main loop will take at least 30 ms. This is bad for the balancing loop then it need to be minimized.
}

void loop()
{
  // Call updateBuffer() before using the buffer, to get the latest
  // data including recent master writes.
  slave.updateBuffer();

  // Write various values into the data structure.
  slave.buffer.buttonA = buttonA.isPressed();
  slave.buffer.buttonB = buttonB.isPressed();
  slave.buffer.buttonC = buttonC.isPressed();

  // Change this to readBatteryMillivoltsLV() for the LV model.
  slave.buffer.batteryMillivolts = readBatteryMillivolts();

  for(uint8_t i=0; i<6; i++)
  {
    slave.buffer.analog[i] = analogRead(i);
  }

  // READING the buffer is allowed before or after finalizeWrites().
  ledYellow(slave.buffer.yellow);
  ledGreen(slave.buffer.green);
  ledRed(slave.buffer.red);
  motors.setSpeeds(slave.buffer.leftMotor, slave.buffer.rightMotor);

  // Playing music involves both reading and writing, since we only
  // want to do it once.
  static bool startedPlaying = false;
  
  if(slave.buffer.playNotes && !startedPlaying)
  {
    buzzer.play(slave.buffer.notes);
    startedPlaying = true;
  }
  else if (startedPlaying && !buzzer.isPlaying())
  {
    slave.buffer.playNotes = false;
    startedPlaying = false;
  }

  slave.buffer.leftEncoder = encoders.getCountsLeft();
  slave.buffer.rightEncoder = encoders.getCountsRight();

  if (millis() - current_time > DWM_REFRESH_RATE_MS) {
    dwmLocGet();
    current_time = millis();
  }

  // When you are done WRITING, call finalizeWrites() to make modified
  // data available to I2C master.
  slave.finalizeWrites();

  //Serial.print("Loop time: ");
  //Serial.println(millis() - begin_loop_time);
  //begin_loop_time = millis();
}

void hexStr(const uint8_t* data, size_t length) {
    for (size_t i = 0; i < length; i++) {
        if (data[i] < 16) Serial.print("0");
        Serial.print(data[i], HEX);
        Serial.print(" ");
    }
    Serial.println();
}

void error(uint8_t err_code) {
    switch (err_code) {
        case 0: Serial.println("OK"); break;
        case 1: Serial.println("Unknown command or broken TLV frame"); break;
        case 2: Serial.println("Internal error"); break;
        case 3: Serial.println("Invalid parameter"); break;
        case 4: Serial.println("Busy"); break;
        case 5: Serial.println("Operation not permitted"); break;
        default: Serial.println("Unknown error");
    }
}

void dwmLocGet() {
    const uint8_t DWM1001_TLV_TYPE_CMD_LOC_GET = 0x0C;
    const uint8_t TLV_TYPE_RET_VAL = 0x40;
    const uint8_t TLV_TYPE_POS_XYZ = 0x41;
    const uint8_t TLV_TYPE_RNG_AN_DIST = 0x48;
    const uint8_t TLV_TYPE_RNG_AN_POS_DIST = 0x49;

    const uint8_t POS_LEN = 13;
    const uint8_t DIST_LEN = 7;

    uint8_t tx_data[] = {DWM1001_TLV_TYPE_CMD_LOC_GET, 0x00};

    SERIAL_PORT.write(tx_data, sizeof(tx_data));
    
    delay(1);
    
    uint8_t rx_data[100];
    size_t len = SERIAL_PORT.readBytes(rx_data, sizeof(rx_data));
    
    //Serial.print("Received: ");
    //hexStr(rx_data, len);
    
    size_t data_cnt = 0;
    if (rx_data[data_cnt] == TLV_TYPE_RET_VAL) {
        uint8_t err_code = rx_data[data_cnt + 2];
        error(err_code);
        data_cnt += 3;
    }
    
    if (rx_data[data_cnt] == TLV_TYPE_POS_XYZ) {
        data_cnt += 2;
        int32_t x, y, z;
        uint8_t qf;
        memcpy(&x, &rx_data[data_cnt], 4);
        memcpy(&y, &rx_data[data_cnt + 4], 4);
        memcpy(&z, &rx_data[data_cnt + 8], 4);
        qf = rx_data[data_cnt + 12];
        Serial.print("Position: X="); Serial.print(x);
        Serial.print(", Y="); Serial.print(y);
        Serial.print(", Z="); Serial.print(z);
        Serial.print(", QF="); Serial.println(qf);
        data_cnt += POS_LEN;

        slave.buffer.x = x;
        slave.buffer.y = y;
        slave.buffer.z = z;
    }

    if (rx_data[data_cnt] == TLV_TYPE_RNG_AN_POS_DIST) {
      uint8_t an_pos_dist_len = rx_data[data_cnt+1];
      uint8_t an_number = rx_data[data_cnt+2];
      data_cnt += 3;

      for (int i=0; i < an_number; i++) {

          if (an_pos_dist_len) {
              uint16_t d;;
              uint8_t qf;
              int16_t uwb_addr;

              memcpy(&uwb_addr, &rx_data[data_cnt], 2);
              memcpy(&d, &rx_data[data_cnt+2], 4);
              qf = rx_data[data_cnt + 6];
              Serial.print("UWB addr="); Serial.print(uwb_addr);
              Serial.print(", d="); Serial.print(d);
              Serial.print(", QF="); Serial.println(qf);

              slave.buffer.distance = d;

              data_cnt += DIST_LEN;

              int32_t x, y, z;
              memcpy(&x, &rx_data[data_cnt], 4);
              memcpy(&y, &rx_data[data_cnt + 4], 4);
              memcpy(&z, &rx_data[data_cnt + 8], 4);
              qf = rx_data[data_cnt + 12];
              Serial.print("Position: X="); Serial.print(x);
              Serial.print(", Y="); Serial.print(y);
              Serial.print(", Z="); Serial.print(z);
              Serial.print(", QF="); Serial.println(qf);

          }
          data_cnt += POS_LEN;
      }
   }
}
