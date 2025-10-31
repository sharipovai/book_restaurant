# 🎤 Book Restaurant Bot — Telegram-бот для бронирования столиков в караоке-клубе *«Бла Бла»*

> Удобный бот для бронирования столиков прямо в Telegram.  
> Все бронирования автоматически синхронизируются с Google Таблицей — включая те, что добавлены вручную.

---

## ✨ Возможности

- 🪑 **Бронирование столика** — выбери дату, время и количество гостей  
- 📋 **Проверка бронирования** — бот покажет твоё текущее бронирование  
- ❌ **Отмена бронирования** — можешь отменить бронь в пару кликов  
- ☁️ **Интеграция с Google Sheets** — бот учитывает все записи, даже внесённые вручную  

---

## 🧩 Структура проекта

- **main.py** - обработка сообщений и логика маршрутизации
- **database.py** - работа с базой данных для хранения ифнормации
- **google_api.py** - взаимодействие с гугл таблицей
- **config_example.py** - параметры и ключи

---

## ⚙️ Установка

```bash
git clone https://github.com/sharipovai/book_restaurant.git
cd book_restaurant
mv config_example.py config.py
pip install -r requirements.txt
```
---

## 💻 Пример работы

### 🧠 Интерфейс бота  
<p align="center">
  <img src="https://github.com/user-attachments/assets/0a347e78-7b1c-4a6b-8836-5d0d5a8d748c" alt="Интерфейс бота" width="80%" />
</p>

---

### 📊 Интеграция с Google Таблицами  
<p align="center">
  <img src="https://github.com/user-attachments/assets/253867a0-ae44-4c82-8226-f249040dc410" alt="Google Таблица" width="65%" />
</p>
