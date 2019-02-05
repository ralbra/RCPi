# RCPi

This project aims to control your RC car, plane, boat or whatever with a standard PS3 controller and a raspi zerow or Raspi 3. Actually it would work with any wireless controller that is supported by rasbian but i will concentrate on the ps3 controller because I only got this.

# Install
## 0. Prequisite
I Assume u are on the latest version of raspbian (stretch atm)
I recommend using the raspbian stretch lite version

Install some stuff:
`sudo apt-get update`

`sudo apt-get -y install bluez bluez-cups bluez-hcidump bluez-tools bluez-firmware checkinstall libusb-dev libbluetooth-dev`

`sudo apt-get install git joystick pkg-config`
## 1. Connect PS3 Controller

Firstly we need a tool tool to pair the controller:
```
cd ~
wget http://www.pabr.org/sixlinux/sixpair.c
gcc -o sixpair sixpair.c -lusb
```

now connect ps3 controller via usb

`sudo reboot`

wait, login and:

`sudo ~/sixpair`

Something like this should come up

> Current Bluetooth master: 00:00:00:00:00:00
> Setting master bd_addr to 00:15:83:0c:bf:eb

Now disconnect controller.

Bluetooth connection RetroPie sixad variant:

Secondly install sixad to connect to the controller:

```
cd ~
git clone https://github.com/RetroPie/sixad.git
cd ~/sixad
sudo make
sudo mkdir -p /var/lib/sixad/profiles
sudo checkinstall
```

to make sure stop the demaon

`sudo sixad --stop`

and then start again

`sudo sixad --start`

Now press the PS button on your controller.

After a short rumble and the "1" LED should light up after a few seconds.

Lets put the deamon in autostart:

`sudo cp sixad /etc/init.d/`

`sudo update-rc.d sixad defaults`

`sudo reboot`

after reboot press mid button again to activate again, "1" LED should light up after a few seconds.

To check if the controller is present and to get device number type:

`ls /dev/input/js*`

To test the connection, get axis and button numbering and so on:

`jstest /dev/input/js0`

	
## 2. Install pigpio

```
wget abyz.me.uk/rpi/pigpio/pigpio.zip
unzip pigpio.zip
cd PIGPIO
make
sudo make install
```

## 3. Programming

`sudo apt-get -y install python-pygame`
You always have to make sure pigpiod service runs before starting up the code. Start rcpi like any other Python program.
```
sudo pigpiod
cd ~
sudo python rcpi.py
```

Eventually usefull for testing controller reconnect:
`sudo invoke-rc.d bluetooth restart`

## 4. Autostart 

`sudo nano /etc/rc.local`
insert before exit 0
```
pigpiod &
python /home/pi/rcpi.py &
```
## 5. Make SD-Card read only
well we want to make our pi to be plug and play and more importantly unplug
so to not damage the sd card we should make it read only

**But first things first: do a backup of your current sd card**
[How to Backup](https://thepihut.com/blogs/raspberry-pi-tutorials/17789160-backing-up-and-restoring-your-raspberry-pis-sd-card)


After that we can begin:

```
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/read-only-fs.sh
sudo bash read-only-fs.sh
```

Enable boot-time read/write jumper
I chose GPIO 1
Install GPIO-halt utility
I chose GPIO 12
No watchdog, if this happens while you drive it's actually to late to reboot... 

For further information see this link: [How to read only by adafruit](https://learn.adafruit.com/read-only-raspberry-pi/)
