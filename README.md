
# Quickstart

## Установка

Чтобы запустить бота, вам необходимо установить необходимые библиотеки. Убедитесь, что у вас установлен Python версии 3.7 или выше.

1. **Клонируйте репозиторий**:

   ```
   git clone https://github.com/elhuel/weatherBot.git
   cd your-repo
   ```

2. **Создайте виртуальное окружение (рекомендуется)**:

   ```
   python -m venv .venv
   source venv/bin/activate  # Для Linux/Mac
   venv\Scripts\activate  # Для Windows
   ```

3. **Установите необходимые библиотеки**:




   ```
   pip install aiogram plotly requests asyncio
   ```

4. **Настройте переменные окружения**:

   Создайте файл `config.py` в корневом каталоге вашего проекта и добавьте следующие строки, заменив `YOUR_BOT_TOKEN` и `YOUR_ACCUWEATHER_API_KEY` на ваши реальные ключи:

   ```
   BOT_TOKEN = 'YOUR_BOT_TOKEN'
   ACCUWEATHER_API_KEY = 'YOUR_ACCUWEATHER_API_KEY'
   ```

5. **Запустите бота**:

   После установки всех зависимостей и настройки переменных окружения, запустите бота с помощью следующей команды:

   ```
   python app.py  # Замените на имя вашего файла с ботом
   ```

Теперь ваш бот должен быть запущен и готов к использованию!

## Использование

1. Запустите бота.
2. Введите команду `/start`, чтобы начать взаимодействие с ботом.
3. Используйте команду `/weather`, чтобы получить прогноз погоды.
4. Введите маршрут в формате: `Город1 - Город2 - Город3`.
5. Выберите количество дней для прогноза (1 или 5).
6. Получите прогноз погоды в текстовом виде или в виде графиков.

