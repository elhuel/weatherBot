from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import Command, StateFilter
from weather import *  # Импортируем функции для получения прогноза погоды
import plotly.graph_objs as go  # Импортируем библиотеку для построения графиков
import plotly.io as pio  # Импортируем модуль для сохранения графиков
from config import BOT_TOKEN, ACCUWEATHER_API_KEY  # Импортируем токены из конфигурации
import asyncio  # Импортируем модуль для асинхронного программирования
import os  # Импортируем модуль для работы с файловой системой

# Инициализируем бота и диспетчер
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
API_KEY = ACCUWEATHER_API_KEY

# Определяем состояния для работы с FSM (Finite State Machine)
class Weather(StatesGroup):
    locations = State() 
    days = State()       

# Обработчик команды /start
@dp.message(Command('start'))
async def start(message: types.Message):
    await message.reply("Привет! Я бот для прогноза погоды по заданным точкам.\n"
                        "Введи команду /weather, чтобы узнать погоду для введенных локаций.")

# Обработчик команды /help
@dp.message(Command('help'))
async def help(message: types.Message):
    await message.reply("Доступные команды:\n"
                        "/start - Знакомство с ботом\n"
                        "/help - Доступные команды\n"
                        "/weather - Получить данные о погоде.")

# Обработчик команды /weather
@dp.message(Command('weather'))
async def weather(message: types.Message, state: FSMContext):
    await message.reply("Введите маршрут, чтобы получить прогноз погоды \n\nПример:"
                         " Москва - Санкт-Петербург - Владивосток. (между названиями городов 'пробел+тире+пробел')")
    await state.set_state(Weather.locations)  # Устанавливаем состояние ввода локаций

# Обработчик ввода локаций
@dp.message(StateFilter(Weather.locations))
async def get_locations(message: types.Message, state: FSMContext):
    locations = message.text.lower().split(" - ")  # Разделяем введенные города по тире
    locations = [location.capitalize() for location in locations]
    await state.update_data(locations=locations)  # Сохраняем локации в состоянии

    # Создаем кнопки для выбора количества дней прогноза
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="1 день", callback_data="1")],
            [InlineKeyboardButton(text="5 дней", callback_data="5")]
        ]
    )
    
    await message.reply("Выберите количество дней, на которые вы хотите получить прогноз погоды:", reply_markup=keyboard)
    await state.set_state(Weather.days)  # Устанавливаем состояние выбора дней

# Обработчик выбора количества дней прогноза
@dp.callback_query(lambda c: c.data in ["1", "5"], StateFilter(Weather.days))
async def get_days(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(days=int(call.data))  # Сохраняем выбранное количество дней в состоянии
    data = await state.get_data()  # Получаем сохраненные данные из состояния
    locations = data.get("locations")  # Извлекаем локации
    days = int(data.get("days"))  # Извлекаем количество дней

    try:
        forecasts = {}
        for location in locations:
            forecast = get_conditions(API_KEY, location, days)  # Получаем прогноз погоды для каждой локации
            forecasts[location] = forecast
        
        response = "Прогноз погоды для выбранных точек:\n"
        for location, forecast_list in forecasts.items():
            response += location + ":\n" 
            
            for forecast in forecast_list:
                day = forecast['date'][:10]  # Извлекаем дату прогноза
                # Создаем форматированный ответ
                response += day + ":\n"
                response += f"Температура: {forecast['temperature']} °C\n" 
                response += f"Ветер: {forecast['wind']} м/с\n"  
                response += f"Влажность: {forecast['precipitation_probability']} %\n" 
                response += "\n"

            if days == 1:
                continue  # Если выбрано 1 день, пропускаем создание графиков
            
            # Создаем графики   
            fig_temp = go.Figure()
            fig_precip = go.Figure()
            fig_wind = go.Figure()

            # Для графиков собираем данные из forecast_list
            days_list = [forecast['date'][:10] for forecast in forecast_list]
            temp_max_list = [forecast['temperature'] for forecast in forecast_list]
            wind_speed_list = [forecast['wind'] for forecast in forecast_list]
            precip_prob_list = [forecast['precipitation_probability'] for forecast in forecast_list]

            # График температуры
            fig_temp.add_trace(go.Scatter(
                x=days_list,
                y=temp_max_list,
                mode='lines+markers',
                name='Температура'
            ))
            fig_temp.update_layout(
                title=f"{location} - Температура",
                xaxis_title="Дни",
                yaxis_title="Температура (°C)",
                legend=dict(x=0.1, y=1.1),
                template="plotly_white"
            )

            # График вероятности осадков
            fig_precip.add_trace(go.Bar(
                x=days_list,
                y=precip_prob_list,
                name='Вероятность осадков',
                marker_color='blue'
            ))
            fig_precip.update_layout(
                title=f"{location} - Вероятность осадков",
                xaxis_title="Дни",
                yaxis_title="Вероятность осадков (%)",
                template="plotly_white"
            )

            # График скорости ветра
            fig_wind.add_trace(go.Scatter(
                x=days_list,
                y=wind_speed_list,
                mode='lines+markers',
                name='Скорость ветра',
                line=dict(color='green')
            ))
            fig_wind.update_layout(
                title=f"{location} - Скорость ветра",
                xaxis_title="Дни",
                yaxis_title="Скорость ветра (м/с)",
                template="plotly_white"
            )

            # Сохраняем изображения графиков на диск
            temp_path = f"{location}_temperature.png"
            precip_path = f"{location}_precipitation.png"
            wind_path = f"{location}_wind.png"
            
            pio.write_image(fig_temp, temp_path)
            pio.write_image(fig_precip, precip_path)
            pio.write_image(fig_wind, wind_path)

            # Отправляем графики пользователю через Telegram
            await bot.send_photo(call.message.chat.id, FSInputFile(temp_path),
                                  caption=f"График температуры для города {location.capitalize()}")
            await bot.send_photo(call.message.chat.id, FSInputFile(precip_path),
                                  caption=f"График вероятности осадков для города {location.capitalize()}")
            await bot.send_photo(call.message.chat.id, FSInputFile(wind_path),
                                  caption=f"График скорости ветра для города {location.capitalize()}")

            # Удаляем временные файлы
            os.remove(temp_path) 
            os.remove(precip_path)  
            os.remove(wind_path)     

    except Exception as e:
        await call.message.answer(f"Произошла ошибка: {e}")  # Обработка ошибок и отправка сообщения пользователю
    
    await call.message.answer(response)
      # Отправляем текстовый ответ с прогнозом пользователю
    await state.clear()
    await help(call.message)  # Вызываем функцию помощи после завершения обработки

# Основная функция запуска бота
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)  # Запускаем опрос обновлений от Telegram

if __name__ == "__main__":
    asyncio.run(main())  # Запускаем основную функцию при выполнении скрипта 
