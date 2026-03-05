import paho.mqtt.client as mqtt
from flask import Flask, render_template_string
import threading
from datetime import datetime
from collections import deque

app = Flask(__name__)
# Використовуємо deque для стабільної історії
history = deque(maxlen=100)

BROKER = '172.25.0.3'
TOPIC = "#"

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "sender": msg.topic,
            "content": payload
        }
        history.append(entry)
    except Exception as e:
        print(f"Error: {e}")

def start_mqtt():
    # Виправлення для paho-mqtt 2.0+
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "logger_v3")
    client.on_message = on_message
    try:
        client.connect(BROKER, 1883, 60)
        client.subscribe(TOPIC)
        client.loop_forever()
    except Exception as e:
        print(f"MQTT Error: {e}")

@app.route('/')
def index():
    html = """
    <html>
        <head>
            <title>MQTT Monitor</title>
            <style>
                body { background: #0f172a; color: #f1f5f9; font-family: sans-serif; padding: 20px; }
                .container { max-width: 800px; margin: auto; }
                table { width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 8px; overflow: hidden; }
                th, td { padding: 12px; border-bottom: 1px solid #334155; text-align: left; }
                th { background: #334155; color: #38bdf8; font-size: 0.8rem; text-transform: uppercase; }
                .sender { color: #fbbf24; font-family: monospace; font-weight: bold; }
                h2 { color: #38bdf8; text-align: center; }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>📊 Історія повідомлень (Postman)</h2>
                <table>
                    <thead>
                        <tr>
                            <th width="20%">Час</th>
                            <th width="30%">Топік</th>
                            <th>Повідомлення</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for item in history|reverse %}
                        <tr>
                            <td>{{ item.time }}</td>
                            <td class="sender">{{ item.sender }}</td>
                            <td>{{ item.content }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            <script>setTimeout(function(){ location.reload(); }, 2000);</script>
        </body>
    </html>
    """
    return render_template_string(html, history=list(history))

if __name__ == "__main__":
    threading.Thread(target=start_mqtt, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
