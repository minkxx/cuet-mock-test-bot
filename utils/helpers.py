from config import ADMIN_IDS

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def validate_test_set_json(data: dict) -> bool:
    required_keys = ["subject_code", "subject_name", "set_code", "questions"]
    for key in required_keys:
        if key not in data:
            return False
    if not isinstance(data["questions"], list) or len(data["questions"]) != 50:
        return False
    for q in data["questions"]:
        if not all(k in q for k in ("question", "options", "answer_index", "explanation")):
            return False
        if not isinstance(q["options"], list) or len(q["options"]) != 4:
            return False
    return True
