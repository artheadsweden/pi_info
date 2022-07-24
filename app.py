import json

from flask import Flask, render_template
from controller import get_next_mail_date, get_next_garbage_date, get_current_weather, radio_info, day_info

app = Flask(__name__)

def update():
    weather_data = get_current_weather()
    mail_date = get_next_mail_date()
    garbage_date = get_next_garbage_date()
    radio = radio_info()
    today = day_info()
    return weather_data, mail_date, garbage_date, radio, today

@app.get('/')
def index():
    weather_data, mail_date, garbage_date, radio, today = update()

    return render_template('index.html',
                           weather_data=weather_data,
                           mail_date=mail_date,
                           garbage_date=garbage_date,
                           radio=radio,
                           today=today)


@app.get('/update')
def get_update():
    weather_data, mail_date, garbage_date, radio, today = update()
    data = {
        'weather': weather_data,
        'mail_date': mail_date,
        'garbage_date': garbage_date,
        'radio': radio,
        'today': today
    }
    return json.dumps(data)


if __name__ == '__main__':
    app.run()