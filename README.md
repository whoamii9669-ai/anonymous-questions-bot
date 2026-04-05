# 💬 Anonymous Questions Bot

> Телеграм-бот для анонимных сообщений. Пользователь получает личную ссылку — по ней любой желающий может отправить анонимное сообщение: текст, фото, видео, голосовое, кружок или стикер.

---

## ✨ Возможности

- 🔗 Уникальная ссылка для каждого пользователя
- 🕵️ Полная анонимность отправителя
- ↩️ Анонимные ответы на сообщения
- 📎 Поддержка медиа: фото, видео, голосовые, кружки, стикеры
- ⚡ Быстрая работа на aiogram 3

---

## 🚀 Установка

```bash
git clone https://github.com/whoamii9669-ai/anonymous-questions-bot
cd anonymous-questions-bot
```

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

```bash
pip install -r requirements.txt
```

---

## ⚙️ Конфиг

Создай `.env`:

```env
token=
username=
```

> 💾 База данных `db.db` создаётся автоматически при первом запуске.

---

## ▶️ Запуск

```bash
python main.py
```

