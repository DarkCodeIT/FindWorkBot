# 🤖 FindWorkBot — Async Telegram Job Scraper & Bot

> **Project Status:** Archived portfolio project (demonstrating backend development skills, web scraping, and asynchronous Python architecture).

## 📌 About the Project
**FindWorkBot** is an end-to-end automated solution built with Python. The application solves the problem of continuous job monitoring by periodically scraping target websites, cleaning and structuring the data, storing it in a remote cloud database, and delivering real-time updates to users via an interactive Telegram bot interface.

---

## 🛠 Tech Stack
* **Language:** Python 3.10+
* **Telegram API:** `aiogram` (asynchronous framework)
* **Web Scraping:** `BeautifulSoup`, `asyncio`, `requests`
* **Database:** MongoDB (NoSQL) + Motor (async driver)
* **Architecture:** Async/Await, FSM (Finite State Machine), Middlewares, Modular Monolith

---

## 📂 Project Architecture
The project is designed following clean architecture principles and separation of concerns:
```text
FindWorkBot/
│
├── bot/                    # Telegram bot interface[cite: 1]
│   ├── handlers/           # Command, message, callback, and admin handlers[cite: 1]
│   ├── keyboards/          # Inline and Reply keyboards[cite: 1]
│   ├── middlewares/        # Anti-flood protection and custom middlewares[cite: 1]
│   └── utils/              # FSM states and text formatting utilities[cite: 1]
│
├── database/               # Data access layer (MongoDB services, statistics)[cite: 1]
├── parsing/                # Background web scraper and task scheduler (timer)[cite: 1]
├── logs/                   # Modular logging system[cite: 1]
├── const.py                # Text constants and configuration[cite: 1]
├── requirements.txt        # Project dependencies[cite: 1]
└── run.py                  # Application entry point[cite: 1]
