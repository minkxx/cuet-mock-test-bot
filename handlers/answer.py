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
    
    # Handle end test action
    if query.data == "end_test":
        await finish_test(update, context)
        return
        
    # Handle skip action
    if query.data == "skip":
        test["current_index"] += 1
        await send_next_question(query, context)
        return
    
    answer_index = int(query.data.split("_")[1])
    
    question = test["questions"][test["current_index"]]
    if answer_index == question["answer_index"]:
        test["score"] += 5
    else:
        test["score"] -= 1
    
    # Store the user's answer
    if "answers" not in test:
        test["answers"] = []
    
    test["answers"].append({
        "question_no": question.get("question_no", test["current_index"] + 1),
        "correct": answer_index == question["answer_index"]
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

async def finish_test(update, context):
    test = context.user_data["current_test"]
    
    # Handle different types of update objects
    if hasattr(update, 'callback_query'):  # Full Update object with callback_query
        user_id = update.callback_query.from_user.id
        message = update.callback_query.message
    elif hasattr(update, 'message'):  # Full Update object from command
        user_id = update.effective_user.id
        message = update.message
    else:  # Direct Message object
        message = update
        user_id = context.user_data.get("current_test", {}).get("user_id")

    record_test_attempt(
        user_id,
        test["subject_code"],
        test["subject_name"],
        test["set_code"],
        test["score"],
        len(test["questions"])
    )

    # Show final score
    max_score = len(test["questions"]) * 5
    await message.reply_text(
        f"🎉 Test Completed!\nYour Score: {test['score']}/{max_score}"
    )

    # Prepare the answers summary
    if "answers" in test:
        answers_summary = [
            "📝 Here are the correct answers:",
            "",
            "Legend:",
            "✅ - Correct answer",
            "❌ - Wrong answer",
            "⏭️ - Skipped/Not attempted",
            ""
        ]
        questions = test["questions"]
        
        for i in range(len(questions)):
            q = questions[i]
            question_no = q.get("question_no", i + 1)
            correct_option = q["options"][q["answer_index"]]
            
            # Check if this question was attempted
            user_answer = None
            for ans in test.get("answers", []):
                if ans["question_no"] == question_no:
                    user_answer = "✅" if ans["correct"] else "❌"
                    break
            
            status = user_answer if user_answer else "⏭️"  # Skip symbol if not attempted
            answers_summary.append(f"{status} Q{question_no}: {correct_option}")
        
        # Send all answers in a single message
        await message.reply_text("\n".join(answers_summary))
    
    context.user_data.pop("current_test", None)
    await message.reply_text("You can now start a new test with /mock_test")
