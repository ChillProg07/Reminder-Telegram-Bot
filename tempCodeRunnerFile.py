@dp.message(Command("list"))
async def list_reminders(message:Message):
   reminders = get_reminders()

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