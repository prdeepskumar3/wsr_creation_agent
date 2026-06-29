# Story 1.2: Application Scaffold

## User Story

As a developer, I want backend, agent, shared, and frontend folders scaffolded by responsibility so that code does not grow into large single files.

## Acceptance Criteria

- Backend package follows architecture package layout.
- Agent package contains graph, nodes, chains, prompts, schemas, retrieval, safety, and human review folders.
- Shared package contains common DTO/enums/contracts.
- Frontend follows feature-based layout for WSR creation, generated review, approval, export, and admin.
- Empty modules include clear ownership boundaries.

## Gherkin

```gherkin
Feature: Application scaffold
  Scenario: Developer locates WSR generation graph code
    Given the project scaffold exists
    When the developer opens the agent package
    Then graph topology is under graphs
    And node implementations are under nodes
    And provider-specific code is isolated behind provider adapters
```

## Pytest Coverage

- Package import smoke tests.
- Architecture folder structure snapshot test.
- Agent graph module import test.

