
import pytest
import requests
from pytest_bdd import scenarios, given, when, then, parsers
import os
import time
from datetime import datetime


from test.utils.validators import validate_response_status, validate_html_response, extract_reasoning_block, validate_reasoning_grammar

scenarios("../features/ai_onboarding.feature")


# Save API response to logs/
def log_api_response(name: str, content: str):
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"logs/{name}_{timestamp}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"{name} API response written to {filename}")


@pytest.fixture
def context():
    return {}


@given("a user logs in with valid credentials")
def login_user(context):
    login_url = "https://cc1fbde45ead-in-south-01.backstract.io/sigma/api/v1/users_login/login"
    payload = {
        "email_id": "shivam123@yopmail.com",
        "password": "Pass@9988"
    }

    res = requests.post(login_url, json=payload)
    print("\nLogin Response:", res.status_code)
    log_api_response("login", res.text)

    validate_response_status(res)
    context["auth_token"] = res.json()["value"]
    return context


@when("the user creates a new workspace")
def create_workspace(context):
    url = "https://cc1fbde45ead-in-south-01.backstract.io/sigma/api/v1/workspace/create"
    headers = {"Authorization": f"Bearer {context['auth_token']}"}
    payload = {"workspace_name": "International Student Network1"}

    res = requests.post(url, json=payload, headers=headers)
    print("\n🛠️ Workspace Creation:", res.status_code)
    log_api_response("create_workspace", res.text)

    validate_response_status(res)
    context["workspace_id"] = res.json()["value"]["workspace_id"]
    return context


@when("a preflight request is made to create a collection")
def preflight_create_collection(context):
    url = "https://cc1fbde45ead-in-south-01.backstract.io/sigma/api/v1/ai_generator/preflight_create_collection"
    headers = {"Authorization": f"Bearer {context['auth_token']}"}
    payload = {"workspace_id": context["workspace_id"]}

    res = requests.post(url, json=payload, headers=headers)
    print("\nPreflight:", res.status_code)
    log_api_response("preflight_create_collection", res.text)

    validate_response_status(res)
    data = res.json()["value"]
    context["collection_id"] = data["collection_id"]
    context["collection_name"] = data["collection_name"]
    return context


@when(parsers.parse('the user sends an AI prompt "{prompt}"'))
def send_ai_prompt(context, prompt):
    url = "https://cc1fbde45ead-in-south-01.backstract.io/sigma/api/v1/ai_generator/generate_initial_crud"
    headers = {"Authorization": f"Bearer {context['auth_token']}"}
    payload = {
        "prompt": prompt,
        "dialect": "SQLite",
        "workspace_id": context["workspace_id"],
        "collection_id": context["collection_id"],
        "collection_name": context["collection_name"]
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"\nSending AI prompt (Attempt {attempt + 1}): {prompt}")
            res = requests.post(url, json=payload, headers=headers, timeout=90)
            res.raise_for_status()

            context["ai_response"] = res.text
            log_api_response("ai_response", res.text)
            print("\nFull AI Response Preview:\n", res.text[:1000], "...")
            return context

        except requests.exceptions.ChunkedEncodingError as ce:
            print(f"ChunkedEncodingError (Attempt {attempt + 1}): {ce}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            else:
                raise AssertionError("AI response failed after retries due to chunked encoding issues.")

        except requests.exceptions.ReadTimeout as te:
            print(f"⏱ReadTimeout (Attempt {attempt + 1}): {te}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            else:
                raise AssertionError("AI response timed out after retries.")

        except Exception as e:
            print(f"Unexpected error: {e}")
            raise


@then("the schema and reasoning should be returned correctly")
def check_ai_response_structure(context):
    html = context["ai_response"]
    validate_html_response(html)

    reasoning = extract_reasoning_block(html)
    context["parsed_reasoning"] = reasoning
    print("\nExtracted Reasoning:\n", reasoning[:1000], "...")


@then("the reasoning should be grammatically correct")
def validate_reasoning_grammar_step(context):
    reasoning = context.get("parsed_reasoning", "")
    print("\nReasoning for Grammar Check:\n", reasoning[:300], "...")
    validate_reasoning_grammar(reasoning)


@when(parsers.parse('the user sends an AI prompt "{prompt}" with dialect "{dialect}"'))
def send_prompt_with_dialect(context, prompt, dialect):
    url = "https://cc1fbde45ead-in-south-01.backstract.io/sigma/api/v1/ai_generator/generate_initial_crud"
    headers = {"Authorization": f"Bearer {context['auth_token']}"}
    payload = {
        "prompt": prompt,
        "dialect": dialect,
        "workspace_id": context["workspace_id"],
        "collection_id": context["collection_id"],
        "collection_name": context["collection_name"]
    }

    res = requests.post(url, json=payload, headers=headers)
    context["ai_response"] = res.text
    context["status_code"] = res.status_code
    log_api_response("ai_response", res.text)


@when("the user sends an empty AI prompt")
def send_empty_prompt(context):
    return send_prompt_with_dialect(context, "", "SQLite")


@when("the user tries to send an AI prompt with an invalid token")
def send_with_invalid_token(context):
    url = "https://cc1fbde45ead-in-south-01.backstract.io/sigma/api/v1/ai_generator/generate_initial_crud"
    headers = {"Authorization": "Bearer invalid_token"}
    payload = {
        "prompt": "Generate a hotel booking app",
        "dialect": "SQLite",
        "workspace_id": "fake_id",
        "collection_id": "fake_collection",
        "collection_name": "Invalid Collection"
    }

    res = requests.post(url, json=payload, headers=headers)
    context["status_code"] = res.status_code
    context["ai_response"] = res.text


@then("the response should indicate unsupported dialect error")
def check_unsupported_dialect_error(context):
    assert context["status_code"] == 400
    assert "unsupported" in context["ai_response"].lower()


@then("the response should indicate missing input error")
def check_missing_prompt_error(context):
    assert context["status_code"] == 400
    assert "prompt" in context["ai_response"].lower()


@then("the response should indicate unauthorized access")
def check_unauthorized_response(context):
    assert context["status_code"] == 401
    assert "unauthorized" in context["ai_response"].lower()


@then("the schema and reasoning should not be present")
def check_empty_response_structure(context):
    html = context["ai_response"]
    assert "Schema generated successfully." not in html
    assert "<div class='reasoning-output'>" not in html
