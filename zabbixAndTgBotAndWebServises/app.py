from flask import Flask, request, render_template_string, jsonify
import paho.mqtt.client as mqtt
import os
from datetime import datetime

app = Flask(__name__)

NODE_NAME = os.getenv('NODE_NAME', 'unknown_node')
BROKER = '172.25.0.3'
MY_TOPIC = f"nodes/{NODE_NAME}"

received_messages = []

def on_message(client, userdata, msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    received_messages.append(f"[{timestamp}] {msg.payload.decode()}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, NODE_NAME)
client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.subscribe("nodes/#")
client.loop_start()

@app.route('/messages')
def get_messages():
    # Повертаємо повідомлення у зворотному порядку для списку
    return jsonify(msgs=received_messages[::-1])

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        target = request.form.get('target')
        msg_text = request.form.get('message')
        if target and msg_text:
            full_message = f"Від {NODE_NAME} для {target}: {msg_text}"
            client.publish(MY_TOPIC, full_message)
        return '', 204 # Повертаємо порожню відповідь, щоб сторінка не перевантажувалась при відправці

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vuzol {{ name }}</title>
        <style>
            body { background: #0f172a; color: #f1f5f9; font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; padding: 40px; }
            .card { background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3); width: 100%; max-width: 500px; border: 1px solid #334155; }
            h2 { color: #38bdf8; margin-top: 0; border-bottom: 2px solid #334155; padding-bottom: 10px; }
            input { width: 100%; padding: 12px; margin: 10px 0; border-radius: 6px; border: 1px solid #334155; background: #0f172a; color: white; box-sizing: border-box; }
            button { width: 100%; padding: 12px; border-radius: 6px; border: none; background: #38bdf8; color: #0f172a; font-weight: bold; cursor: pointer; }
            .msg-list { margin-top: 20px; background: #0f172a; border-radius: 6px; padding: 10px; height: 200px; overflow-y: auto; border: 1px solid #334155; }
            .msg-item { font-size: 0.9rem; padding: 5px 0; border-bottom: 1px solid #1e293b; color: #94a3b8; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Вузол: {{ name }}</h2>
            <form id="msgForm">
                <label>Отримувач:</label>
                <input type="text" name="target" id="target" placeholder="Наприклад: web2" required>
                <label>Повідомлення:</label>
                <input type="text" name="message" id="message" placeholder="Введіть текст..." required>
                <button type="submit">Надіслати через шлюз</button>
            </form>
            <div class="msg-list" id="msgContainer">
                </div>
        </div>

        <script>
            // Відправка форми без перезавантаження сторінки
            document.getElementById('msgForm').onsubmit = async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                await fetch('/', { method: 'POST', body: formData });
                document.getElementById('message').value = ''; // Очищуємо тільки поле повідомлення
            };

            // Функція фонового оновлення повідомлень
            async function updateMessages() {
                try {
                    const response = await fetch('/messages');
                    const data = await response.json();
                    const container = document.getElementById('msgContainer');
                    container.innerHTML = data.msgs.map(m => '<div class="msg-item">' + m + '</div>').join('');
                } catch (e) { console.error("Помилка оновлення:", e); }
            }

            setInterval(updateMessages, 2000); // Оновлюємо список кожні 2 секунди
            updateMessages(); // Перший запуск
        </script>
    </body>
    </html>
    """
    return render_template_string(html, name=NODE_NAME)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
