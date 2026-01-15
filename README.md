# Kolokol Pottery Workshop Telegram Bot

Это Telegram-бот для гончарной мастерской "Колокол" в Самаре. Бот помогает управлять сообществом мастерской, отслеживать баллы пользователей, отправлять напоминания, вести статистику мероприятий и маркетинговых кампаний.

## Функциональность

### Для пользователей:
- **Регистрация**: Регистрация через номер телефона
- **Личный кабинет**: Просмотр баланса, истории транзакций
- **UTM-трекинг**: Отслеживание переходов по реферальным ссылкам
- **Напоминания**: Получение персональных напоминаний
- **Информация о мастерской**: Контакты, расписание, описание услуг

### Для администраторов:
- **Рассылка сообщений**: Текстовые и медиа-рассылки всем пользователям или по мероприятиям
- **Сканирование QR-кодов**: Проверка баланса пользователей по QR-коду
- **Управление UTM-кампаниями**: Создание и статистика реферальных ссылок
- **Экспорт данных**: Выгрузка списка пользователей в Excel
- **Управление напоминаниями**: Создание напоминаний для пользователей
- **Статистика мероприятий**: Отслеживание посещаемости

## Технологии

- **Python 3.11+**
- **Aiogram 3** - фреймворк для Telegram ботов
- **PostgreSQL** - база данных
- **SQLAlchemy** - ORM для работы с БД
- **APScheduler** - планировщик задач (для напоминаний)
- **Docker** - контейнеризация
- **Pydantic** - валидация конфигурации

## Установка и запуск

### Локальный запуск

1. **Клонируйте репозиторий:**
   ```bash
   git clone <repository-url>
   cd kolocol
   ```

2. **Создайте виртуальное окружение:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Для Windows: venv\Scripts\activate
   ```

3. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Настройте переменные окружения:**
   Создайте файл `.env` в корне проекта:
   ```env
   BOT_TOKEN=your_telegram_bot_token
   POSTGRES_USER=your_db_user
   POSTGRES_PASSWORD=your_db_password
   POSTGRES_DB=kolokol_bot
   POSTGRES_PORT=5432
   POSTGRES_HOST=localhost
   ADMIN_IDS=123456789,987654321
   ```

5. **Запустите PostgreSQL:**
   Убедитесь, что PostgreSQL запущен и доступен.

6. **Создайте таблицы БД:**
   ```bash
   python database/create_tables.py
   ```

7. **Запустите бота:**
   ```bash
   python main.py
   ```

### Запуск через Docker

1. **Соберите образ:**
   ```bash
   docker compose up --build
   ```

2. **Запустите контейнеры:**
   ```bash
   docker-compose up -d
   ```

## Структура проекта

```
kolocol/
├── main.py                 # Точка входа в приложение
├── config.py              # Конфигурация (Pydantic settings)
├── requirements.txt       # Зависимости Python
├── Dockerfile            # Docker образ
├── docker-compose.yaml   # Docker Compose конфигурация
├── database/
│   ├── __init__.py
│   ├── db.py            # Класс для работы с БД
│   ├── models.py        # SQLAlchemy модели
│   └── create_tables.py # Скрипт создания таблиц
├── handlers/
│   ├── user_handlers/    # Обработчики для пользователей
│   │   ├── start.py     # Регистрация и старт
│   │   ├── cabinet.py   # Личный кабинет
│   │   └── transaction_history.py # История транзакций
│   └── admin_handlers/   # Обработчики для админов
│       ├── admin_mailng.py    # Рассылки
│       ├── admin_utm.py       # UTM кампании
│       ├── scan.py            # Сканирование QR
│       ├── people_hendlers.py # Экспорт пользователей
│       └── admin_remind.py    # Напоминания
├── keyboards/
│   ├── IKB.py           # Inline клавиатуры
│   └── RKB.py           # Reply клавиатуры
├── states/
│   └── states.py        # FSM состояния
└── .env                 # Переменные окружения (не в репозитории)
```

## База данных

Бот использует PostgreSQL с следующими таблицами:

- **users**: Пользователи (tg_id, username, balance, phone, utm)
- **transactions**: Транзакции (tg_id, add_or_not, transaction)
- **events**: Мероприятия (tg_id, event_name, created_at)
- **utms**: UTM кампании (name, statistics)
- **remindes**: Напоминания (tg_id, text_remind, date_remind)

## Конфигурация

Все настройки хранятся в файле `.env`:

- `BOT_TOKEN`: Токен Telegram бота
- `POSTGRES_*`: Настройки подключения к PostgreSQL
- `ADMIN_IDS`: ID администраторов через запятую

## Использование

### Для пользователей:
1. Запустите бота командой `/start`
2. Поделитесь номером телефона для регистрации
3. Используйте меню для доступа к функциям

### Для администраторов:
1. Отправьте `/admin` для доступа к админ-панели
2. Выберите нужную функцию из меню

## Разработка

Проект использует современные практики Python-разработки:
- Type hints
- Асинхронное программирование
- Dependency injection через middleware
- FSM для сложных сценариев

## Контакты

Гончарная мастерская "Колокол"
- Адрес: г. Самара, Проспект Масленникова, 15
- Телефон: +7 (919) 816-69-00
- VK: https://vk.ru/kolokolschool_smr
- Telegram: https://t.me/kolokolschool_smr
