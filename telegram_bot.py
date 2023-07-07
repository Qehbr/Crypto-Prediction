import asyncio
import sqlite3
import threading

from telegram import Update
import schedule
import update
import training
from telegram.ext import Application, CommandHandler, CallbackContext, ContextTypes

# Start the bot
TOKEN = "YOUR_TOKEN"
application = Application.builder().token(TOKEN).build()


def update_data():
    update.update_all_data(['BTCUSDT'])


async def send_data():
    coins = ['BTCUSDT']
    predicitons = training.train_data(coins)

    to_send = ''
    for c in coins:
        data = predicitons[c]
        to_send += f'<b>{c}</b>\n'
        to_send += f'Prediction: {data["prediction"]}\n'
        to_send += f'Average MSE: {data["mse"]}\n'
        to_send += f'Average rMSE: {data["rmse"]}\n'
        to_send += f'Average r2: {data["r2"]}\n'
        to_send += f'\n'

    # Retrieve the list of subscribed user chat IDs from your storage/database
    conn = sqlite3.connect('crypto.db')
    c = conn.cursor()

    # Retrieve the list of subscribed user chat IDs from the table
    c.execute("SELECT id FROM Users")
    subscribed_users = [row[0] for row in c.fetchall()]
    conn.close()

    # Send the message to each subscribed user
    for user_id in subscribed_users:
        await application.bot.send_message(chat_id=user_id, text=to_send, parse_mode='HTML')


async def update_and_send():
    update_data()
    await send_data()


def schedule_update_and_send():
    asyncio.create_task(update_and_send())


schedule.every().day.at("3:00").do(schedule_update_and_send)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    conn = sqlite3.connect('crypto.db')
    conn.cursor().execute("INSERT OR IGNORE INTO Users (id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()
    await application.bot.send_message(user_id, "You've been successfully added\nYou will get updates every day in 3:00")


async def hlp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    to_send = "TO DO HELP"
    await application.bot.send_message(chat_id=user_id, text=to_send, parse_mode='HTML')


def main():
    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", hlp))
    asyncio.run(application.run_polling())


async def start_scheduler():
    while True:
        schedule.run_pending()
        await asyncio.sleep(30)

if __name__ == "__main__":
    schedule_thread = threading.Thread(target=asyncio.run, args=(start_scheduler(),))
    schedule_thread.start()
    main()
