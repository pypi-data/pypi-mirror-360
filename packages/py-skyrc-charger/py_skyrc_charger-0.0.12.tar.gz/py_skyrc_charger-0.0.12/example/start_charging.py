
import time


if True:  # pylint: disable=W0125
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

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
