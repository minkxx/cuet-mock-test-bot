from telegram import Update
from telegram.ext import ContextTypes
from database.users import get_subject_leaderboard
from database.questions import get_all_subjects

async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the leaderboard for a specific subject"""
    message = update.message
    
    # Get all available subjects
    subjects = get_all_subjects()
    
    if not context.args:
        # If no subject code provided, show available subjects
        subject_list = "\n".join([f"{subject['code']} - {subject['name']}" for subject in subjects])
        await message.reply_text(
            "Please specify a subject code to view its leaderboard.\n"
            "Available subjects:\n"
            f"{subject_list}\n\n"
            "Example: /leaderboard 308"
        )
        return
    
    subject_code = context.args[0].upper()
    
    # Check if subject exists
    subject_exists = any(subject['code'] == subject_code for subject in subjects)
    if not subject_exists:
        await message.reply_text(f"Subject code '{subject_code}' not found. Please use a valid subject code.")
        return
    
    # Get the leaderboard for the specified subject
    leaderboard = get_subject_leaderboard(subject_code)
    
    if not leaderboard:
        await message.reply_text(f"No attempts found for subject {subject_code}.")
        return
    
    # Format the leaderboard message
    subject_name = leaderboard[0]['subject_name']
    response = f"🏆 Top 10 Leaderboard - {subject_name} ({subject_code})\n\n"
    
    for idx, entry in enumerate(leaderboard, 1):
        name = entry['name'] or entry['username'] or f"User{entry['user_id']}"
        percentage = (entry['score'] / entry['total']) * 100
        response += f"{idx}. {name}: {entry['score']}/{entry['total']} ({percentage:.1f}%)\n"
    
    await message.reply_text(response)
