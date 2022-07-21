import datetime
import json
import time

import requests

months = ['januari', 'februari', 'mars', 'april', 'maj', 'juni', 'juli', 'augusti', 'september', 'oktober', 'november', 'december']
weekdays = ['Måndag', 'Tisdag', 'Onsdag', 'Torsdag', 'Fredag', 'Lördag', 'Söndag']

def degrees_to_cardinal(d):
    '''
    note: this is highly approximate...
    '''
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    ix = int((d + 11.25)/22.5)
    return dirs[ix % 16]

def get_current_weather():
    headers = {
        'User-Agent': "acmeweathersite.com support@acmeweathersite.com"
    }
    url = 'https://api.met.no/weatherapi/locationforecast/2.0/complete.json?lat=57.678665&lon=18.569196'
    weather_data = requests.get(url, headers=headers)
    weather_data = json.loads(weather_data.text)
    t = datetime.datetime.now()
    for i, data in enumerate(weather_data['properties']['timeseries']):
        dt = data['time']
        dt = dt.replace('T', ' ')
        dt = dt.replace('Z', '')
        weather_time = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
        if weather_time > t:
            break
    i -= 1
    air_temp = weather_data['properties']['timeseries'][i]['data']['instant']['details']['air_temperature']
    wind_dir = weather_data['properties']['timeseries'][i]['data']['instant']['details']['wind_from_direction']
    wind_speed = weather_data['properties']['timeseries'][i]['data']['instant']['details']['wind_speed']
    next_hour_icon = weather_data['properties']['timeseries'][i]['data']['next_1_hours']['summary']['symbol_code']
    next_6_hour_icon = weather_data['properties']['timeseries'][i]['data']['next_6_hours']['summary']['symbol_code']
    next_6_hour_temp_max = weather_data['properties']['timeseries'][i]['data']['next_6_hours']['details']['air_temperature_max']
    next_6_hour_temp_min = weather_data['properties']['timeseries'][i]['data']['next_6_hours']['details']['air_temperature_min']
    next_12_hour_icon = weather_data['properties']['timeseries'][i]['data']['next_12_hours']['summary']['symbol_code']
    next_12_hour_temp = weather_data['properties']['timeseries'][i+12]['data']['instant']['details']['air_temperature']
    return {
        'air_temp': air_temp,
        'wind_direction': degrees_to_cardinal(wind_dir)+'.png',
        'wind_speed': wind_speed,
        'next_1_hour_icon': f'{next_hour_icon}.png',
        'next_6_hour_icon': f'{next_6_hour_icon}.png',
        'next_6_hour_min_temp': next_6_hour_temp_min,
        'next_6_hour_max_temp': next_6_hour_temp_max,
        'next_12_hour_icon': f'{next_12_hour_icon}.png',
        'next_12_hour_temp': next_12_hour_temp,
    }


def get_next_mail_date():
    data = requests.get('https://portal.postnord.com/api/sendoutarrival/closest?postalCode=62436').json()
    delivery = data['delivery'].split(',')[0]
    delivery_day = delivery.split(' ')[0]
    delivery_month = months.index(delivery.split(' ')[1]) + 1
    now = datetime.datetime.now()
    delivery_date = datetime.datetime.strptime(f'{delivery_day}-{delivery_month}-{now.year} 23:59:59', '%d-%m-%Y %H:%M:%S')
    upcoming = data['upcoming'].split(',')[0]
    return delivery if delivery_date >= datetime.datetime.now() else upcoming


def get_next_garbage_date():
    date = datetime.datetime.now()
    while date.weekday() != 2 or int(date.strftime('%V')) % 2 != 0:
        date += datetime.timedelta(days=1)

    return f'{date.day} {months[date.month-1]}'


def get_swim_temp():
    data = requests.get('https://www.gotlandsenergi.se/badapp/iframe').text
    print()


from collections import defaultdict

def etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
              d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d

def radio_channels():
    from xml.etree import cElementTree
    data = requests.get('https://api.sr.se/api/v2/channels').text
    data = etree_to_dict(cElementTree.XML(data))
    channels = data['sr']['channels']['channel']
    return [{
        'image': channel['image'],
        'name': channel['@name'],
        'id': channel['@id'],
        'stream': channel['liveaudio']['url']
    } for channel in channels]

def now_playing(channel_id):
    url = f'https://api.sr.se/api/v2/scheduledepisodes/rightnow?channelid={channel_id}&format=json'
    return json.loads(requests.get(url).text)

def day_info():
    today = datetime.datetime.now()
    day = today.day if today.day > 9 else f'0{today.day}'
    month = months[today.month-1]
    year = today.year
    weekday = weekdays[datetime.datetime.weekday(datetime.datetime.now())]
    hour = today.hour if today.hour > 9 else f'0{today.hour}'
    minute = today.minute if today.minute > 9 else f'0{today.minute}'
    second = today.second if today.second > 9 else f'0{today.second}'
    data = {
        'date': f'{weekday} {day} {month} {year}'
    }
    return data

if __name__ == '__main__':
    get_next_mail_date()
    channels = radio_channels()
    now_playing = [now_playing(channel['id']) for channel in channels]
    day_info()
    print(get_current_weather())
    print(get_next_mail_date())
    print(get_next_garbage_date())




