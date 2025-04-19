from config import ADMIN_IDS

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def validate_test_set_json(data: dict) -> bool:
    # Check required top-level keys
    required_keys = ["subject_code", "subject_name", "set_code", "questions"]
    if not all(key in data for key in required_keys):
        return False

    # Check if questions is a list and has exactly 50 questions
    if not isinstance(data["questions"], list) or len(data["questions"]) != 50:
        return False

    # Validate each question
    for q in data["questions"]:
        # Check required question keys
        if not all(k in q for k in ("question_no", "question", "options", "answer_index")):
            return False
        
        # Validate options
        if not isinstance(q["options"], list) or len(q["options"]) != 4:
            return False
        
        # Validate answer_index is within range
        if not isinstance(q["answer_index"], int) or q["answer_index"] not in range(4):
            return False
        
        # Validate question_no is an integer and within range
        if not isinstance(q["question_no"], int) or q["question_no"] not in range(1, 51):
            return False

    return True
