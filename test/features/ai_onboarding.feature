Feature: AI Onboarding via APIs

  Scenario: Complete onboarding flow via APIs
    Given a user logs in with valid credentials
    When the user creates a new workspace
    And the user sends an AI prompt to generate CRUD schema
    Then the schema and reasoning should be returned correctly
    And the schema should include users and orders tables
    And the reasoning should be grammatically correct
