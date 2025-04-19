from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from handlers.start import start, mock_test
from handlers.subject import subject_callback, set_callback
from handlers.answer import answer_callback, end_test_command
from handlers.admin import handle_json_file
from handlers.error_handler import error_handler
from handlers.leaderboard import leaderboard_command
from telegram.ext import MessageHandler, filters
from datetime import datetime, UTC

from config import BOT_TOKEN, LOG_GROUP_ID

async def send_startup_message(context):
    """Send a message to the log group when the bot starts."""
    startup_time = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    await context.bot.send_message(
        chat_id=LOG_GROUP_ID,
        text=f"🟢 Bot is now online!\nStartup Time: {startup_time}"
    )

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mock_test", mock_test))
    app.add_handler(CommandHandler("end_test", end_test_command))
    app.add_handler(CommandHandler("leaderboard", leaderboard_command))
    
    app.add_handler(CallbackQueryHandler(subject_callback, pattern="^start_"))
    app.add_handler(CallbackQueryHandler(set_callback, pattern="^set_"))
    app.add_handler(CallbackQueryHandler(answer_callback, pattern="^answer_"))
    app.add_handler(CallbackQueryHandler(answer_callback, pattern="^skip$"))
    app.add_handler(CallbackQueryHandler(answer_callback, pattern="^end_test$"))
    app.add_handler(MessageHandler(filters.Document.FileExtension("json"), handle_json_file))

    app.add_error_handler(error_handler)

    app.job_queue.run_once(send_startup_message, when=1)

    print("✅ CUET Bot is running...")
    app.run_polling()
