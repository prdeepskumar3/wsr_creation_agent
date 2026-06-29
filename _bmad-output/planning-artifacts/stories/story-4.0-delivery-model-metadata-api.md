# Story 4.0: Delivery Model Metadata API

## User Story

As a frontend developer, I want delivery model field metadata from the backend so that the WSR UI can render Sprint and PI sections from one source of truth.

## Acceptance Criteria

- Metadata API returns Sprint and PI field definitions.
- Each field includes key, label, input type, section, required flag, help text, options, default value, read-only flag, calculated flag, formula key, validation hints, and visibility rules.
- Metadata version is included for frontend cache invalidation.
- Metadata is generated from the delivery model registry, not hard-coded separately in UI code.
- Hidden fields for the non-selected delivery model are not required during validation.

## Gherkin

```gherkin
Feature: Delivery model metadata
  Scenario: Frontend requests Sprint metadata
    Given Sprint is an enabled MVP delivery model
    When the frontend requests delivery model metadata
    Then Sprint setup and progress fields are returned
    And calculated fields include formula keys
    And metadataVersion is present
```

## Pytest Coverage

- Sprint metadata shape test.
- PI metadata shape test.
- Metadata generated from registry test.
- Metadata versioning test.
- Formula-key mapping test for Sprint point completion and effort usage.
- Hidden field validation test.

