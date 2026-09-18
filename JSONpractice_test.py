import json
import re
import pytest

input_1 = '{"username": "Alex99", "email": "alex@example.com", "age": 21, "roles": ["user"]}'
input_2 = '{"username": "Alex99", "age": 21}'
input_3 = '{"username": "Alex!", "email": "alex@example.com", "age": 17}'
input_4 = '{"username": "Alex99", "email": "alex@'

def handle_registration(raw_json_payload):
    #validates JSON format
    
    #checks its actually json
    try:
        json_text = json.loads(raw_json_payload)
    except json.JSONDecodeError:
        return (400,json.dumps({"status": "error", "message": "Invalid JSON format"}))
    #checks its a dict
    if not isinstance(json_text,dict):
        return (400,json.dumps({"status": "error", "message": "Invalid JSON format"}))

    username = json_text.get("username")
    email = json_text.get("email")
    age = json_text.get("age")

    #validate no empty fields
    if not username or not email or not age:
        return (422,json.dumps({"status": "error", "message": "One or more empty field"}))

    #validate username    
    if not isinstance(username, str) or not re.fullmatch("[A-Za-z0-9]+",username) or len(username) < 3 or len(username) > 20 :
        return (422,json.dumps({"status": "error", "message": "Invalid username"}))

    #validate email
    if not isinstance(email, str) or not re.fullmatch("[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}",email):
        return (422,json.dumps({"status": "error", "message": "Invalid email"}))

    #validate age
    if not isinstance(age, int) or age < 18:
        return (422,json.dumps({"status": "error", "message": "Invalid email"}))

    roles = json_text.get("roles")

    if roles:
        for role in roles:
            if role != "user" and role != "admin" and role != "editor":
                return (422,json.dumps({"status": "error", "message": "Invalid roles"}))
        return (201,json.dumps({"status": "success", "data": {"username": username, "email": email, "age": age, "roles": roles}}))

    return (201,json.dumps({"status": "success", "data": {"username": username, "email": email, "age": age}}))


# ==========================================
# TEST CODE WRITTEN BY GEMINI
# ==========================================

def run_test(function_under_test, payload_str):
    """Utility to execute function and parse response body JSON."""
    status_code, response_json_str = function_under_test(payload_str)
    response_body = json.loads(response_json_str)
    return status_code, response_body


# --- TEST SUITE ---

def test_valid_registration_without_roles():
    payload = json.dumps({
        "username": "ValidUser123",
        "email": "user@domain.com",
        "age": 25
    })
    status, body = run_test(handle_registration, payload)
    
    assert status == 201
    assert body["status"] == "success"
    assert body["data"]["username"] == "ValidUser123"
    assert body["data"]["email"] == "user@domain.com"
    assert body["data"]["age"] == 25


def test_valid_registration_with_allowed_roles():
    payload = json.dumps({
        "username": "AdminUser",
        "email": "admin@domain.co.uk",
        "age": 30,
        "roles": ["admin", "user"]
    })
    status, body = run_test(handle_registration, payload)
    
    assert status == 201
    assert body["status"] == "success"


def test_malformed_json_syntax():
    payload = '{"username": "Alex", "email": "alex@'  # Unclosed string/JSON
    status, body = run_test(handle_registration, payload)
    
    assert status == 400
    assert body["status"] == "error"
    assert "Invalid JSON" in body["message"]


def test_payload_not_a_json_dict():
    payload = json.dumps(["username", "email", "age"])  # JSON array instead of object
    status, body = run_test(handle_registration, payload)
    
    assert status == 400
    assert body["status"] == "error"


@pytest.mark.parametrize("missing_field", ["username", "email", "age"])
def test_missing_required_fields(missing_field):
    data = {"username": "ValidUser", "email": "valid@test.com", "age": 20}
    del data[missing_field]
    
    status, body = run_test(handle_registration, json.dumps(data))
    
    assert status == 422
    assert body["status"] == "error"
    assert missing_field in body["message"]


@pytest.mark.parametrize("invalid_username", [
    "ab",                       # Too short (< 3 chars)
    "a" * 21,                   # Too long (> 20 chars)
    "user_name!",               # Special characters (not alphanumeric)
    12345                       # Incorrect type (integer instead of string)
])
def test_invalid_usernames(invalid_username):
    payload = json.dumps({"username": invalid_username, "email": "test@test.com", "age": 20})
    status, body = run_test(handle_registration, payload)
    
    assert status == 422
    assert body["status"] == "error"


@pytest.mark.parametrize("invalid_email", [
    "not_an_email",             # Missing @
    "user@@test.com",           # Double @
    "user@domain",              # Missing dot in domain
    "@domain.com"               # Missing recipient before @
])
def test_invalid_emails(invalid_email):
    payload = json.dumps({"username": "ValidUser", "email": invalid_email, "age": 20})
    status, body = run_test(handle_registration, payload)
    
    assert status == 422
    assert body["status"] == "error"


@pytest.mark.parametrize("invalid_age", [
    17,                         # Under 18
    "20",                       # String instead of int
    True,                       # Boolean (Pytest checks boolean edge-case)
    -5                          # Negative integer
])
def test_invalid_ages(invalid_age):
    payload = json.dumps({"username": "ValidUser", "email": "test@test.com", "age": invalid_age})
    status, body = run_test(handle_registration, payload)
    
    assert status == 422
    assert body["status"] == "error"


@pytest.mark.parametrize("invalid_roles", [
    "admin",                    # Not a list
    ["admin", "super_user"],    # Disallowed role value
    [123, 456]                  # List of integers instead of strings
])
def test_invalid_optional_roles(invalid_roles):
    payload = json.dumps({
        "username": "ValidUser", 
        "email": "test@test.com", 
        "age": 20, 
        "roles": invalid_roles
    })
    status, body = run_test(handle_registration, payload)
    
    assert status == 422
    assert body["status"] == "error"