from flask import Flask, render_template
import smbus2
import time
from datetime import datetime

app = Flask(__name__)

# I2C Adresse des DHT20
DHT20_I2C_ADDR = 0x38
bus = smbus2.SMBus(1)

def init_dht20():
    """Initialisiert den DHT20 und überprüft, ob er erreichbar ist."""
    try:
        bus.write_byte(DHT20_I2C_ADDR, 0)
        time.sleep(0.1)
    except OSError:
        print("Fehler: DHT20 nicht gefunden! Prüfe die Verkabelung.")
        return False
    return True

def read_dht20():
    """Liest Temperatur und Luftfeuchtigkeit vom DHT20-Sensor aus."""
    try:
        bus.write_i2c_block_data(DHT20_I2C_ADDR, 0xAC, [0x33, 0x00])
        time.sleep(0.08)

        data = bus.read_i2c_block_data(DHT20_I2C_ADDR, 0, 6)

        if (data[0] & 0x80) != 0:
            print("Fehler: Ungültige Sensordaten erhalten")
            return None, None

        humidity_raw = ((data[1] << 12) | (data[2] << 4) | (data[3] >> 4))
        humidity = (humidity_raw / 2**20) * 100

        temp_raw = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
        temperature = (temp_raw / 2**20) * 200 - 50

        return round(temperature, 2), round(humidity, 2)
    except Exception as e:
        print(f"Fehler beim Lesen des Sensors: {e}")
        return None, None

@app.route("/")
def home():
    """Hauptseite mit aktuellen Sensordaten"""
    temperature, humidity = read_dht20()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return render_template("index.html", temperature=temperature, humidity=humidity, timestamp=timestamp)

if __name__ == "__main__":
    if not init_dht20():
        exit(1)

    app.run(host="0.0.0.0", port=5000, debug=True)

