import pytest
import requests
from pytest_bdd import scenarios, given, when, then
from bs4 import BeautifulSoup

scenarios("../features/ai_onboarding.feature")


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

    print("Login API URL:", login_url)
    print("Login Payload:", payload)
    print("Login Response:", res.status_code, res.json())

    assert res.status_code == 200
    token = res.json()["value"]
    context["auth_token"] = token
    return context


@when("the user creates a new workspace")
def create_workspace(context):
    workspace_url = "https://cc1fbde45ead-in-south-01.backstract.io/sigma/api/v1/workspace/create"
    headers = {"Authorization": f"Bearer {context['auth_token']}"}
    payload = {"workspace_name": "Students WorkSpace 17"}

    res = requests.post(workspace_url, json=payload, headers=headers)

    print("Workspace API URL:", workspace_url)
    print("Workspace Payload:", payload)
    print("Workspace Headers:", headers)
    print("Workspace Response:", res.status_code, res.json())

    assert res.status_code == 200
    context["workspace_id"] = res.json()["value"]["workspace_id"]
    return context


@when("the user sends an AI prompt to generate CRUD schema")
def send_ai_prompt(context):
    prompt_url = "https://cc1fbde45ead-in-south-01.backstract.io/sigma/api/v1/ai_generator/generate_initial_crud"
    headers = {"Authorization": f"Bearer {context['auth_token']}"}
    payload = {
        "prompt": "Create a Student Management System with students, courses, and enrollment tables.",
        "dialect": "SQLite",
        "workspace_id": context["workspace_id"]
    }

    res = requests.post(prompt_url, json=payload, headers=headers)

    print("AI Prompt URL:", prompt_url)
    print("AI Prompt Payload:", payload)
    print("AI Prompt Headers:", headers)
    print("AI Prompt Response:", res.status_code, res.text)

    assert res.status_code == 200

    try:
        context["ai_response"] = res.json()
    except requests.exceptions.JSONDecodeError:
        context["ai_response"] = res.text  # fallback to raw HTML

    return context


@then("the schema and reasoning should be returned correctly")
def check_ai_response_structure(context):
    html = context["ai_response"]
    assert isinstance(html, str), "Expected HTML string as AI response"

    soup = BeautifulSoup(html, "html.parser")

    assert soup.find(string="Schema generated successfully."), "Schema generation success message not found"

    reasoning_code = soup.select_one("div.reasoning-output code")
    assert reasoning_code, "Reasoning block not found"

    reasoning_text = reasoning_code.get_text(strip=True)
    assert len(reasoning_text) > 100, "Reasoning text seems too short"
    assert "students" in reasoning_text.lower(), "Reasoning does not mention students"

    context["parsed_reasoning"] = reasoning_text
    print("Extracted Reasoning (first 200 chars):", reasoning_text[:200], "...")


@then("the schema should include users and orders tables")
def validate_tables(context):
    html = context["ai_response"]
    soup = BeautifulSoup(html, "html.parser")

    reasoning_code = soup.select_one("div.reasoning-output code")
    assert reasoning_code, "Reasoning block not found"

    reasoning_text = reasoning_code.get_text(strip=True).lower()

    expected_keywords = ["students", "courses", "enrollments"]
    for keyword in expected_keywords:
        assert keyword in reasoning_text, f"Expected table '{keyword}' not found in reasoning."

    print("All expected tables found in reasoning.")


@then("the reasoning should be grammatically correct")
def validate_reasoning_grammar(context):
    html = context["ai_response"]
    soup = BeautifulSoup(html, "html.parser")

    code_block = soup.select_one("div.reasoning-output code")
    reasoning = code_block.get_text(strip=True) if code_block else ""

    print("Grammar Reasoning Check (first 100 chars):", reasoning[:100], "...")
    assert reasoning != "", "No reasoning found in response"
    assert "This database design" in reasoning, "Unexpected grammar or missing intro in reasoning"
