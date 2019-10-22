# -*- coding: utf-8 -*-

# Import relevant libraries
%matplotlib inline
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

import requests as http # HTTP request library
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets # useful for user interaction

### START: Scripts

# Global constants
OWM_BASE_URL     = 'http://api.openweathermap.org/data/2.5'
OWM_WEATHER_URL  = OWM_BASE_URL + '/weather'
OWM_FORECAST_URL = OWM_BASE_URL + '/forecast'
OWM_API_KEY      = '008da7addc4cd8fc63053350fd71d595'

OWM_UNITS        = {'C': 'metric', 'F': 'imperial', 'K': ''}
OWM_COLORS       = {'grey': '#AAAAAA'}
OWM_ERR_MSG      = ''

DEFAULT_CITY_NAME    = 'BREMEN'
DEFAULT_COUNTRY_CODE = 'DE' # ISO-2 country code


""" 
get_data_from_API - Perform API requests. 
This function basically sends HTTP requests (GET mainly) to Open Weather Map and expects
a JSON-oriented weather data.
Args:
    url: the url of the Open Weather Map's endpoint to perform API calls
    city_name: name of the city (including the ISO-alpha2 code) of interests

Returns:
    the JSON data obtain from the HTTP response if successful (city found)

Exception:
    return an HTTP response (JSON) of NOT_FOUND (404)
"""
def get_data_from_API(url = OWM_WEATHER_URL, city_name = DEFAULT_CITY_NAME):
    params = { 'q': city_name, 'APPID': OWM_API_KEY, 'units': OWM_UNITS['C'] }
    return http.get(url, params = params)

""" 
validate_data_from_API - Validate HTTP response once request is performed. 
This function intends to standardize the response object so that some validation
rule can be used in the future. NOT IMPLEMENTED for the moment.
Args:
    response: plain HTTP response in JSON-like format

Returns:
    a new transformed dictionary with 'data' key, if successful or 'error', otherwise.
"""
def validate_data_from_API(response):
    # API response
    if(response.status_code == 200):
        return { 'data': response.json() }
    return { 'error': response.json() }

""" 
get_current_weather - Get today's weather from loaded data 

Args:
    data: JSON data (response) from Open Weather Map

Returns:
    a tuple of 'times' and 'temps' (temeratures) of today's date. 
    additionally, 'filtered', the filtered 'main' object data for future use.
    finally, 'metadada', the story behind the filtered data.
"""
def get_current_weather(data):
    metadata = {
        'plot_title': 'Current weather in ' + data['city']['name'] + ', ' + data['city']['country']
    }
    today = datetime.today().strftime('%Y-%m-%d')
    times, temps, filtered = [], [], []
    
    # select today's date only
    for el in data['list']:
        day, time = el['dt_txt'].split(' ') 
        if(day == today):
            times.append(time[:-3]) # get rid of seconds
            temps.append(el['main']['temp'])
            filtered.append(el['main'])
            
    return (times, temps, filtered, metadata)

def calculate_all_mean(objects):
    # mean accumulator
    acc = {
        "temp": 0,
        "temp_min": 0,
        "temp_max": 0,
        "pressure": 0,
        "sea_level": 0,
        "grnd_level": 0,
        "humidity": 0,
        "temp_kf": 0
    }
    
    """
        The idea is to look up the sibling elements distributed in each 'main' object
        of the array of objects and calculate the mean of all together. The data looks 
        like this:
        [
          { 'main': {'temp': 1, 'temp_min': 2, ...} },
          { 'main': {'temp': 1, 'temp_min': 2, ...} }, ...
        ]
        Algorithm:
            1) sum them all accordingly (distributed)
            2) calculate the mean (Average / length)
    """
    for o in objects:
        for k, v in o['main'].items():
            acc[k] += v
    for k, v in acc.items():
        acc[k] = acc[k] / len(objects)
    return acc


""" 
get_daily_weather - Get daily weather from loaded data 
Recall that for the Free subscription plan, the daily basis is 5 days 3-hour wise.
This function groups temperatures by day and calculate the mean temperature for
that day.

Args:
    data: JSON data (response) from Open Weather Map

Returns:
    a tuple of 'times' and 'temps' (temeratures) on a daily basis. 
    additionally, 'filtered', the filtered 'main' object data for future use.
    finally, 'metadada', the story behind the filtered data.
"""
def get_daily_weather(data):
    metadata = {
        'plot_title': 'Daily weather in ' + data['city']['name'] + ', ' + data['city']['country']
    }
    days = {}
    times, temps, filtered = [], [], []
    
    # group by same date: yyyy-MM-dd
    for el in data['list']:
        day, time = el['dt_txt'].split(' ')
        if day in days:
            days[day].append(el)
        else:
            days[day] = [el]
    
    # accumulate mean temperature on a daily basis
    for key, value in days.items():
        parsed_date = datetime.strptime(key, '%Y-%m-%d')
        formated_date = parsed_date.strftime('%d %b %y')
        mean_values = calculate_all_mean(value)
            
        times.append(formated_date)
        temps.append(mean_values['temp'])
        filtered.append(mean_values)
            
    return (times, temps, filtered, metadata)


# helper function to plot graphs
def plot_graph(data):
    times, temps, filtered, metadata = data
    humidities = [f['humidity'] for f in filtered]
    
    fig = plt.figure(figsize=(11, 6.5))
    # Set temperature y-axis on the left
    left_axis = fig.add_subplot(111)
    temp_line = left_axis.plot(times, temps, '-b')
    left_axis.plot(times, temps, 'ro')
    left_axis.set_ylabel('Temperature ($^{\circ}{C}$)', color='blue', fontsize=12)
    left_axis.tick_params(axis='y', colors='blue')
    # left_axis.set_xlabel('Time', fontsize=12)
    
    # Set humidity y-axis on the right
    right_axis = left_axis.twinx()
    hum_line = right_axis.plot(times, humidities, color=OWM_COLORS['grey'])
    right_axis.plot(times, humidities, 'yo')
    right_axis.set_ylabel('Humidity (%)', fontsize=12)
    right_axis.tick_params(axis='y', colors=OWM_COLORS['grey'])
    
    # Set additional/common properties for the figure
    plt.legend(temp_line + hum_line, ['Temperature', 'Humidity'], loc='best')
    plt.title(metadata['plot_title'], fontsize=14)
    plt.grid()
    plt.show()
    

# main function to run the entire process: fetch, prepare, and visualize data
def main(city):
    
    print('You have selected the city of', city)
    data = {}
    
    # Access data online via API
    api_response = get_data_from_API( OWM_FORECAST_URL, city)
    content = validate_data_from_API( api_response )
    
    if('data' in content):
        OWM_ERR_MSG = ''
        data = content['data']
    else:
        OWM_ERR_MSG  = 'The weather for ' + city + ' could not be found. '
        OWM_ERR_MSG += 'Check for your internet connection and try again later.'
        print(OWM_ERR_MSG)
        # TODO: handle type of error info to display
        return
    
    current_weather = get_current_weather( data )
    plot_graph( current_weather )
    daily_weather = get_daily_weather( data )
    plot_graph( daily_weather )
    
# helper function to load static cities
def load_static_cities():
    return [
        ('Bremen, Germany', 'BREMEN,DE'), ('Mexico, Mexico', 'MEXICO,MX'),
        ('Milan, Italy', 'MILAN,IT'), ('New York, United States', 'NEW YORK,US'), 
        ('London, United Kingdom', 'LONDON,UK'), ('Ottawa, Canada', 'OTTAWA,CA'),
        ('Paris, France', 'PARIS,FR'), ('Port-au-Prince, Haiti', 'PORT-AU-PRINCE,HT'),
        ('Santiago, Chile', 'SANTIAGO,CL'), ('Tokyo, Japan', 'TOKYO,JP')
    ]

# main application
def application():
    file = open('../assets/data/welcome-msg@project.txt', 'r') 
    print(file.read())
    file.close()
    cities = load_static_cities()
    interact(main, city=cities)

# run application 
application()
### END: Scripts