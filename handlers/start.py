from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.users import create_or_update_user
from database.questions import get_available_subjects
from handlers.answer import has_ongoing_test

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    create_or_update_user(user.id, user.username, user.full_name)

    welcome_message = (
        f"👋 Hello {user.first_name}!\n\n"
        "Welcome to CUET Mock Test Bot! 📚\n\n"
        "Here's what you can do:\n"
        "• /mock_test - Start a mock test\n"
        "• /end_test - End current test and see results\n\n"
        "Ready to test your knowledge? Use /mock_test to begin!"
    )

    await update.message.reply_text(welcome_message)

async def mock_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if there's an ongoing test
    if has_ongoing_test(context):
        await update.message.reply_text(
            "❌ You have an ongoing test!\n"
            "Please either:\n"
            "1. Complete the current test, or\n"
            "2. Use /end_test to end the current test and see your results\n"
            "before starting a new one."
        )
        return

    subjects = get_available_subjects()
    
    if not subjects:
        await update.message.reply_text(
            "😕 No subjects are available at the moment. Please try again later."
        )
        return

    buttons = [
        [InlineKeyboardButton(subj, callback_data=f"start_{subj}")]
        for subj in subjects
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        "📝 Select a subject to begin your mock test:",
        reply_markup=reply_markup
    )
