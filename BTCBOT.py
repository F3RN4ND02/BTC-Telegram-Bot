"""
Hi! This is a simple bot to update the price from Binance and send you the updated price.
"""

import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from binance.client import Client

# Declare the Binance Key and Secret (This will be revoked)
api_key = 'YOUR_BINANCE_API_ KEY'
api_secret = 'YOUR_BINANCE_SECRET_KEY'
# Declare to the python-binance library
client = Client(api_key, api_secret)

# Enable logging to debug
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)


# BTC
# With this function we will request the actual price

def price(context: CallbackContext):
    # Using the test URL
    client.API_URL = 'https://testnet.binance.vision/api'
    # Send the command to get the price
    btc_price = client.get_symbol_ticker(symbol="BTCUSDT")
    # Extract the price from the JSON format
    a = btc_price['price']
    # Convert the variable to float
    b = float(a)
    # Round the number up to 2 decimals
    c = round(b, 2)
    # Creating the string
    btc_price2 = "The BTC-USDT price is " + str(c)
    # Creating the Job
    job = context.job
    # Send the Message
    context.bot.send_message(job.context, text=btc_price2)
    return btc_price2


def start(update: Update, context: CallbackContext) -> None:
    """Sends explanation on how to use the bot."""
    update.message.reply_text(
        'Hi! You have reached the BTC-USDT update price bot. Please use /set <minutes> to explain how often you wish to receive the news. /unset to stop the news. Enjoy!')


def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def set_timer(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(context.args[0]) * 60  # We will convert it to minutes
        if due < 60:
            update.message.reply_text(
                'Sorry my friend, the updates MUST be more than 1 per minute.')
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        # This is what making the repeating task
        context.job_queue.run_repeating(
            price, due, context=chat_id, name=str(chat_id))

        min = due // 60  # To inform how many minutes you will receive the update
        text = 'Excellent, you will receive the updates every ' + \
            str(min) + ' minute(s)'
        # We run the price once to get it now and then every due minutes
        context.job_queue.run_once(
            price, 0, context=chat_id, name=str(chat_id))
        # Will remove it, according new instructions
        if job_removed:
            text += ', Old update time has been removed.'
        update.message.reply_text(text)
        # If it has an error
    except (IndexError, ValueError):
        update.message.reply_text(
            'Usage: /set <minutes>, remember that MUST be more than 1 per minute')

# To cancel the job


def unset(update: Update, context: CallbackContext) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'You have cancelled the updates' if job_removed else 'You have no active updates. Use /set <minutes> to create one'
    update.message.reply_text(text)


def main() -> None:
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("set", set_timer))
    dispatcher.add_handler(CommandHandler("unset", unset))

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
