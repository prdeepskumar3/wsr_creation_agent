# Story 2.1: Shared Enums and DTOs

## User Story

As a frontend and backend developer, I want shared request and response contracts so that API payloads are predictable, typed, and documented.

## Acceptance Criteria

- DTOs use Pydantic v2.
- Public API JSON uses camelCase.
- Python DTO fields use snake_case.
- Field descriptions and examples exist for important request fields.
- Delivery model enum exposes only `SPRINT` and `PI` in MVP.
- `ReadyToShareWsrContentSectionsDTO`, `WsrReviewRequestDTO`, and `WsrReviewResponseDTO` are defined.
- `DeliveryModelFieldMetadataDTO` and `DeliveryModelMetadataDTO` are defined.

## Gherkin

```gherkin
Feature: Shared API contracts
  Scenario: Serialize a WSR review request
    Given a valid WSR review DTO
    When it is serialized to JSON
    Then the payload uses camelCase field names
    And contentSections includes ready-to-share WSR schemaVersion
    And PM-only insight fields are not present
```

## Pytest Coverage

- CamelCase serialization test.
- Enum value test for MVP delivery models.
- Ready-to-share WSR content schema validation test.
- WSR review request rejects missing required content sections.
- Delivery model metadata DTO shape test.

