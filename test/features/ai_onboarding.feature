Feature: AI Onboarding Flow

  Scenario: Complete onboarding flow via APIs
    Given a user logs in with valid credentials
    When the user creates a new workspace
    And a preflight request is made to create a collection
    When the user sends an AI prompt "Generate a TO DO app"
    Then the schema and reasoning should be returned correctly
    And the reasoning should be grammatically correct

  Scenario: AI prompt with unsupported dialect
    Given a user logs in with valid credentials
    When the user creates a new workspace
    And a preflight request is made to create a collection
    When the user sends an AI prompt "Build a POS system" with dialect "UnknownDB"
    Then the response should indicate unsupported dialect error

  Scenario: Missing prompt input
    Given a user logs in with valid credentials
    When the user creates a new workspace
    And a preflight request is made to create a collection
    When the user sends an empty AI prompt
    Then the response should indicate missing input error

  Scenario: Invalid auth token
    Given a user logs in with valid credentials
    When the user tries to send an AI prompt with an invalid token
    Then the response should indicate unauthorized access

  Scenario: AI response missing schema or reasoning
    Given a user logs in with valid credentials
    When the user creates a new workspace
    And a preflight request is made to create a collection
    When the user sends an AI prompt "Give me nothing"
    Then the schema and reasoning should not be present
