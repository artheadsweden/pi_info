import json

from flask import Flask, render_template
from controller import get_next_mail_date, get_next_garbage_date, get_current_weather, radio_channels, day_info, now_playing

app = Flask(__name__)

def update():
    weather_data = get_current_weather()
    mail_date = get_next_mail_date()
    garbage_date = get_next_garbage_date()
    channels = radio_channels()
    current_programs = [now_playing(channel['id']) for channel in channels]
    today = day_info()
    return weather_data, mail_date, garbage_date, channels, current_programs, today

@app.get('/')
def index():
    weather_data, mail_date, garbage_date, channels, current_programs, today = update()

    return render_template('index.html',
                           weather_data=weather_data,
                           mail_date=mail_date,
                           garbage_date=garbage_date,
                           channels=channels,
                           today=today,
                           current_programs=current_programs)


@app.get('/update')
def get_update():
    weather_data, mail_date, garbage_date, channels, current_programs, today = update()
    return json.dumps([weather_data, mail_date, garbage_date, channels, current_programs, today])


if __name__ == '__main__':
    app.run()