from .db import db

def get_subject_collection(subject_name):
    return db[subject_name.lower().replace(" ", "_")]

def insert_question_set(subject_name, question_set):
    collection = get_subject_collection(subject_name)
    return collection.insert_one(question_set)

def get_random_set(subject_name):
    collection = get_subject_collection(subject_name)
    try:
        return collection.aggregate([{"$sample": {"size": 1}}]).next()
    except StopIteration:
        return None

def get_set_by_code(subject_name, set_code):
    collection = get_subject_collection(subject_name)
    return collection.find_one({"set_code": set_code})

def list_all_sets(subject_name):
    collection = get_subject_collection(subject_name)
    return list(collection.find({}, {"_id": 0, "set_code": 1}))

def get_available_subjects():
    # Get all collection names and filter out system collections
    all_collections = db.list_collection_names()
    system_collections = {'users', 'system.indexes'}  # Add other system collections if needed
    subject_collections = [coll for coll in all_collections if coll not in system_collections]
    
    # Convert collection names back to subject names (replace underscores with spaces and capitalize)
    subjects = [coll.replace('_', ' ').title() for coll in subject_collections]
    return sorted(subjects)

def get_all_sets(subject_name):
    collection = get_subject_collection(subject_name)
    return list(collection.find({}, {
        "_id": 0,
        "set_code": 1,
        "subject_code": 1,
        "total_questions": {"$size": "$questions"}
    }))

def get_all_subjects():
    """
    Get all available subjects with their codes and names.
    Returns a list of dictionaries with 'code' and 'name' keys.
    """
    # Get all collection names and filter out system collections
    all_collections = db.list_collection_names()
    system_collections = {'users', 'system.indexes'}  # Add other system collections if needed
    subject_collections = [coll for coll in all_collections if coll not in system_collections]
    
    subjects = []
    for collection_name in subject_collections:
        # Get a sample document to extract subject code and name
        collection = db[collection_name]
        sample_doc = collection.find_one({}, {"subject_code": 1, "subject_name": 1})
        if sample_doc and "subject_code" in sample_doc:
            subjects.append({
                "code": sample_doc["subject_code"],
                "name": sample_doc.get("subject_name", collection_name.replace('_', ' ').title())
            })
    
    return sorted(subjects, key=lambda x: x["code"])
