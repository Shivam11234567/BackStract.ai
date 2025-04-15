import language_tool_python
from bs4 import BeautifulSoup


def validate_schema_structure(data):
    try:
        nodes = data["nodes"]
        table_names = [n["data"]["label"] for n in nodes]
        return "users" in table_names and "orders" in table_names
    except Exception as e:
        print(f"Validation error: {e}")
        return False

def check_grammar(text):
    tool = language_tool_python.LanguageTool('en-US')
    matches = tool.check(text)
    return len(matches) == 0

"""def validate_schema_structure(ai_response_html: str) -> bool:
    expected_tables = ["students", "teachers", "courses", "departments", "enrollments", "assignments", "grades", "attendance"]
    # Extract the schema text from HTML
    soup = BeautifulSoup(ai_response_html, "html.parser")
    reasoning_block = soup.find("div", class_="reasoning-output")
    if not reasoning_block:
        return False

    code_block = reasoning_block.find("code")
    if not code_block:
        return False

    text = code_block.text.lower()
    return all(table in text for table in expected_tables)"""

