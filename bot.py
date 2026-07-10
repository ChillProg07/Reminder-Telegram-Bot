import asyncio

from aiogram import Bot,Dispatcher,F
from aiogram.types import Message,BotCommand, ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from storage import add_reminder, get_reminders, delete_reminders,update_reminder, get_all_reminders,mark_as_sent
from datetime import datetime
from storage import init_db
from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()

class ReminderState(StatesGroup):
   waiting_for_text = State()
   waiting_for_delete = State()
   waiting_for_date = State()
   waiting_for_time = State()

   waiting_for_edit_index = State()
   waiting_for_edit_text = State()
   waiting_for_edit_date = State()
   waiting_for_edit_time = State()
   waiting_for_edit_choice = State()

 #buttons for users
menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text = "Додати нагадування"), KeyboardButton(text="Показати все")],
        [KeyboardButton(text="Видалити"), KeyboardButton(text="Редагувати")]
    ],
    resize_keyboard=True
)


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("👋 Привіт!\n\n"
        "Я бот-нагадувач ⏰\n"
        "Я допоможу тобі зберігати події "
        "і нагадувати про них.\n\n"
        "Обери дію:",
        reply_markup=menu)
    
    
# команда help
@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "🤖 Допомога:\n\n"
        "/add — створити нагадування\n"
        "/list — всі твої події\n"
        "/delete — видалити подію\n"
        "/edit - редагувати нагадування"
    )  

#add command
@dp.message(Command("add"))
@dp.message(F.text=="Додати нагадування")
async def add_command(message:Message, state:FSMContext):
   await message.answer("📝 Напиши, що потрібно нагадати:")
   await state.set_state(ReminderState.waiting_for_text)

@dp.message(ReminderState.waiting_for_text)
async def save_Reminder(message:Message, state:FSMContext):
   reminder = message.text
   await state.update_data(text=reminder)
   await message.answer(
        "📅 Тепер введіть дату\n\n"
        "Наприклад: 15.07.2026"
    )
   await state.set_state(ReminderState.waiting_for_date)

@dp.message(ReminderState.waiting_for_date)
async def save_date(message:Message, state:FSMContext):
   date_text = message.text.strip()
   formats = [
        "%d.%m.%Y",
        "%d.%m"
    ]
   parsed_date = None
   for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_text, fmt)
            break
        except ValueError:
            pass

   if parsed_date is None:
        await message.answer(
            "❌ Неправильний формат дати.\n\n"
            "Приклади:\n"
            "02.07\n"
            "02.07.2026"
        )
        return
   # по дефолту ставимо 2026р.
   if parsed_date.year == 1900:
      parsed_date = parsed_date.replace(year=datetime.now().year)
   formatted_date = parsed_date.strftime("%d.%m.%Y")

   await state.update_data(date=formatted_date)
   await message.answer(
        "⏰ Тепер введіть час\n\n"
        "Наприклад: 14:30"
)
   await state.set_state(ReminderState.waiting_for_time)



@dp.message(ReminderState.waiting_for_time)
async def save_time(message:Message, state:FSMContext):
   time = message.text
   try:
    datetime.strptime(time, "%H:%M")
   except ValueError:
      await message.answer(
        "❌ Неправильний час.\n"
        "Введіть так:\n"
        "14:30"
    )
      return

   await state.update_data(time=time)
   data = await state.get_data()

   reminder = {
    "chat_id": message.chat.id,
    "text": data["text"],
    "date": data["date"],
    "time": data["time"]
}
   add_reminder(reminder)

   await message.answer(
    "✅ Нагадування створено!"
)

   await state.clear()


#list command 
@dp.message(Command("list"))
@dp.message(F.text=="Показати все")
async def list_reminders(message:Message):
   reminders = get_reminders(message.chat.id)

   if not reminders:
      await message.answer("У вас поки немає нагадувань")
      return
   text = "📋 Твої нагадування:\n\n"

   for i, reminder in enumerate(reminders,start=1):
    text += (
        f"{i}.\n"
        f"📌 {reminder['text']}\n"
        f"📅 {reminder['date']}\n"
        f"⏰ {reminder['time']}\n\n"
    )
   await message.answer(text)
   
#delete command
@dp.message(Command("delete"))
@dp.message(F.text=="Видалити")
async def delete_command(message:Message, state:FSMContext):
   reminders = get_reminders(message.chat.id)

   if not reminders:
        await message.answer(
            "📭 Немає нагадувань для видалення"
        )
        return
   text = "🗑️ Введи номер нагадування:\n\n"
   for i, reminder in enumerate(reminders, start=1):
      text += (
        f"{i}. {reminder['text']}\n"
        f"   📅 {reminder['date']}\n"
        f"   ⏰ {reminder['time']}\n\n")
   await message.answer(text)
   await state.set_state(ReminderState.waiting_for_delete)

@dp.message(ReminderState.waiting_for_delete)
async def delete_selected(message:Message, state:FSMContext):
    try:
        number = int(message.text) - 1
        reminders = get_reminders(message.chat.id)

        if number < 0 or number >= len(reminders):
            raise ValueError

        reminder_id = reminders[number]["id"]

        delete_reminders(reminder_id)

        await message.answer("✅ Нагадування видалено!")
        await state.clear()

    except ValueError:
        await message.answer("❌ Введіть правильний номер.")


# edit text
@dp.message(Command("edit"))
@dp.message(F.text=="Редагувати")
async def edit_command(message:Message, state:FSMContext):
   reminders = get_reminders(message.chat.id)
   if not reminders:
      await message.answer("📭 Немає нагадувань для редагування")
      return

   text = "✏️ Обери номер нагадування для редагування:\n\n"

   for i, reminder in enumerate(reminders, start=1):
        text += (
            f"{i}. 📌 {reminder['text']}\n"
            f"   📅 {reminder['date']}\n"
            f"   ⏰ {reminder['time']}\n\n"
        )
   await message.answer(text)
   await state.set_state(ReminderState.waiting_for_edit_index)

#choose a number of edit
@dp.message(ReminderState.waiting_for_edit_index)
async def edit_choose_index(message: Message, state: FSMContext):
    reminders = get_reminders(message.chat.id)
    try:
        chosen_index = int(message.text) - 1
    except ValueError:
        await message.answer("❌ Будь ласка, введіть число (наприклад: 1, 2...)")
        return

    if chosen_index < 0 or chosen_index >= len(reminders):
        await message.answer("❌ Нагадування з таким номером не існує. Спробуйте ще раз.")
        return
    
    reminder = reminders[chosen_index]
    await state.update_data(reminder_id=reminders["id"])

    keyboard = InlineKeyboardMarkup(
       inline_keyboard=[
            [ InlineKeyboardButton(
                    text="📝 Текст",
                    callback_data="edit_text"
                ),
                InlineKeyboardButton(
                    text="📅 Дата",
                    callback_data="edit_date"
                )
            ],
            [ InlineKeyboardButton(
                    text="⏰ Час",
                    callback_data="edit_time"
                ),
                InlineKeyboardButton(
                    text="✏️ Усе",
                    callback_data="edit_all"
                )
            ],
            [ InlineKeyboardButton(
                    text="❌ Скасувати",
                    callback_data="edit_cancel"
                )
            ]
        ]
    )

    await message.answer(
        f"📌 Обране нагадування:\n\n"
        f"{reminder['text']}\n"
        f"📅 {reminder['date']}\n"
        f"⏰ {reminder['time']}\n\n"
        f"Що потрібно змінити?",
        reply_markup=keyboard
    )

    await state.set_state(ReminderState.waiting_for_edit_choice)


@dp.callback_query(ReminderState.waiting_for_edit_choice, F.data=="edit_text")
async def process_edit_text(
    callback: CallbackQuery,
    state: FSMContext
):

    await callback.message.edit_text(
        "📝 Введіть новий текст для нагадування:"
    )

    await state.set_state(
        ReminderState.waiting_for_edit_text
    )

    await callback.answer()

@dp.callback_query(
    ReminderState.waiting_for_edit_choice,
    F.data == "edit_date"
)
async def process_edit_date(
    callback: CallbackQuery,
    state: FSMContext
):

    await callback.message.edit_text(
        "📅 Введіть нову дату:"
    )

    await state.set_state(
        ReminderState.waiting_for_edit_date
    )

    await callback.answer()

@dp.callback_query(
    ReminderState.waiting_for_edit_choice,
    F.data == "edit_time"
)
async def process_edit_time(
    callback: CallbackQuery,
    state: FSMContext
):

    await callback.message.edit_text(
        "⏰ Введіть новий час:"
    )

    await state.set_state(
        ReminderState.waiting_for_edit_time
    )

    await callback.answer()


@dp.callback_query(
    ReminderState.waiting_for_edit_choice,
    F.data == "edit_all"
)
async def process_edit_all(
    callback: CallbackQuery,
    state: FSMContext
):

    await state.update_data(
        edit_all=True
    )

    await callback.message.edit_text(
        "📝 Введіть новий текст:"
    )

    await state.set_state(
        ReminderState.waiting_for_edit_text
    )

    await callback.answer()

@dp.callback_query(
    ReminderState.waiting_for_edit_choice,
    F.data == "edit_cancel"
)
async def process_edit_cancel(
    callback: CallbackQuery,
    state: FSMContext
):

    await callback.message.edit_text(
        "❌ Редагування скасовано."
    )

    await state.clear()

    await callback.answer()

    
# edit only text
@dp.message(ReminderState.waiting_for_edit_text)
async def edit_save_text(message:Message, state:FSMContext):
   newText = message.text
   data = await state.get_data()
   reminder_id = data.get("reminder_id")

   if reminder_id is None:
      await message.answer("❌ Щось пішло не так. Спробуйте заново через /edit")
      await state.clear()
      return
   
   update_reminder(reminder_id, newText)
   await message.answer("✅ Нагадування оновлено!")
   await state.clear()
   

#налаштування меню бота
async def set_commands():
    commands = [BotCommand(
            command="start",
            description="Запустити бота"),
            BotCommand(
            command="add",
            description="Додати нагадування"
        ),BotCommand(
            command="list",
            description="Мої нагадування"
        ),BotCommand(
            command="delete",
            description="Видалити нагадування"
        ),BotCommand(
            command="help",
            description="Допомога"
        ),BotCommand(
            command="edit",
            description="Редагувати нагадування"),
    ]

    await bot.set_my_commands(commands)

async def check_reminders():
   while True:
        now = datetime.now()
        reminders = get_all_reminders()
        to_delete = []

        for reminder in reminders:
            reminder_dt = datetime.strptime(
                f"{reminder['date']} {reminder['time']}",
                "%d.%m.%Y %H:%M"
            )

            if reminder["is_sent"] == 0 and now >= reminder_dt:
                await bot.send_message(
                    chat_id=reminder["chat_id"],
                    text=f"⏰ Нагадування!\n\n📌 {reminder['text']}"
                )
                mark_as_sent(reminder["id"])
        await asyncio.sleep(5)


async def main():
 init_db()
 await set_commands()
 asyncio.create_task(check_reminders())
 await dp.start_polling(bot)

asyncio.run(main())