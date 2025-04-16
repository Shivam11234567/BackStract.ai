from bs4 import BeautifulSoup


def validate_response_status(response):
    """Ensure API response is 200 OK."""
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"


def validate_html_response(html):
    """Validate that HTML contains both schema and reasoning blocks."""
    assert isinstance(html, str), "Expected AI response as HTML string"

    soup = BeautifulSoup(html, "html.parser")

    # Look for the message with a substring match
    assert soup.find(string=lambda text: text and "Schema generated successfully." in text), \
        "Schema success message not found in HTML response."

    # Check if reasoning block is present
    reasoning_block = soup.select_one("div.reasoning-output code")
    assert reasoning_block, "Reasoning block not found in HTML response."



def extract_reasoning_block(html):
    """Extract reasoning text from raw HTML string."""
    soup = BeautifulSoup(html, "html.parser")
    code_block = soup.select_one("div.reasoning-output code")
    return code_block.get_text(strip=True) if code_block else ""


def validate_reasoning_grammar(reasoning_text):
    """Check if reasoning text contains basic grammatical structure."""
    assert len(reasoning_text) > 50, "Reasoning text is too short"

    intro_phrases = [
        "This application", "This database", "The application", "The schema", "In this design"
    ]
    assert any(phrase in reasoning_text for phrase in intro_phrases), \
        "Reasoning lacks a proper grammatical introduction"
