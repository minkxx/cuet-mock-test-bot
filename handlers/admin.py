import json
from telegram import Update
from telegram.ext import ContextTypes

from utils.helpers import is_admin, validate_test_set_json
from database.questions import get_subject_collection

async def handle_json_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("🚫 You are not authorized to upload test sets.")
        return

    document = update.message.document
    if not document.file_name.endswith(".json"):
        await update.message.reply_text("❗ Please upload a valid JSON file.")
        return

    file = await context.bot.get_file(document.file_id)
    json_bytes = await file.download_as_bytearray()
    
    try:
        data = json.loads(json_bytes)
    except json.JSONDecodeError:
        await update.message.reply_text("❌ Invalid JSON format. Please check your file.")
        return

    if not validate_test_set_json(data):
        await update.message.reply_text(
            "❌ Invalid test set format. Please ensure:\n"
            "1. Required fields are present: subject_code, subject_name, set_code, questions\n"
            "2. Exactly 50 questions are included\n"
            "3. Each question has: question_no (1-50), question, options (4), answer_index (0-3)\n"
            "4. Question numbers are sequential from 1 to 50"
        )
        return

    collection = get_subject_collection(data["subject_name"])
    if collection.find_one({"set_code": data["set_code"]}):
        await update.message.reply_text(
            f"⚠️ Set code '{data['set_code']}' already exists for {data['subject_name']}."
        )
    else:
        collection.insert_one(data)
        await update.message.reply_text(
            f"✅ New test set '{data['set_code']}' added to {data['subject_name']}!\n"
            f"• Subject Code: {data['subject_code']}\n"
            f"• Questions: {len(data['questions'])}"
        )
