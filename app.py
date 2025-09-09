from flask import Flask, render_template, request, jsonify
from datetime import datetime
import os
import requests

from flask_mail import Mail, Message
import config

app = Flask(__name__)

# Flask-Mail config
app.config['MAIL_SERVER'] = config.MAIL_SERVER
app.config['MAIL_PORT'] = config.MAIL_PORT
app.config['MAIL_USE_TLS'] = config.MAIL_USE_TLS
app.config['MAIL_USERNAME'] = config.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = config.MAIL_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = config.MAIL_DEFAULT_SENDER

mail = Mail(app)

# Telegram Bot
BOT_TOKEN = config.BOT_TOKEN
CHAT_ID = config.CHAT_ID

# Upload folder (if needed)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# In-memory storage
events_data = []
messages_data = []

# ----------------- Routes -----------------
@app.route('/')
def index():
    return render_template('index.html')

# Contact API: send email + telegram
@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    subject = data.get('subject', 'No Subject')
    message_text = data.get('message')

    # Store message in memory
    message = {
        'id': len(messages_data) + 1,
        'name': name,
        'email': email,
        'subject': subject,
        'message': message_text,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    messages_data.append(message)

    # -------- Send Email --------
    try:
        msg = Message(
            subject=f"Contact Form: {subject} from {name}",
            recipients=[app.config['MAIL_USERNAME']],
            body=f"Name: {name}\nEmail: {email}\nMessage:\n{message_text}"
        )
        mail.send(msg)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Email failed: {str(e)}'})

    # -------- Send Telegram --------
    try:
        telegram_msg = f"📩 New Contact Message\nName: {name}\nEmail: {email}\nMessage: {message_text}"
        requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            params={'chat_id': CHAT_ID, 'text': telegram_msg}
        )
    except Exception as e:
        return jsonify({'success': False, 'message': f'Telegram failed: {str(e)}'})

    return jsonify({'success': True, 'message': 'Message sent successfully!'})

# Other routes (events, pages, etc.) remain the same
@app.route('/api/events', methods=['GET', 'POST'])
def events():
    global events_data
    if request.method == 'POST':
        event = {
            'id': len(events_data) + 1,
            'title': request.json.get('title'),
            'date': request.json.get('date'),
            'description': request.json.get('description'),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        events_data.append(event)
        return jsonify({'success': True, 'event': event})
    return jsonify(events_data)

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    global events_data
    events_data = [e for e in events_data if e['id'] != event_id]
    return jsonify({'success': True})

@app.route('/pro_photoshop')
def pro_photoshop():
    return render_template('pro_photoshop.html')

@app.route('/pro_ai')
def pro_ai():
    return render_template('pro_ai.html')

@app.route('/myevent')
def myevent():
    return render_template('event.html')

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/my_contact')
def my_contact():
    return render_template('contect.html')


if __name__ == '__main__':
    app.run(debug=True)
