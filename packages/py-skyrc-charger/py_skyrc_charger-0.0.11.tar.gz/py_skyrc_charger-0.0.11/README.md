
# py skyrc charger

this package allows to interface with skyrc chargers using the usb-connection as a more flexible replacement for the *Charge Master* software.
This library was created by reverse engineering the protocol and does not support the complete set of functions yet.

## supported devices

this code was developed and tested using the SkyRC T1000: https://www.skyrc.com/t1000
however chargers working with the original Charge Master software are likely to work as well. A list of supported devices is on the download page of Charge Master: https://www.skyrc.com/downloads

**tested on linux only**, windows should also work, but it is more difficult to setup the usb driver

# setup (linux)

## fix usb permissions

this might be necessary to run the code without sudo.

create a file `/lib/udev/rules.d/50-skyrc-t1000.rules` with the following content:
```bash
ACTION=="add", SUBSYSTEMS=="usb", ATTRS{idVendor}=="0000", ATTRS{idProduct}=="0001", MODE="660", GROUP="plugdev"
```

run:
```bash
sudo adduser $USER plugdev
```

# how to use

```python
import time
from py_skyrc_charger import Charger, Config, Action, ChargerResponse


def rec_data_callback_sample(data: ChargerResponse):
    print("---")
    print(f"got cmd: {data.command}")
    if data.is_error:
        print(f"error: {data.error_str}")
    else:
        print(f"got data: {data.data}")


if __name__ == "__main__":
    charger = Charger(rec_data_callback_sample, device_index=0)
    charger.connect()

    time.sleep(1.0)

    print("read version...")
    charger.poll_version()
    time.sleep(0.2)

    print("read settings...")
    charger.poll_settings()
    time.sleep(0.2)

    # configure charge program
    conf = Config(port=1,
                  action=Action.BALANCE,
                  cells=3,
                  cur_in=0.1,
                  cur_out=0.5)

    # read values in idle
    start_time = time.time()
    while time.time() - start_time < 5:
        charger.poll_all_vals()
        time.sleep(1.0)

    print("START")
    charger.start_program(conf)

    # read values while charging
    start_time = time.time()
    while time.time() - start_time < 10:
        charger.poll_all_vals()
        time.sleep(1.0)

    print("STOP")
    charger.stop_program(conf.port)

    # read values in idle
    start_time = time.time()
    while time.time() - start_time < 10:
        charger.poll_all_vals()
        time.sleep(1.0)

```
