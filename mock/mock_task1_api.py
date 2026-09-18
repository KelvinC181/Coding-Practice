"""
MOCK TASK 1 — API Development & Data Handling      (suggested time: ~40 min)
=============================================================================

PROBLEM: Support Ticket Submission Endpoint

Implement `handle_ticket_submission(raw_json_payload: str) -> tuple[int, str]`
that validates a raw JSON string and returns (status_code, json_response_body).

REQUIRED FIELDS
  - ticket_id      : string, must match format "TCK-" followed by EXACTLY 6 digits
                      (e.g. "TCK-000123"). No other format is valid.
  - priority        : string, must be one of: "low", "medium", "high", "critical"
  - description     : string, length must be between 10 and 500 characters (inclusive)
  - reporter_email  : string, must be a syntactically valid email address

OPTIONAL FIELD
  - tags            : list of strings. If present:
                        - max 5 tags
                        - each tag must be 1–20 characters
                        - if invalid, reject the whole request

RESPONSES
  - 400  Malformed JSON, or JSON is not an object (e.g. it's a list/string/number)
          body: {"status": "error", "message": "Invalid JSON format"}
  - 422  Missing a required field, or any field fails its validation rule
          body: {"status": "error", "message": "<field>: <what's wrong>"}
          (the message MUST name the offending field — this bit people in practice!)
  - 201  All valid
          body: {"status": "success", "data": {...all fields, including tags if present...}}

EDGE CASES TO THINK ABOUT (some are deliberately in the test cases below):
  - ticket_id "TCK-12345" (5 digits) or "TCK-1234567" (7 digits) -> invalid
  - priority "Low" (wrong case) -> invalid (case-sensitive)
  - description exactly 10 chars -> valid (boundary); 9 chars -> invalid
  - tags = [] (empty list present) -> should this be treated as "no tags"? decide and be consistent
  - tags = ["a", 123] (mixed types) -> invalid
"""

import json
import re


def handle_ticket_submission(raw_json_payload: str) -> tuple[int, str]:
    # TODO: implement

    prioriteis = ["low", "medium", "high", "critical"]

    #test for if input is json
    try:
        json_dict = json.loads(raw_json_payload)
    except:
        return(400,json.dumps({"status": "error", "message": "Invalid JSON format"}))

    #test for if json is in dict form
    if not isinstance(json_dict, dict):
        return(400,json.dumps({"status": "error", "message": "Invalid JSON format"}))

    #get all variables
    ticket_id = json_dict.get("ticket_id")
    priority = json_dict.get("priority")
    description = json_dict.get("description")
    reporter_email = json_dict.get("reporter_email")
    tags = json_dict.get("tags")

    #check if empty for each required field
    if not ticket_id:
        return (422,json.dumps({"status": "error", "message": "ticket_id: missing"}))
    if not priority:
        return (422,json.dumps({"status": "error", "message": "priority: missing"}))
    if not description:
        return (422,json.dumps({"status": "error", "message": "description: missing"}))
    if not reporter_email:
        return (422,json.dumps({"status": "error", "message": "reporter_email: missing"}))

    #check for valid information
    if not isinstance(ticket_id, str) or not re.fullmatch("TCK-[0-9]{6}" ,ticket_id):
        return (422,json.dumps({"status": "error", "message": "ticket_id: invalid"}))

    if not isinstance(priority, str) or priority not in prioriteis:
        return (422,json.dumps({"status": "error", "message": "priority: invalid"}))

    if not isinstance(description, str) or len(description) < 10 or len(description) > 500:
        return (422,json.dumps({"status": "error", "message": "description: invalid"}))

    if not isinstance(reporter_email, str) or not re.fullmatch("[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}" ,reporter_email):
        return (422,json.dumps({"status": "error", "message": "reporter_email: invalid"}))

    #ignores tags if empty
    if isinstance(tags,list):
        if len(tags) > 5:
            return (422,json.dumps({"status": "error", "message": "tags: exceed tag limit"}))
        for tag in tags:
            if not isinstance(tag, str) or len(tag)<1 or len(tag)>20:
                return (422,json.dumps({"status": "error", "message": "tags: invalid"}))
        return  (201,json.dumps({"status": "success", "data": {"ticket_id":ticket_id, "priority":priority, "description":description, "reporter_email":reporter_email, "tags":tags}}))
            
    #passes all checks
    return  (201,json.dumps({"status": "success", "data": {"ticket_id":ticket_id, "priority":priority, "description":description, "reporter_email":reporter_email}}))
    
        



# ---------------------------------------------------------------------
# Self-check harness — run this file directly once you've implemented
# the function above. It does NOT reveal the implementation.
# ---------------------------------------------------------------------

def _run():
    results = []

    def check(name, payload_dict_or_str, expect_status, extra_check=None):
        payload = json.dumps(payload_dict_or_str) if not isinstance(payload_dict_or_str, str) else payload_dict_or_str
        try:
            status, body_str = handle_ticket_submission(payload)
            body = json.loads(body_str)
            ok = (status == expect_status)
            if ok and extra_check:
                ok = extra_check(body)
            results.append((name, "PASS" if ok else f"FAIL (got status={status}, body={body})"))
        except NotImplementedError:
            results.append((name, "NOT IMPLEMENTED"))
        except Exception as e:
            results.append((name, f"ERROR: {e}"))

    valid = {
        "ticket_id": "TCK-000123",
        "priority": "high",
        "description": "The login page throws a 500 error on submit.",
        "reporter_email": "alex@example.com",
    }

    check("valid_no_tags", valid, 201)
    check("valid_with_tags", {**valid, "tags": ["bug", "urgent"]}, 201)
    check("malformed_json", '{"ticket_id": "TCK-000123"', 400)
    check("json_is_a_list", ["not", "a", "dict"], 400)
    check("missing_field_priority", {k: v for k, v in valid.items() if k != "priority"}, 422)
    check("bad_ticket_id_5_digits", {**valid, "ticket_id": "TCK-12345"}, 422)
    check("bad_ticket_id_7_digits", {**valid, "ticket_id": "TCK-1234567"}, 422)
    check("bad_priority_case", {**valid, "priority": "High"}, 422)
    check("bad_priority_value", {**valid, "priority": "urgent"}, 422)
    check("description_9_chars", {**valid, "description": "too short"}, 422)  # 9 chars
    check("description_10_chars_boundary", {**valid, "description": "1234567890"}, 201)  # exactly 10
    check("bad_email", {**valid, "reporter_email": "not-an-email"}, 422)
    check("too_many_tags", {**valid, "tags": ["a", "b", "c", "d", "e", "f"]}, 422)
    check("tag_too_long", {**valid, "tags": ["x" * 21]}, 422)
    check("tag_wrong_type", {**valid, "tags": ["ok", 123]}, 422)
    check("message_names_the_field", {k: v for k, v in valid.items() if k != "priority"}, 422,
          extra_check=lambda body: "priority" in body.get("message", "").lower())

    for name, result in results:
        print(f"{name:35} {result}")


if __name__ == "__main__":
    _run()
