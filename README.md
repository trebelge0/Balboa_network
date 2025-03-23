# Balboa swarm communication using RPi's

This repository contains a communication platform between a Balboa swarm. 
A RPi is shielded on each Balboa.
There are two communication protocole used in it:
I²C communication between RPi and Balboa
and a RFCOMM Bluetooth communication between each RPis
#
## System, communication & peripherals
### RPi - Balboa Communication: I²C
The master is the RPi, it has 4 slaves:
* Balboa
* IMU
* Magnetometer (not used)
* OLED screen

The Balboa manage encoders and push button reading as well as leds setting.
IMU measure acceleration and angular speed for the 3-axis.

The RPi manages the control loop by requesting information from Balboa and IMU via I²C.

#### balboa.py
Class that allows RPi to request/write information from/to Balboa using I²C communication such as:
* Encoder values (read)
* Push button (read)
* Battery level (read)
* Buzzer (write)
* Leds (write)
* Motor speed (write)

#### lsm6.py
Class that allows RPi to request information from IMU using I²C communication such as:
* Acceleration[3]
* Gyroscope[3]

#### balance.py
Run control algorithm in a separate thread.

### RPi Network communication: Bluetooth
#### bluetooth.py
Class that allows RPi's to communicate between them providing:
* **RPi's MAC address list**
* **ID** of the current RPi corresponding of its index in the RPi's MAC address list.
* **Adjacency matrix**: Symmetric square matrix containing edges in the RPi's graph.

Two steps are performed, after having successfully setup devices beforehand as explained in the next section.

**1. Connection**
* Neighbors are set based on adjacency matrix
* Connection need to be made in only 1 way: lower MAC address connect to higher MAC address
* As soon as a connection is made, a thread is listening incoming messages for this connection.

**2. Communication**
* **Bidirectionnal**
* *send_message(self, type, \*args)* send args converted in hexadecimal based on the specified type following the *struct* library.
* *handle_client(self, conn, addr)* is run by a separate thread for each connection. For example if a RPi is connected to 3 other RPi,
there will be 3 threads running this function.
* Last message is stored in *bluetooth.buffer* in hexadecimal format. This buffer has length corresponding to *bluetooth.RPI_MACS*.


### Balboa (Arduino)
#### BalboaRPiSlave.ino
It is constantly reading encoders values and push buttons states. 
It sends data requested by RPi via I²C and write received data from the RPi.

#
## Setup & configuration
### RPi's
I use an ssh connection with each of my RPi's using a mobile hotspot because RPi's cannot connect to eduroam.

### Bluetooth
Before the first communication, you should run:
```bash

sudo sdptool add SP
sudo sdptool browse local
```
The last command is supposed to show Serial Port to enable RFCOMM communication.

It may give you an **error**, then run:
```bash

sudo nano /etc/systemd/system/dbus-org.bluez.service
```
And add --compat to the following line:
```bash

ExecStart=/usr/lib/bluetooth/bluetoothd --compat
```
Then run:
```bash

sudo systemctl daemon-reload
sudo systemctl restart bluetooth
```

Try again to enable RFCOMM Serial Port with sdptool.

Before the first connection, devices that need to connect are needed to be paired first. 
You should use VNC or an HDMI monitor on both devices in order to accept the pair request with corresponding PIN.

In parrallel, on both RPi's, run:
```bash

bluetoothctl
```
On the first RPi, run
```bash

discoverable on
pairable on
```
On the other RPi, run
```bash

scan on
pair <MAC_RPi_1>
```
Accept the pair request on the screen using VNC or a monitor. 
Devices are now paired and will be able to connect using python at each future boot.

If you got permission errors, try running:
```bash

sudo usermod -aG bluetooth $USER
newgrp bluetooth
```

### I²C
RPi's are shielded on Balboa using pin headers. Balboa includes a level shifter connected between SDA/SCL from Arduino and RPi.
IMU and magnetometer are connected on the bus via the Balboa as well.

I²C can be activated using :
```bash

sudo raspi-config
```

I²C speed can be set for the RPi in the following file:
```bash

sudo nano /boot/firmware/config.txt
```
Then, modify this line like this to set a baudrate of 100kHz.
```bash

dtparam=i2c_arm=on,i2c_arm_baudrate=100000
```
You may need to set 200 kHz for RPi 4b and some other RPi versions to get actually approximately 100 kHz due to CPU scaling.

A delay is set on the Balboa (slave) side in BalboaRPISlave.ino, 10 is supposed to work for 100 kHz, 
but you could put it to 15 or 20 if you get I²C I/O errors.
```C
PololuRPiSlave<struct Data,20> slave;
```

#
## Examples
For these examples, bluetooth and I²C communication need to be setup before the first use as described in the previous section.

Each of these example has a function that translate *bluetooth.buffer* from hexadecimal to specified types. 
The result is stored in another buffer owned by the related class.

### Consensus
A consensus algorithm will make the RPi's to converge toward the same value without direct communication.

This example contains an algorithm that performs the average between each RPi's value and its neighbors values that have been sent via Bluetooth.
```
Usage: python script.py <ID> <init_state> <i2c>
```
ID is the index of the current RPi in bluetooth.RPIS_MACS, init_state is the initial value of the current RPi and i2c is
set to 0 when the RPi is not shielded on the Balboa, 1 otherwise to use leds to observe convergence.

Inside main_consensus.py, you should change the following lines corresponding to your own setup:
* **RPIS_MACS** need to be set according to you own setup in main_consensus.py
* **ADJACENCY** need to be set according to the connections you want to set.

The format of the buffer used in this example is [[iteration_1, value_1], ..., [iteration_n, value_n]]. 
It is created based on *bluetooth.buffer* thanks to the function *consensus.get_consensus()* that translate hexadecimal into wanted format.

If RPi's are shielded on the Balboa's and i2c parameter is not set to 0, leds from the Balboa should blink at the frequency corresponding to the current value of the RPi's.

### StandUp
This example will make the Balboa stand up like dominos. If a Balboa is down and one of its neighbors is up, it will stand up.
```
Usage: python main_standup.py <ID>
```
ID is the index of the current RPi in bluetooth.RPIS_MACS

Inside main_standup.py, you should change the following lines corresponding to your own setup:
* **RPIS_MACS** need to be set according to you own setup in main_consensus.py
* **ADJACENCY** need to be set according to the connections you want to set.


#
## Scripts

I created 2 bash scripts that aim to facilitate and accelerate the testing process of the system. 
Indeed, uploading each file manually using Filezilla with different parameters and executing each of them separately on each RPi could take time.

These scripts allow the user to do that with only 2 commands.
Before running these scripts, make sure the execution permission is set or run:
```bash

sudo chmod +x ./deploy.sh
```

### deploy.sh
This script can be used instead of **Filezilla** to transfer files faster and easier.

This script allows the user to transfer the same files to several RPi on the same LAN network using scp.
It is especially useful when working with a lot of RPi

```
Usage: ./deploy.sh <IP1> <IP2> ... <IPn>
```

Inside deploy.sh, you should change the following lines corresponding to your own setup:
* **LOCAL_DIR** must be set as the PC side directory containing all files to transfer.
* **REMOTE_DIR** must be as the RPi side directory that will contain transferred files
* **USER** is the RPi user used to connect via ssh
* **SSH_KEY** can contain the path to an ssh key to avoid being asked to type ssh password

### run.sh
This script can be used to run the same program on several RPi's via ssh.
It allows the user to specify the python file to run as well as args.

```
Usage: ./run.sh <python_program> <IP1>:<param1>,<param2>,... <IP2>:<param1>,<param2>,...
```

The first argument given to the python file MUST be its ID among bluetooth.RPIS_MACS.
User do not need to type it for each RPi, it is automatic: the first IP will run python program with ID 0.

Inside run.sh, you should change the following lines corresponding to your own setup:
* **USER** is the RPi user used to connect via ssh
* **SSH_KEY** can contain the path to an ssh key to avoid being asked to type ssh password

For example, consensus example can be run for 3 RPi's with this single command : 
```bash

./run.sh /home/trebelge/Documents/synchro/Bluetooth/main_consensus.py 192.168.1.37:10.0,0 192.168.1.35:3.0,0 192.168.1.17:5.0,0
```
