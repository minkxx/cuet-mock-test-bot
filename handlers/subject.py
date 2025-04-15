from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.questions import get_random_set

async def subject_callback(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    subject_name = query.data.split("_", 1)[1]
    test_set = get_random_set(subject_name)
    
    if test_set is None:
        await query.message.reply_text(f"Sorry, no questions are available for {subject_name} at the moment. Please try another subject.")
        return

    context.user_data["current_test"] = {
        "subject_name": subject_name,
        "subject_code": test_set["subject_code"],
        "set_code": test_set["set_code"],
        "questions": test_set["questions"],
        "current_index": 0,
        "score": 0
    }

    await send_next_question(query, context)

async def send_next_question(query, context):
    test = context.user_data["current_test"]
    index = test["current_index"]

    if index >= len(test["questions"]):
        from handlers.answer import finish_test
        await finish_test(query, context)
        return

    q = test["questions"][index]
    # Store original options for reference
    test["current_options"] = q["options"].copy()
    
    buttons = [
        [InlineKeyboardButton(opt, callback_data=f"answer_{i}")]
        for i, opt in enumerate(q["options"])
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    # Use question_no if available, fallback to index + 1 if not
    question_no = q.get("question_no", index + 1)
    
    await query.message.reply_text(
        f"Q{question_no}: {q['question']}",
        reply_markup=reply_markup
    )
