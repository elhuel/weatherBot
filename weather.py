import requests
import json

    
def get_location_id(API_KEY, city):
    location_url = f'http://dataservice.accuweather.com/locations/v1/cities/search?apikey={API_KEY}&q={city}&language=ru'
    try:
        location_response = requests.get(location_url)
        location_response.raise_for_status()
        location_data = location_response.json()
        if location_data:
            return location_data[0]['Key']
    except requests.exceptions.RequestException as e:
        print(f"Ошибка получения данных для города '{city}': {e}")
        return None


def get_conditions(api_key, city, days):
    try:
        location_key = get_location_id(api_key, city)
        if isinstance(location_key, str) and location_key.startswith("Request error"):
            return location_key
        
        url_forecast = f"https://dataservice.accuweather.com/forecasts/v1/daily/{days}day/{location_key}?apikey={api_key}&metric=true&details=true"
        response_forecast = requests.get(url_forecast)
        response_forecast.raise_for_status()

        data_forecast = response_forecast.json()

        if not data_forecast.get("DailyForecasts"):
            raise ValueError("Invalid data received from API.")

        forecasts = []
        for day in data_forecast["DailyForecasts"]:
            forecast = {
                "date": day["Date"],
                "temperature": day["Temperature"]["Maximum"]["Value"],
                "wind": day["Day"]["Wind"]["Speed"]["Value"],
                "precipitation_probability": day['Day']['PrecipitationProbability']
            }
            forecasts.append(forecast)

        return forecasts
    except requests.exceptions.RequestException as e:
        return f"Request error: {e}"
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def check_bad_weather(conditions):
    try:
        bad_weather_score = 0

        if conditions["rain_probability_day"] > 70 or conditions["rain_probability_night"] > 70:
            bad_weather_score += 1 

        if conditions['temperature'] < 0 or conditions['temperature'] > 35:
            bad_weather_score += 1
        
        if conditions['wind'] > 15:
            bad_weather_score += 1
        
        if bad_weather_score >= 2:
            return "Неблагоприятные погодные условия"
        if bad_weather_score == 1:
            return "Слегка неблагоприятные погодные условия"
        if bad_weather_score == 0:
            return "Благоприятные погодные условия"
    except Exception as e:
        return f"An unexpected error occurred: {e}\nOutput: {conditions}"