import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler
from chat_api import read_secret, openai_api
import httpx
import json

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def make_request(method, endpoint, data=None):
    url = f'http://gavmild_backend:5005/telegram/{endpoint}'
    headers = {
        "Content-Type": "application/json",
        'X-Api-Key': read_secret("bot-api-token")
        }

    async with httpx.AsyncClient() as client:
        response = await client.request(method, url, headers=headers, data=data)

    return response


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")



async def suggestion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    req_message = update.message.text.partition(' ')[2]
    if not req_message:
        content = f"Brukeren {update.message.from_user.first_name} har brukt kommandoen /forslag feil. Forklar brukeren i korthet at riktig bruk er /forslag Dette er mitt forslag."
        response = openai_api(content)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
        return "ok"

    data = {
        "username": update.message.from_user.username,
        "id": update.message.from_user.id,
        "suggestion": req_message
    }

    response = await make_request("POST", "suggestion", json.dumps(data))

    if response.status_code == 200:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Takk {update.message.from_user.first_name}, forslaget har blitt lagt til!")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Noe gikk dessverre galt.")  # Invalid API Key or the server encountered an error


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id == 79156661:
        if not context.args:
            await context.bot.send_message(chat_id=update.effective_chat.id, text='/slett <id>')
            return
        data = {
            "suggestion_id": context.args[0]
        }

        response = await make_request("DELETE", "suggestion", json.dumps(data))
        data = response.json()

        if response.status_code == 200:
            await context.bot.send_message(chat_id=update.effective_chat.id, text='Forslaget "' + data["message"] + '" ble slettet fordi det var idiotisk.')
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=data["message"])
        
    else:
        content = f"Forklar brukeren {update.message.from_user.first_name} at vedkommende ikke har tilstrekkelige rettigheter til å utføre handlingen."
        response = openai_api(content)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)


async def solve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id == 79156661:
        if not context.args:
            await context.bot.send_message(chat_id=update.effective_chat.id, text='/solve <id>')
            return
        data = {
            "suggestion_id": context.args[0]
        }

        response = await make_request("POST", "solve", json.dumps(data))
        data = response.json()

        if response.status_code == 200:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Forslaget "{data["message"]}" har blitt utført og fjernet fra listen.')
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=data["message"])
        
    else:
        content = f"Forklar brukeren {update.message.from_user.first_name} at vedkommende ikke har tilstrekkelige rettigheter til å utføre handlingen."
        response = openai_api(content)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)


async def hello_api(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = await make_request("GET", "api/data")

    if response.status_code == 200:
        data = response.json()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=data["message"])
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Noe gikk dessverre galt.")  # Invalid API Key or the server encountered an error


async def chatgpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = openai_api(update.message.text, "You are a friendly chat bot that love to small talk")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)


if __name__ == '__main__':
    application = ApplicationBuilder().token(read_secret("telegram-token")).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler("hello_api", hello_api))
    application.add_handler(CommandHandler("forslag", suggestion))
    application.add_handler(CommandHandler("slett", delete))
    application.add_handler(CommandHandler("solve", solve))
    #application.add_handler(MessageHandler(None, chatgpt))

    application.run_polling()

