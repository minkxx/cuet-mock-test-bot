from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.questions import get_all_sets, get_set_by_code
from database.users import get_user_history

async def subject_callback(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    subject_name = query.data.split("_", 1)[1]
    
    # Get all available sets for the subject
    sets = get_all_sets(subject_name)
    if not sets:
        await query.message.reply_text(f"Sorry, no question sets are available for {subject_name} at the moment. Please try another subject.")
        return

    # Get user's attempt history for this subject
    user_history = get_user_history(query.from_user.id)
    attempts_by_set = {}
    
    # Create a dictionary of set_code -> best score
    for attempt in user_history:
        if attempt["subject_name"] == subject_name:
            set_code = attempt["set_code"]
            score = attempt["score"]
            total = attempt["total"]
            
            if set_code not in attempts_by_set or score > attempts_by_set[set_code]["score"]:
                attempts_by_set[set_code] = {"score": score, "total": total}

    # Create buttons for each set with attempt status
    buttons = []
    for set_info in sets:
        set_code = set_info["set_code"]
        total_questions = set_info["total_questions"]
        
        if set_code in attempts_by_set:
            # Show best score if attempted
            best_attempt = attempts_by_set[set_code]
            button_text = f"Set {set_code} - Best: {best_attempt['score']}/{best_attempt['total']}"
        else:
            # Show as unattempted
            button_text = f"Set {set_code} - Unattempted"
        
        buttons.append([InlineKeyboardButton(button_text, callback_data=f"set_{subject_name}_{set_code}")])

    reply_markup = InlineKeyboardMarkup(buttons)

    await query.message.reply_text(
        f"📝 Available sets for {subject_name}:\n"
        "Select a set to begin the test:",
        reply_markup=reply_markup
    )

async def set_callback(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Extract subject and set code from callback data
    _, subject_name, set_code = query.data.split("_", 2)
    
    # Get the specific set
    test_set = get_set_by_code(subject_name, set_code)
    if not test_set:
        await query.message.reply_text(f"Sorry, this set is no longer available. Please choose another set.")
        return

    context.user_data["current_test"] = {
        "subject_name": subject_name,
        "subject_code": test_set["subject_code"],
        "set_code": set_code,
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
