import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler
from chat_api import openai_api


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def read_secret(secret_name):
    try:
        with open(f"/run/secrets/{secret_name}", "r") as secret_file:
            return secret_file.read().strip()
    except IOError:
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


import httpx
async def hello_api(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = 'http://gavmild_backend:5005/telegram/api/data'
    headers = {'X-Api-Key': 'Your-API-Key'}  # Replace with your actual API key

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=data["message"])
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to make request.")  # Invalid API Key or the server encountered an error

async def chatgpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = openai_api(update.message.text, "You are a friendly chat bot that love to small talk")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

if __name__ == '__main__':
    application = ApplicationBuilder().token(read_secret("telegram-token")).build()

    start_handler = CommandHandler('start', start)
    hello_handler = CommandHandler("hello_api", hello_api)
    chatgpt_handler = MessageHandler(None, chatgpt)
    application.add_handler(start_handler)
    application.add_handler(hello_handler)
    application.add_handler(chatgpt_handler)

    application.run_polling()

