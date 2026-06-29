# Story 1.0: Project Setup

## User Story

As a developer, I want the monorepo initialized with the agreed tools and package boundaries so that implementation starts from a clean, scalable foundation.

## Acceptance Criteria

- Root `uv` workspace is defined for backend, agent, and shared Python packages.
- Frontend is initialized with Vite, React, and TypeScript.
- Root commands exist for setup, lint, type-check, tests, and local run.
- Placeholder backend API and frontend app boot locally.
- Tests run without real Grok or DeepSeek credentials.

## Gherkin

```gherkin
Feature: Project setup
  Scenario: Developer boots the empty project
    Given dependencies are installed
    When the developer runs the default checks
    Then backend tests pass
    And frontend checks pass
    And no real LLM provider key is required
```

## Pytest Coverage

- Workspace dependency metadata loads.
- Backend smoke test passes.
- Provider settings default to stub-safe test mode.

