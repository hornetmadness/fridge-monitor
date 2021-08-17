# Fridge-Monitor

This is simple python script to gather the temperature of a refrigerator and tools for moniutoring and alerting

## Features
- A rolling winndow used for creating an average
- Supports the DS18B20 [Temperature Sensor] (or any temp sensor that W1ThermSensor supports)
- Displays current results to [OLED] display
- Contains [monit] and [systemd] config files

I built this on a [Raspberry Pi] Zero W using [Raspberry Pi OS]. I would assume any device that support the python libs, [1 Wire], and [i2c] protocol would work.

## PI Setup
The [OLED] tutorial prety much tells you what you need to do. I also suggest adding the following to the /boot/config.txt
```sh
echo "dtoverlay=w1-gpio" >> /boot/config.txt
```
[Raspberry Pi] -  [Pinout]
Plug the data wire from the [Temperature Sensor] into GPIO4 (pin 7)
Plug the Ground wire from the [Temperature Sensor] into GND (pin 9)
Plug the VCC wire from the [Temperature Sensor] into 3.3v power (pin 17)

## Configuation envionemnt variables
These are the only configuration vars and it default thats are supported
```
MAX_AGE = 300  #Rolling window
RESULTS_FILE = /run/user/1000/temp_results  #Where to write the current result to
```
## License
MIT

Checkout [my BLOG], I've been known to update it from time to time.

   [Temperature Sensor]: https://www.amazon.com/gp/product/B08RJ59BDJ
   [OLED]: https://www.adafruit.com/product/3527
   [OLED Setup]: https://learn.adafruit.com/adafruit-pioled-128x32-mini-oled-for-raspberry-pi/usage
   [i2c]: https://www.circuitbasics.com/basics-of-the-i2c-communication-protocol/
   [my BLOG]: https://syslinux.info
   [monit]: https://mmonit.com/monit/
   [systemd]: https://www.freedesktop.org/wiki/Software/systemd/
   [Raspberry Pi]: https://www.raspberrypi.org/products/raspberry-pi-zero-w/
   [Raspberry PI OS]: https://www.raspberrypi.org/software/operating-systems/
   [1 Wire]: https://www.maximintegrated.com/en/design/technical-documents/tutorials/1/1796.html
   [Pinout]: https://i.stack.imgur.com/yHddo.png

