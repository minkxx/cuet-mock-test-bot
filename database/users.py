from .db import db
from datetime import datetime, UTC

users_collection = db["users"]

def create_or_update_user(user_id, username=None, name=None):
    users_collection.update_one(
        {"user_id": user_id},
        {
            "$setOnInsert": {
                "user_id": user_id,
                "username": username,
                "name": name,
                "joined_at": datetime.now(UTC),
                "last_test_attempt": None,
                "tests_attempted": []
            }
        },
        upsert=True
    )

def record_test_attempt(user_id, subject_code, subject_name, set_code, score, total):
    current_time = datetime.now(UTC)
    test_result = {
        "subject_code": subject_code,
        "subject_name": subject_name,
        "set_code": set_code,
        "score": score,
        "total": total,
        "attempted_on": current_time
    }

    users_collection.update_one(
        {"user_id": user_id},
        {
            "$push": {"tests_attempted": test_result},
            "$set": {"last_test_attempt": current_time}
        }
    )

def get_user_history(user_id):
    user = users_collection.find_one({"user_id": user_id}, {"_id": 0, "tests_attempted": 1})
    return user.get("tests_attempted", []) if user else []

def has_attempted_set(user_id, set_code):
    user = users_collection.find_one(
        {"user_id": user_id, "tests_attempted.set_code": set_code}
    )
    return bool(user)

def get_user_info(user_id):
    user = users_collection.find_one(
        {"user_id": user_id},
        {
            "_id": 0,
            "user_id": 1,
            "username": 1,
            "name": 1,
            "joined_at": 1,
            "last_test_attempt": 1,
            "tests_attempted": {"$slice": -5}  # Get only the last 5 attempts
        }
    )
    return user

def get_subject_leaderboard(subject_code):
    """
    Get top 10 users for a specific subject based on their highest score.
    Returns a list of users with their best scores for the subject.
    """
    pipeline = [
        # Unwind the tests_attempted array to work with individual test attempts
        {"$unwind": "$tests_attempted"},
        # Match documents for the specific subject
        {"$match": {"tests_attempted.subject_code": subject_code}},
        # Group by user to get their highest score
        {
            "$group": {
                "_id": {
                    "user_id": "$user_id",
                    "username": "$username",
                    "name": "$name"
                },
                "highest_score": {"$max": "$tests_attempted.score"},
                "total_questions": {"$first": "$tests_attempted.total"},
                "subject_name": {"$first": "$tests_attempted.subject_name"}
            }
        },
        # Sort by highest score in descending order
        {"$sort": {"highest_score": -1}},
        # Limit to top 10 users
        {"$limit": 10},
        # Project the final format
        {
            "$project": {
                "_id": 0,
                "user_id": "$_id.user_id",
                "username": "$_id.username",
                "name": "$_id.name",
                "score": "$highest_score",
                "total": "$total_questions",
                "subject_name": "$subject_name"
            }
        }
    ]
    
    return list(users_collection.aggregate(pipeline))

def get_overall_leaderboard():
    """
    Get top 10 users across all subjects based on their total score percentage.
    Returns a list of users with their overall performance.
    """
    pipeline = [
        # Unwind the tests_attempted array to work with individual test attempts
        {"$unwind": "$tests_attempted"},
        # Group by user and subject to get highest score per subject
        {
            "$group": {
                "_id": {
                    "user_id": "$user_id",
                    "username": "$username",
                    "name": "$name",
                    "subject_code": "$tests_attempted.subject_code"
                },
                "highest_score": {"$max": "$tests_attempted.score"},
                "total_questions": {"$first": "$tests_attempted.total"}
            }
        },
        # Group by user to calculate overall performance
        {
            "$group": {
                "_id": {
                    "user_id": "$_id.user_id",
                    "username": "$_id.username",
                    "name": "$_id.name"
                },
                "total_score": {"$sum": "$highest_score"},
                "total_questions": {"$sum": "$total_questions"},
                "subjects_attempted": {"$sum": 1}
            }
        },
        # Add percentage field
        {
            "$addFields": {
                "percentage": {
                    "$multiply": [
                        {"$divide": ["$total_score", "$total_questions"]},
                        100
                    ]
                }
            }
        },
        # Sort by percentage in descending order
        {"$sort": {"percentage": -1}},
        # Limit to top 10 users
        {"$limit": 10},
        # Project the final format
        {
            "$project": {
                "_id": 0,
                "user_id": "$_id.user_id",
                "username": "$_id.username",
                "name": "$_id.name",
                "score": "$total_score",
                "total": "$total_questions",
                "percentage": 1,
                "subjects_attempted": 1
            }
        }
    ]
    
    return list(users_collection.aggregate(pipeline))
