from flask import Flask, render_template
import RPi.GPIO as GPIO
import threading
import time

app = Flask(__name__)

@app.route("/")
def hello():
    return render_template("index.html")

@app.route("/led/")
def toggle_led():
    global looping
    looping = not looping
    threading.Thread(target=loop_till_false).start()
    return str(looping)

def loop_till_false():
    while looping:
        GPIO.output(23, True)
        time.sleep(0.1)
    GPIO.output(23, False)

if __name__ == "__main__":
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(23, GPIO.OUT)
    looping = False
    app.run(debug=True, host="0.0.0.0")
