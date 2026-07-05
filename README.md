# ReminderBot 🕒

A Telegram bot for creating, editing, and managing reminders.  
Built with Python using the **aiogram 3** library and **SQLite** database.

---
## 🚀 How to Run the Project Locally

### 1. Clone the repository

```bash
git clone https://github.com/your_username/ReminderBot.git
cd ReminderBot

### 2. Set up a virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate  # macOS / Linux
venv\Scripts\activate     # Windows
pip install -r requirements.txt

### 3. Configure your Telegram Bot Token
Create a file named config.py in the root directory of the project (it is added to .gitignore for security reasons).

Copy the structure from config_example.py and insert your actual token received from @BotFather

### 4. Run the bot
python bot.py