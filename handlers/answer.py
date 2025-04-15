from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.users import record_test_attempt
from handlers.subject import send_next_question

def has_ongoing_test(context):
    return bool(context.user_data.get("current_test"))

async def end_test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not has_ongoing_test(context):
        await update.message.reply_text("No test in progress. Use /mock_test to begin a new test.")
        return
    
    await finish_test(update, context)

async def answer_callback(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    test = context.user_data.get("current_test")
    if not test:
        await query.answer("No test in progress. Use /mock_test to begin a new test.")
        return

    # Check if this is a disabled button
    if query.data.startswith("disabled_"):
        await query.answer("You've already answered this question!")
        return

    await query.answer()
    answer_index = int(query.data.split("_")[1])
    
    question = test["questions"][test["current_index"]]
    if answer_index == question["answer_index"]:
        test["score"] += 1
    
    # Store the user's answer for showing explanations later
    if "answers" not in test:
        test["answers"] = []
    
    test["answers"].append({
        "question_no": question.get("question_no", test["current_index"] + 1),
        "correct": answer_index == question["answer_index"],
        "explanation": question["explanation"]
    })

    # Update the message with ticked option and disabled buttons
    options = test["current_options"].copy()
    options[answer_index] = f"✓ {options[answer_index]}"
    
    buttons = [
        [InlineKeyboardButton(opt, callback_data=f"disabled_{i}")]
        for i, opt in enumerate(options)
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await query.edit_message_reply_markup(reply_markup=reply_markup)
    
    # Small delay before showing next question
    from asyncio import sleep
    await sleep(1)
    
    test["current_index"] += 1
    await send_next_question(query, context)

async def explain_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not has_ongoing_test(context):
        await update.message.reply_text("No test in progress. Use /mock_test to begin a new test.")
        return

    test = context.user_data.get("current_test")
    if "answers" not in test or not test["answers"]:
        await update.message.reply_text("No explanations available. You need to attempt some questions first.")
        return
    
    # Send explanations for all attempted questions
    for answer in test["answers"]:
        status = "✅" if answer["correct"] else "❌"
        await update.message.reply_text(
            f"{status} Q{answer['question_no']} Explanation: {answer['explanation']}"
        )

async def finish_test(update, context):
    test = context.user_data["current_test"]
    user_id = update.effective_user.id

    record_test_attempt(
        user_id,
        test["subject_code"],
        test["subject_name"],
        test["set_code"],
        test["score"],
        len(test["questions"])
    )

    # Show final score
    await update.message.reply_text(
        f"🎉 Test Completed!\nYour Score: {test['score']}/{len(test['questions'])}"
    )

    # Show all explanations at the end
    if "answers" in test:
        await update.message.reply_text("📝 Here are the explanations for all questions:")
        for answer in test["answers"]:
            status = "✅" if answer["correct"] else "❌"
            await update.message.reply_text(
                f"{status} Q{answer['question_no']} Explanation: {answer['explanation']}"
            )
    
    context.user_data.pop("current_test", None)
    await update.message.reply_text("You can now start a new test with /mock_test")
