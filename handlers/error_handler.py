import html
import json
import traceback
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from datetime import datetime, UTC
from config import LOG_GROUP_ID

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before doing anything else
    print(f"Exception while handling an update:", file=open("error.log", "a"))
    traceback.print_exception(context.error, file=open("error.log", "a"))

    # Extract error information
    error_details = {
        "timestamp": datetime.now(UTC).isoformat(),
        "error_type": type(context.error).__name__,
        "error_message": str(context.error),
        "update_type": None,
        "chat_type": None,
        "chat_id": None,
        "user_id": None,
        "username": None,
        "message_text": None,
        "command": None
    }

    # Extract update information if available
    if update and update.effective_message:
        message = update.effective_message
        error_details.update({
            "update_type": "message",
            "chat_type": message.chat.type,
            "chat_id": message.chat.id,
            "user_id": message.from_user.id if message.from_user else None,
            "username": message.from_user.username if message.from_user else None,
            "message_text": message.text,
            "command": message.text.split()[0] if message.text and message.text.startswith('/') else None
        })
    elif update and update.callback_query:
        callback = update.callback_query
        error_details.update({
            "update_type": "callback_query",
            "chat_type": callback.message.chat.type if callback.message else None,
            "chat_id": callback.message.chat.id if callback.message else None,
            "user_id": callback.from_user.id,
            "username": callback.from_user.username,
            "message_text": callback.data
        })

    # Format traceback
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    # Format message for Telegram
    message = (
        f"⚠️ <b>An error occurred:</b>\n\n"
        f"<b>Error Type:</b> <code>{html.escape(error_details['error_type'])}</code>\n"
        f"<b>Error Message:</b> <code>{html.escape(error_details['error_message'])}</code>\n\n"
        f"<b>Update Type:</b> {error_details['update_type']}\n"
        f"<b>Chat Type:</b> {error_details['chat_type']}\n"
        f"<b>Chat ID:</b> <code>{error_details['chat_id']}</code>\n"
        f"<b>User ID:</b> <code>{error_details['user_id']}</code>\n"
        f"<b>Username:</b> {('@' + error_details['username']) if error_details['username'] else 'None'}\n"
        f"<b>Message/Command:</b> <code>{html.escape(str(error_details['message_text']))}</code>\n\n"
        f"<b>Traceback:</b>\n<code>{html.escape(tb_string)}</code>"
    )

    # Split message if it's too long
    if len(message) > 4096:
        for x in range(0, len(message), 4096):
            await context.bot.send_message(
                chat_id=LOG_GROUP_ID,
                text=message[x:x+4096],
                parse_mode=ParseMode.HTML
            )
    else:
        await context.bot.send_message(
            chat_id=LOG_GROUP_ID,
            text=message,
            parse_mode=ParseMode.HTML
        )

    # Also save error details to a JSON file for later analysis
    try:
        with open('error_log.json', 'a') as f:
            json.dump(error_details, f)
            f.write('\n')
    except Exception as e:
        print(f"Failed to write to error_log.json: {e}")

    # If the error is critical, we might want to reply to the user
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "An error occurred while processing your request. "
            "The development team has been notified."
        ) 