"""
Read water level from a water level sensor and turn on or off a light, depending on the reading
"""
import json
import time

import RPi.GPIO as GPIO

THRESHOLDS = {}
LIGHT_CHANNEL = 27
SENSOR_CHANNEL = 26
GPIO.setmode(GPIO.BCM)
GPIO.setup(LIGHT_CHANNEL, GPIO.OUT)
GPIO.setup(SENSOR_CHANNEL, GPIO.IN)

def wait(seconds=10):
    for second in range(seconds, 0, -1):
        time.sleep(1)
        print(f"{second}.")


def set_thresholds():
    if not THRESHOLDS:
        try:
            with open("thresholds.json") as f:
                thresholds = json.load(f)
                THRESHOLDS.update(thresholds)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            print("Thresholds not set")

    if all(_ in THRESHOLDS for _ in ("high", "low", "med")):
        return

    input("Press enter when the water sensor is connected and not in water")
    THRESHOLDS["low"] = GPIO.input(SENSOR_CHANNEL)

    input("Press enter when the water sensor is connected and immersed in water")
    THRESHOLDS["high"] = GPIO.input(SENSOR_CHANNEL)
    # set the medium threshold
    THRESHOLDS["med"] = (THRESHOLDS["high"] - THRESHOLDS["low"]) / 2

    with open("thresholds.json", "w") as f:
        json.dump(THRESHOLDS, f, indent=2)


def main():
    # test the light
    for state in "on", "off":
        new_state = GPIO.HIGH if state == "on" else GPIO.LOW
        GPIO.output(LIGHT_CHANNEL, new_state)
        light_input = input(f"Is the light {state}? (enter Y/y then press enter)")
        if light_input.lower().strip() != "y":
            raise SystemExit("Check light sensor connections")

    while True:
        reading = GPIO.input(SENSOR_CHANNEL)
        new_state = GPIO.HIGH if reading >= THRESHOLDS["med"] else GPIO.LOW
        GPIO.output(LIGHT_CHANNEL, new_state)
        wait()
        print("Press CTRL+C to quit")


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    set_thresholds()
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
