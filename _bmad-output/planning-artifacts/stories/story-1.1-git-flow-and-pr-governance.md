# Story 1.1: Git Flow and PR Governance

## User Story

As a delivery team, I want Git Flow, branch naming, PR templates, and review gates documented so that changes are traceable and reviewable.

## Acceptance Criteria

- `main` and `develop` branch policy is documented.
- Feature branches use story-scoped naming.
- PR template asks for story link, test evidence, screenshots for UI changes, migration notes, risk, and rollback notes.
- CODEOWNERS and branch protection expectations are documented.

## Gherkin

```gherkin
Feature: PR governance
  Scenario: Developer opens a story PR
    Given a story-scoped feature branch exists
    When the PR is opened
    Then the PR template asks for story link
    And test evidence is required
    And UI screenshots are requested when applicable
```

## Pytest Coverage

- Repository policy files exist.
- PR template contains required sections.
- Branch naming policy is documented.

