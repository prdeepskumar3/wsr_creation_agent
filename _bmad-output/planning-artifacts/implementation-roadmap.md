---
date: "2026-06-27"
project: "wsr_creation_agent"
sourceDocuments:
  - "_bmad-output/planning-artifacts/prd.md"
  - "_bmad-output/planning-artifacts/architecture.md"
  - "_bmad-output/planning-artifacts/ux-design-specification.md"
  - "_bmad-output/planning-artifacts/wsr-ui-prototype.html"
status: "Draft"
---

# WSR Creation Agent Implementation Roadmap

## Roadmap Principles

- Build from contracts outward: shared DTOs, database schema, API contract, frontend model schema, then agent workflows.
- Keep modules small and named by business responsibility.
- Use LangChain and LangGraph 1.x built-ins before custom agent glue code.
- Treat PM-approved customer-facing content as the export source of truth.
- Preserve account + project isolation in every API, query, workflow run, and retrieval call.

## Phase 0: Decisions Locked

Outcome: no hidden product or architecture choices remain before coding.

Deliverables:
- Confirm MVP delivery models: Sprint and PI only.
- Confirm Grok and DeepSeek provider policy, default primary/fallback order, and secret storage approach.
- Confirm immutable approved-content versioning.
- Confirm PostgreSQL + Redis + Celery deployment baseline.
- Confirm export template ownership and customer-safe field policy.

Exit criteria:
- PRD, architecture, and UX docs agree on MVP scope.
- No implementation-blocking open question remains for schema, workflow, approval, export, or provider selection.

## Phase 1: Repository Foundation

Outcome: project structure prevents single-file growth from day one.

Deliverables:
- Initialize repository in the target Git remote and configure Git Flow branches.
- Initialize Python workspace with `uv`.
- Add backend, agent, and shared Python dependencies through `uv add`.
- Initialize frontend app with Vite + React + TypeScript.
- Install frontend runtime and development libraries.
- Add root developer commands for setup, lint, type-check, test, and local run.
- Add PR template, issue/story template, CODEOWNERS, branch protection expectations, and CI quality gates.
- Create monorepo folders: `frontend`, `backend`, `agent`, `shared`, `infra`, `docs`.
- Add Python backend package layout from architecture.
- Add React feature-based frontend layout from architecture.
- Add agent package layout with `graphs`, `nodes`, `chains`, `prompts`, `state`, `tools`, and `contracts`.
- Add linting, formatting, type checking, and test commands.

Exit criteria:
- `main` and `develop` branches exist with direct pushes disabled.
- Feature work happens through PRs from story-scoped branches.
- `uv sync` installs Python dependencies successfully.
- Frontend package install succeeds.
- Empty backend API and frontend app boot locally.
- Pytest, lint, type-check, and frontend test placeholders run without real provider credentials.

## Phase 2: Shared Contracts and Database

Outcome: frontend, API, persistence, and agent speak the same language.

Deliverables:
- Define enums for `DeliveryModel`, `RagStatus`, `RiskStatus`, lifecycle status, generation status, WSR review decisions, and approval decisions.
- Define Pydantic DTOs with clear `Field` descriptions, examples, and type hints.
- Add SQLAlchemy models and Alembic migrations for all core tables.
- Implement UUID primary keys and database foreign keys.
- Implement `wsr_content_versions` as the approved/export source.
- Implement `workflow_runs` and checkpointer strategy.

Exit criteria:
- Migration creates schema successfully.
- Contract tests verify camelCase API JSON and snake_case Python/database mapping.
- Database constraints cover account/project isolation and content version uniqueness.

## Phase 3: Auth, Account, Project, and Admin Settings

Outcome: users can access only authorized account/project context and admins can configure runtime policy.

Deliverables:
- Implement enterprise login, logout, and session lifecycle.
- Implement auth adapter interface and local development auth.
- Implement account/project lookup APIs.
- Implement project assignment authorization service.
- Implement admin settings APIs for LLM providers, retention, and integrations.
- Add audit logging for admin setting changes.

Exit criteria:
- Unauthorized account/project access is rejected.
- Admin settings never return provider secrets.
- Provider configuration can be read by backend and agent startup/runtime code.

## Phase 4: WSR Draft Creation and Delivery Model Registry

Outcome: PM-entered UI data persists cleanly and calculations are server-authoritative.

Deliverables:
- Implement WSR create, get, patch, save-draft, prefill, and validate APIs.
- Implement delivery model metadata API for Sprint and PI UI schemas.
- Implement Sprint and PI model definitions in one registry.
- Implement server calculations for Sprint and PI.
- Implement validation services for required fields, narrative requirements, cross-field rules, RAG justification, and risk lifecycle rules.
- Persist complete UI snapshots and normalized risk rows.

Exit criteria:
- Saved draft restores the full form.
- Validate returns field-level errors.
- Sprint and PI calculations match documented formulas.

## Phase 5: Production WSR UI

Outcome: PM can fill a polished WSR form without confusion.

Deliverables:
- Build React shell, routing, layout, and design primitives.
- Build account/project, delivery model, Sprint setup, PI setup, progress, RAG, risk/dependency, notes, and action sections.
- Make delivery-model sections data-driven.
- Add risk row add/remove with validation.
- Add local mirrored calculations for immediate feedback, while displaying server validation results.

Exit criteria:
- UI aligns with the approved prototype but uses reusable components.
- Switching Sprint/PI changes only model-specific sections.
- No layout overflow or broken alignment on desktop and mobile breakpoints.

## Phase 6: Agentic Generation Foundation

Outcome: LangGraph can generate resumable PM-only insights and customer-ready draft content.

Deliverables:
- Implement `WeeklyStatusReportGenerationState`.
- Implement graph nodes and named edges from architecture.
- Implement account + project approved-history retrieval.
- Implement LangChain provider adapters for Grok and DeepSeek.
- Implement deterministic insight signal rules for discrepancy, risk, narrative quality, actionability, and customer-safety issues.
- Implement structured output contracts for insights, draft sections, and quality review.
- Implement Celery generation worker and status polling.

Exit criteria:
- Generation starts only after persisted validation success.
- Graph state is checkpointed by `workflow_run_id`.
- Provider fallback works for retryable provider failures.
- PM-only insights are never mixed into exportable content.

## Phase 7: Human-in-the-Loop Review

Outcome: PM can review collapsible AI insights and edit the ready-to-share WSR preview while the graph remains stateful.

Deliverables:
- Implement WSR preview review resume API.
- Persist edited ready-to-share WSR preview content before graph resume; AI insights remain collapsible read-only guidance.
- Create generated `wsr_content_versions` from edited WSR preview content.
- Add UI states for waiting, resumed, failed, and completed generation.

Exit criteria:
- Stale run IDs are rejected.
- Repeated resume calls with the same idempotency key do not duplicate records.
- Every HITL decision is audit-visible.

## Phase 8: Approval, Export, and Dashboard

Outcome: approved customer-facing WSRs can be exported and tracked.

Deliverables:
- Implement submit-review, approve, approve-with-edits, and reject state transitions.
- Enforce immutable approved content versions.
- Implement PPTX export from approved `wsr_content_versions`.
- Implement export status polling and object storage.
- Implement executive dashboard APIs for latest approved WSR, delivery health, risk severity, and export status.

Exit criteria:
- Export is impossible before approval.
- Export never reads PM-only insights or stale AI drafts.
- Editing approved content creates a new version and requires re-approval.

## Phase 9: Observability, Security, and Retention

Outcome: the system is operable in enterprise conditions.

Deliverables:
- Add correlation IDs across API, Celery, LangGraph, LLM calls, repositories, and export.
- Add structured logs, metrics, and traces.
- Add retention jobs for drafts, checkpoints, exports, and generated artifacts.
- Add prompt-injection redaction and secret-safe logging checks.
- Add audit log coverage for draft edits, generation, HITL, approval, rejection, export, and admin settings.
- Add PMO audit-history review and admin operational health monitoring.

Exit criteria:
- A production incident can be traced by correlation ID.
- Retention policy can be configured and executed safely.
- Security tests cover account/project isolation and customer-safe export filtering.

## Phase 10: Release Readiness

Outcome: implementation is ready for controlled rollout.

Deliverables:
- Add Playwright E2E flows for Sprint, PI, generation, approval, export, and rejection.
- Add API contract tests and repository integration tests.
- Add LangGraph node tests with deterministic provider stubs.
- Add performance smoke/load tests for dashboard, risk table, save, validate, generate status, and export.
- Add deployment manifests and environment documentation.
- Validate release branch, semantic version tag, PR approvals, release notes, and rollback notes before merging to `main`.

Exit criteria:
- Implementation readiness check passes.
- Required PR checks and approvals are green for the release PR.
- Critical and high defects are closed.
- Pilot deployment runbook exists.

## First Implementation Slice

Start with this thin vertical slice:

1. Initialize the Python workspace with `uv`, add required backend/agent/shared dependencies, and commit `pyproject.toml` plus lockfile.
2. Initialize the React + TypeScript frontend with Vite and install required UI/runtime/test libraries.
3. Create `main` and `develop`, configure Git Flow documentation, PR template, issue/story template, CODEOWNERS, and initial CI workflow.
4. Scaffold project folders and test tooling.
5. Create shared enums, DTOs, database models, and migrations.
6. Implement auth stub, account/project APIs, and authorization service.
7. Implement delivery model metadata API.
8. Implement WSR draft save/restore and prefill for Sprint only.
9. Add Sprint calculations, narrative validation, and risk lifecycle validation.
10. Build the production UI shell and Sprint form sections.
11. Add PI after the Sprint path is stable.

This sequence gives quick visible progress while keeping the domain contracts clean enough for the agent and export phases.

## Testing Standard

Use Pytest for backend, agent, shared-contract, service, repository, and domain unit tests.

Minimum Python test expectations:
- Unit tests live beside the owning Python package under `tests/unit`.
- Service orchestration tests use repository fakes rather than a real database unless the story explicitly requires integration coverage.
- Repository and migration behavior is tested under `tests/integration`.
- Agent node tests use deterministic model stubs and fixed structured outputs.
- API tests use FastAPI test client or HTTPX async client with dependency overrides.
- Every story that changes Python behavior includes Pytest coverage for the happy path, validation failure, authorization failure where relevant, and one edge case.
- Domain rule and validation modules target at least 90% Pytest coverage to match PRD rules coverage goals.
- CI must fail when backend or agent unit tests cannot run without real Grok or DeepSeek credentials.

Frontend component tests may use Vitest and Testing Library, but backend and agent correctness must be covered with Pytest.

## Git Flow and PR Governance

Use Git Flow with protected long-lived branches and short-lived story branches.

Branch model:
- `main`: production-ready code only. Merges come from release or hotfix PRs. Direct push is disabled.
- `develop`: integration branch for completed stories. Feature branches merge here through PR only. Direct push is disabled.
- `feature/{story-id}-{short-name}`: normal story work, for example `feature/4-2-validate-sprint-pi-metrics`.
- `bugfix/{ticket-id}-{short-name}`: non-production bug fixes targeting `develop`.
- `release/{version}`: release stabilization branch cut from `develop`, for example `release/0.1.0`.
- `hotfix/{version}-{short-name}`: urgent production fix branch cut from `main`, merged back to both `main` and `develop`.

Commit and PR rules:
- Use Conventional Commits: `feat:`, `fix:`, `test:`, `docs:`, `refactor:`, `chore:`, `ci:`.
- One PR should map to one story or one tightly scoped technical task.
- PR title includes story ID when applicable, for example `feat(4.2): validate Sprint and PI metrics`.
- PR description includes context, changes, tests run, screenshots for UI changes, migration notes, and risk/rollback notes.
- PR must link the story or issue it implements.
- No generated secrets, `.env` files with real values, local caches, build artifacts, or notebook scratch files are committed.

Review rules:
- At least one peer approval is required for normal PRs.
- Two approvals are required for database migrations, auth/security changes, approval/export logic, LangGraph workflow changes, provider/secret handling, and production deployment changes.
- CODEOWNERS approval is required for owned areas such as frontend, backend, agent, infra, and docs.
- PR author cannot merge their own PR without required approvals.
- Reviewers check acceptance criteria, Gherkin scenarios, Pytest coverage, architecture boundaries, naming clarity, and security impact.

Required PR checks:
- Python formatting/linting.
- Python type checking.
- Pytest unit and integration tests.
- Frontend lint/type-check/tests.
- OpenAPI/schema compatibility check when API contracts change.
- Migration smoke test when Alembic migrations change.
- Secret scan.
- Build check for frontend and backend containers or packages once containerization exists.

Merge and release rules:
- Squash merge feature branches into `develop` unless preserving commits is explicitly useful.
- Release branches accept only bug fixes, release notes, version changes, and deployment configuration fixes.
- `main` is tagged for every release using semantic versioning.
- Hotfixes are merged into `main`, tagged, and then merged or cherry-picked back into `develop`.
- Release notes list completed stories, migrations, operational changes, known issues, and rollback guidance.

## Requirements Traceability Matrix

| PRD Area | Requirement IDs | Roadmap Stories |
|---|---|---|
| Authentication and authorization | `FR-AUTH-001` through `FR-AUTH-003`, `FR-ACC-001`, `FR-ACC-002`, `NFR-SEC-001`, `NFR-SEC-002` | 3.0, 3.1, 8.4 |
| Delivery model selection and calculations | `FR-MOD-001` through `FR-MOD-003` | 2.1, 4.0, 4.2, 5.2 |
| WSR draft data entry | `FR-WSR-001` through `FR-WSR-005` | 4.1, 4.5, 5.1 |
| Prefill and historical retrieval | `FR-PRE-001`, `FR-PRE-002` | 4.4, 6.2 |
| Risk and dependency governance | `FR-RSK-001` through `FR-RSK-007`, `NFR-COMP-004` | 4.3, 4.6, 8.4 |
| Validation and discrepancy rules | `FR-VAL-001` through `FR-VAL-003` | 4.2, 4.5, 4.6, 6.4 |
| AI generation and PM insights | `FR-AIG-001` through `FR-AIG-003`, `FR-AIS-001` through `FR-AIS-007`, `NFR-REL-002`, `NFR-REL-004` | 6.1, 6.2, 6.3, 6.4, 7.1, 7.2 |
| Review, approval, and immutable content | `FR-APR-001` through `FR-APR-003`, `NFR-COMP-001` | 7.2, 7.3, 8.1, 8.2 |
| Customer-safe export | `FR-EXP-001`, `FR-EXP-002`, `NFR-REL-003`, `NFR-COMP-002`, `NFR-COMP-003` | 8.3 |
| Executive dashboard | `FR-DASH-001`, `FR-DASH-002` | 8.4 |
| Audit and PMO review | `FR-AUD-001`, `FR-AUD-002`, `NFR-OBS-001`, `NFR-OBS-002` | 9.1, 9.3 |
| Platform administration | `FR-ADM-001` through `FR-ADM-003`, `NFR-SEC-003`, `NFR-DATA-002`, `NFR-DATA-003` | 3.2, 9.2, 9.4 |
| Performance and operability | Performance targets, `NFR-REL-001`, `NFR-OBS-003` | 9.1, 9.4, 10.4 |
| Delivery governance | Git Flow, PR review, branch protection, CI quality gates | 1.1, 10.1, 10.2, 10.3 |

## Phase Story Map

### Phase 0 Stories: Decisions Locked

#### Story 0.1: Confirm MVP Scope and Technical Baseline

As a product owner, I want MVP decisions recorded in one implementation baseline so that developers do not make conflicting assumptions during build.

Acceptance criteria:
- MVP delivery models are documented as Sprint and PI only.
- Grok and DeepSeek provider policy is documented.
- PostgreSQL, Redis, Celery, FastAPI, React, LangChain 1.x, and LangGraph 1.x are confirmed.
- Approved WSR content versioning is documented as immutable.

Gherkin:

```gherkin
Feature: MVP implementation baseline
  Scenario: Developer reads the baseline before implementation
    Given the implementation roadmap exists
    When a developer reviews Phase 0
    Then Sprint and PI are listed as the only MVP delivery models
    And Grok and DeepSeek are listed as required LLM providers
    And approved content is described as immutable after approval
```

Pytest coverage:
- No product code required.
- Add a lightweight documentation guard later if docs are parsed in CI.

### Phase 1 Stories: Repository Foundation

#### Story 1.0: Initialize Project Tooling and Dependencies

As a developer, I want the project initialized with repeatable package management and install commands so that every contributor can create the same local environment.

Acceptance criteria:
- Root Python workspace is initialized with `uv`.
- Backend, agent, and shared Python packages are installable through `uv sync`.
- Runtime dependencies are added with `uv add`, and development dependencies are added with `uv add --dev`.
- Frontend is initialized with Vite, React, and TypeScript.
- Frontend libraries are installed for routing, server state, forms, validation, tables, icons, and tests.
- `.env.example` files document required environment variables without real secrets.
- Setup commands are documented in `README.md` or `docs/development-setup.md`.

Required Python setup commands:

```bash
uv init --package
uv add fastapi uvicorn pydantic pydantic-settings sqlalchemy alembic asyncpg "psycopg[binary]" redis celery python-pptx boto3 structlog opentelemetry-api opentelemetry-sdk httpx tenacity orjson email-validator python-multipart openai
uv add "langchain>=1.0,<2.0" "langgraph>=1.0,<2.0" langgraph-checkpoint-postgres
uv add --dev pytest pytest-asyncio pytest-cov ruff mypy httpx factory-boy freezegun
uv lock
```

Dependency ownership rules:
- Backend, agent, and shared packages belong to the root `uv` workspace defined in the root `pyproject.toml`.
- Package-specific source and tests stay under `backend`, `agent`, and `shared`; dependency resolution and locking happen through the root workspace.
- Agent runtime dependencies must include LangChain/LangGraph 1.x pins.
- Provider-specific LangChain packages for Grok/xAI and DeepSeek must be verified against the pinned LangChain 1.x documentation before adding; do not install unverified package names.
- Secrets are never stored in dependency files, `.env.example`, test fixtures, or setup scripts.

Required frontend setup commands:

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install @tanstack/react-query @tanstack/react-router react-hook-form zod @hookform/resolvers @tanstack/react-table zustand lucide-react
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event playwright eslint prettier typescript
```

Gherkin:

```gherkin
Feature: Repeatable project setup
  Scenario: Developer installs project dependencies
    Given the repository has setup files
    When the developer runs uv sync
    And the developer installs frontend dependencies
    Then backend, agent, shared, and frontend dependencies are installed
    And no real Grok or DeepSeek credentials are required
```

Pytest coverage:
- `test_dependency_metadata.py` verifies required Python packages are declared.
- `test_environment_examples.py` verifies `.env.example` files do not contain real secrets.
- `test_settings_load_without_provider_keys.py` verifies test settings load with stub providers.

#### Story 1.1: Configure Git Flow, PR Templates, and Branch Protection

As a technical lead, I want the repository configured with Git Flow and PR governance so that every change is reviewable, testable, and traceable to a story.

Acceptance criteria:
- Remote repository has protected `main` and `develop` branches.
- Direct pushes to `main` and `develop` are disabled.
- Branch naming conventions are documented for `feature`, `bugfix`, `release`, and `hotfix`.
- PR template captures story link, summary, acceptance criteria, tests run, screenshots for UI, migration impact, security impact, and rollback notes.
- Issue/story template captures user story, Gherkin scenarios, acceptance criteria, and Pytest expectations.
- CODEOWNERS defines review ownership for frontend, backend, agent, shared contracts, infra, docs, and migrations.
- Required PR checks are documented and wired into CI as soon as CI exists.

Recommended initial repository files:

```text
.github/
  pull_request_template.md
  ISSUE_TEMPLATE/
    story.md
    bug_report.md
  CODEOWNERS
  workflows/
    ci.yml
docs/
  git-flow.md
```

Gherkin:

```gherkin
Feature: Git Flow repository governance
  Scenario: Developer opens a story PR
    Given the developer creates a feature branch from develop
    When the developer opens a pull request
    Then the PR template asks for story link, tests, risks, and rollback notes
    And required checks must pass before merge
    And at least one reviewer approval is required
```

Pytest coverage:
- No product behavior required.
- Repository governance can be checked later with CI policy checks for required files.

#### Story 1.2: Scaffold Modular Monorepo

As a developer, I want a clear project folder structure so that frontend, backend, agent, shared contracts, and infrastructure code do not grow into large mixed files.

Acceptance criteria:
- Root folders exist: `frontend`, `backend`, `agent`, `shared`, `infra`, and `docs`.
- Backend package separates API, services, domain, repositories, models, workers, integrations, and observability.
- Agent package separates graphs, nodes, chains, prompts, state, providers, and contracts.
- Public Python modules include class/function docstring rules in project guidance.

Gherkin:

```gherkin
Feature: Modular repository structure
  Scenario: Developer creates a new backend service
    Given the repository scaffold exists
    When the developer adds a WSR application service
    Then the service belongs under backend services
    And SQLAlchemy models remain under backend models
    And LangGraph nodes remain under the agent package
```

Pytest coverage:
- `test_project_structure.py` asserts required directories exist.
- `test_python_packages_import.py` imports backend, agent, and shared package roots.

#### Story 1.3: Add Tooling and Test Commands

As a developer, I want standard lint, type-check, and test commands so that code quality is enforced consistently.

Acceptance criteria:
- Backend and agent support `pytest`.
- Python formatting and linting commands are documented.
- Test folders exist for unit, integration, and contract tests.
- CI placeholder can run without application secrets.

Gherkin:

```gherkin
Feature: Developer quality commands
  Scenario: Developer runs unit tests locally
    Given the repository scaffold exists
    When the developer runs the backend Pytest command
    Then unit tests execute without requiring real LLM provider credentials
```

Pytest coverage:
- Smoke test verifies test configuration loads.
- Smoke test verifies environment defaults do not require real Grok or DeepSeek keys.

### Phase 2 Stories: Shared Contracts and Database

#### Story 2.1: Define Shared Enums and DTOs

As a frontend and backend developer, I want shared request and response contracts so that API payloads are predictable and documented.

Acceptance criteria:
- DTOs use Pydantic v2.
- Public API JSON uses camelCase.
- Python DTO fields use snake_case.
- Field descriptions and examples exist for important request fields.
- Delivery model enum exposes only `SPRINT` and `PI` in MVP.

Gherkin:

```gherkin
Feature: Shared API contracts
  Scenario: Serialize a WSR draft request
    Given a valid Python WSR draft DTO
    When it is serialized for API response
    Then JSON field names are camelCase
    And unknown fields are rejected
    And deliveryModel accepts SPRINT or PI only
```

Pytest coverage:
- `test_dto_camel_case_serialization`.
- `test_dto_rejects_unknown_fields`.
- `test_delivery_model_rejects_non_mvp_values`.

#### Story 2.2: Create Database Schema With UUID Keys

As a backend developer, I want normalized database tables with UUID primary and foreign keys so that account/project isolation and lifecycle history are enforceable.

Acceptance criteria:
- Core tables from architecture are represented in SQLAlchemy models.
- Alembic migration creates UUID primary keys and foreign keys.
- `wsr_content_versions` exists and is linked to approval and export events.
- `workflow_runs` and checkpoint persistence strategy exist.
- Approved/exported history uses restrictive delete behavior.

Gherkin:

```gherkin
Feature: WSR database schema
  Scenario: Create schema for WSR content approval
    Given the database migration has run
    When a WSR content version is approved
    Then approval_events references the content version by UUID
    And export_attempts can reference the same approved content version
```

Pytest coverage:
- Migration smoke test creates all tables.
- Model relationship test verifies foreign keys.
- Constraint test prevents duplicate `wsr_content_versions` for the same report/version number.

### Phase 3 Stories: Auth, Account, Project, and Admin Settings

#### Story 3.0: Implement Enterprise Session Lifecycle

As a user, I want to log in, maintain an authorized session, and log out so that access to WSR data is controlled by enterprise identity.

Acceptance criteria:
- Login accepts the configured enterprise or portal identity provider.
- Logout ends the active application session.
- Expired or invalid sessions cannot call protected APIs.
- Session errors return a controlled API error with correlation ID.

Gherkin:

```gherkin
Feature: Enterprise session lifecycle
  Scenario: User logs out
    Given the user has an active authenticated session
    When the user logs out
    Then the active session is ended
    And protected API calls require a new login
```

Pytest coverage:
- Login callback/session creation test using auth adapter fake.
- Logout invalidates session test.
- Expired session protected-route rejection test.
- Error envelope includes correlation ID test.

#### Story 3.1: Enforce Account and Project Authorization

As a PM, I want to see only my assigned accounts and projects so that customer data remains isolated.

Acceptance criteria:
- Account list contains only accounts mapped to the user.
- Project list contains only projects mapped to the selected account and user.
- Protected API routes enforce server-side authorization.
- Unauthorized access returns a controlled error with correlation ID.

Gherkin:

```gherkin
Feature: Account and project authorization
  Scenario: PM requests an unmapped project
    Given the PM is assigned to Account A Project 1
    When the PM requests Account B Project 2
    Then the API rejects the request
    And no project data is returned
```

Pytest coverage:
- Authorized account/project list test.
- Unauthorized project access test.
- Route-level dependency override test for protected API authorization.

#### Story 3.2: Configure LLM Provider and Retention Settings

As a platform admin, I want to configure Grok, DeepSeek, retention, and integration settings so that runtime policy can change without code changes.

Acceptance criteria:
- Admin can read and update LLM provider policy.
- Provider secrets are never returned in API responses.
- Admin can configure retention settings for drafts, checkpoints, exports, insights, and audit records.
- Admin setting changes are audited.

Gherkin:

```gherkin
Feature: Admin runtime settings
  Scenario: Admin updates fallback LLM provider
    Given the admin is authorized
    When the admin sets Grok as primary and DeepSeek as fallback
    Then the setting is saved
    And the response hides provider API secrets
    And an audit event is recorded
```

Pytest coverage:
- Admin authorization test.
- Secret redaction test.
- Audit event creation test.
- Invalid provider policy validation test.

### Phase 4 Stories: WSR Draft Creation and Delivery Model Registry

#### Story 4.0: Expose Delivery Model Metadata API

As a frontend developer, I want delivery model field metadata from the backend so that the WSR UI can render Sprint and PI sections from one source of truth.

Acceptance criteria:
- Metadata API returns Sprint and PI field definitions, labels, required flags, help text, validation hints, and calculated field definitions.
- Metadata API returns field key, input type, section, options, default value, read-only flag, calculated flag, formula key, visibility rules, and metadata version.
- Metadata is generated from the delivery model registry, not hard-coded separately in UI code.
- Hidden fields for the non-selected delivery model are not required during validation.
- Metadata version is included so frontend caches can be invalidated safely.

Gherkin:

```gherkin
Feature: Delivery model metadata
  Scenario: Frontend requests PI metadata
    Given PI is an enabled MVP delivery model
    When the frontend requests delivery model metadata
    Then PI setup and progress fields are returned
    And Sprint-only fields are not marked required for PI validation
```

Pytest coverage:
- Sprint metadata shape test.
- PI metadata shape test.
- Metadata generated from registry test.
- Metadata versioning test.
- Formula-key mapping test for Sprint point completion and effort usage.
- Hidden field validation test.

#### Story 4.1: Save and Restore WSR Draft

As a PM, I want to save my WSR draft so that I can return later without losing entered data.

Acceptance criteria:
- Draft stores account, project, reporting week, prepared by, delivery model, snapshots, calculated metrics, and risk rows.
- Draft restore returns the full form state needed by the UI.
- Draft save does not start LangGraph generation.
- Server recalculates derived metrics before persistence.

Gherkin:

```gherkin
Feature: Save WSR draft
  Scenario: PM saves a Sprint WSR draft
    Given the PM entered Sprint setup, progress, RAG, risks, and notes
    When the PM saves the draft
    Then the API persists the full draft state
    And the returned draft can restore the same form
    And generationStatus remains NOT_STARTED
```

Pytest coverage:
- Draft save happy path.
- Draft restore snapshot equivalence.
- Draft save does not enqueue generation.
- Invalid account/project authorization failure.

#### Story 4.2: Validate Sprint and PI Delivery Metrics

As a PM, I want the system to validate delivery-model-specific fields so that generated WSR content is based on reliable data.

Acceptance criteria:
- Sprint validation checks required sprint setup and progress fields.
- PI validation checks PI setup, current sprint, total sprints, planned points, completed points, and required velocity.
- RAG status requires remarks when metrics and selected status conflict.
- Validation returns field-level errors.

Gherkin:

```gherkin
Feature: Delivery model validation
  Scenario: PI current sprint exceeds total sprints
    Given a PI-based WSR draft
    And currentSprint is greater than totalSprints
    When the PM validates the draft
    Then validation fails
    And the error points to currentSprint
```

Pytest coverage:
- Sprint story-count completion calculation test.
- Sprint point completion calculation test.
- Sprint effort usage calculation test.
- PI calculation tests.
- Cross-field validation tests.
- Field-level error mapping tests.

#### Story 4.3: Manage Risk Rows Inside WSR Creation

As a PM, I want to add, edit, and carry forward risks while preparing the WSR so that risks are visible in the report without becoming a separate risk tracker.

Acceptance criteria:
- PM can add and remove risk rows.
- Active risks require owner/contact, mitigation, severity, status, and planned closure date.
- Closed risks require closure remarks.
- Duplicate active risk descriptions are blocked for the same project.
- Previous active risks can be loaded from latest approved WSR for the same account and project.

Gherkin:

```gherkin
Feature: WSR risk rows
  Scenario: PM closes a risk without closure remark
    Given a WSR risk row is marked Closed
    When the PM validates the WSR
    Then validation fails
    And closureRemark is required
```

Pytest coverage:
- Active risk required field tests.
- Closed risk closure remark test.
- Duplicate active risk test.
- Carry-forward risk query scoped by account and project.

#### Story 4.4: Prefill WSR From Latest Approved Report

As a PM, I want reusable data prefilled from the latest approved WSR for the same account and project so that weekly report creation is faster.

Acceptance criteria:
- Prefill uses only the latest approved WSR for the same account ID and project ID.
- Prefill can populate reusable fields, active carry-forward risks, prior PI completed points, and previous customer-facing context.
- Prefill does not copy PM-only insight content, rejected drafts, or internal discrepancy evidence into customer-facing content.
- Prefilled values remain editable unless the field is explicitly read-only context.

Gherkin:

```gherkin
Feature: Latest approved WSR prefill
  Scenario: PM starts a new WSR for an existing project
    Given an approved WSR exists for the same account and project
    When the PM requests prefill
    Then reusable fields are returned
    And PM-only insight content is excluded
```

Pytest coverage:
- Latest approved report selection test.
- Account/project scope isolation test.
- PM-only insight exclusion test.
- No approved history returns empty prefill test.

#### Story 4.5: Validate Project Overview, Achievements, and Plans

As a PM, I want the product to validate narrative fields so that the WSR has enough business context before AI generation.

Acceptance criteria:
- Project overview fields for reporting week, prepared by, and progress update are required.
- At least three achievements are required before generation.
- At least three next-week plan items are required before generation.
- Plan items support owner and target timing when available.
- Validation returns field-level errors for missing or weak narrative data.

Gherkin:

```gherkin
Feature: WSR narrative validation
  Scenario: PM submits too few achievements
    Given the WSR draft has two achievements
    When the PM validates the draft
    Then validation fails
    And the achievements field explains that at least three items are required
```

Pytest coverage:
- Required project overview test.
- Minimum achievements test.
- Minimum next-week plan items test.
- Field-level narrative error mapping test.

#### Story 4.6: Enforce Risk Lifecycle Rules

As a PM, I want risk status transitions governed inside WSR creation so that risk history is clear without creating a separate risk tracker.

Acceptance criteria:
- Risks support `Open`, `In-Progress`, and `Closed`.
- PM can move risk from `Open` to `In-Progress`.
- PM can close only `In-Progress` risks.
- Closed risks cannot be reopened; recurring issues require a new linked risk row.
- High active risks without owner, mitigation, or planned closure date block generation.
- Overdue risks are highlighted for the WSR form and dashboard.

Gherkin:

```gherkin
Feature: Risk lifecycle governance
  Scenario: PM attempts to reopen a closed risk
    Given a risk is Closed
    When the PM changes the status back to Open
    Then validation fails
    And the PM is instructed to create a new linked risk
```

Pytest coverage:
- Open to In-Progress transition test.
- Close only from In-Progress test.
- Closed risk cannot reopen test.
- High active risk blocks generation when accountability fields are missing.
- Overdue risk detection test.

### Phase 5 Stories: Production WSR UI

#### Story 5.1: Build Production WSR Form Shell

As a PM, I want a clean and aligned WSR form so that data entry feels simple and enterprise-ready.

Acceptance criteria:
- UI uses reusable section, field, select, metric, badge, risk grid, and action bar components.
- Form sections are aligned across desktop and mobile widths.
- Required fields are visually clear.
- Errors appear near the fields they belong to.
- Form controls are keyboard navigable with visible focus states.
- Required and error states use text or messages, not color alone.
- Icon-only buttons have accessible labels.
- Form sections expose semantic labels suitable for screen readers.

Gherkin:

```gherkin
Feature: WSR form shell
  Scenario: PM opens a new WSR form
    Given the PM has account and project access
    When the PM opens New WSR
    Then the form shows account/project, delivery model, setup, progress, risks, notes, and actions
    And required fields are marked consistently
```

Pytest coverage:
- Not applicable for React components.
- Backend API fixtures used by UI tests should be produced from Pydantic DTO tests.

#### Story 5.2: Switch UI by Delivery Model

As a PM, I want the form to show Sprint fields for Sprint projects and PI fields for PI projects so that I only enter relevant information.

Acceptance criteria:
- Delivery model is a dropdown.
- Selecting Sprint shows Sprint setup and Sprint progress fields.
- Selecting PI shows PI setup and PI progress fields.
- Switching models updates local calculations and validation metadata.

Gherkin:

```gherkin
Feature: Delivery model driven UI
  Scenario: PM selects PI delivery model
    Given the PM is creating a new WSR
    When the PM selects PI from delivery model
    Then PI setup fields are displayed
    And Sprint-only fields are hidden
```

Pytest coverage:
- Python metadata endpoint tests verify Sprint and PI field schemas.
- Python validation tests verify hidden model fields are not required.

### Phase 6 Stories: Agentic Generation Foundation

#### Story 6.1: Execute Stateful LangGraph Generation

As a PM, I want AI generation to run only after validation so that generated content is based on saved, reliable WSR data.

Acceptance criteria:
- `generate` validates persisted draft before enqueuing workflow.
- Workflow run is created with UUID, account, project, WSR, requester, status, and correlation ID.
- LangGraph loads persisted draft by `wsr_id`.
- Every node writes explicit state keys.
- Graph state is checkpointed by `workflow_run_id`.

Gherkin:

```gherkin
Feature: Stateful WSR generation
  Scenario: PM starts generation after valid draft
    Given a valid persisted WSR draft
    When the PM clicks Generate
    Then a workflow run is queued
    And LangGraph receives the workflowRunId
    And the graph loads the saved draft instead of browser state
```

Pytest coverage:
- Generation rejects invalid draft.
- Generation creates workflow run.
- Node unit tests assert read/write state keys.
- Checkpointer adapter test persists and restores state.

#### Story 6.2: Retrieve Approved Account and Project History

As the AI generation workflow, I want approved history scoped by account and project so that insights use relevant context without leaking data.

Acceptance criteria:
- Retrieval uses both account ID and project ID.
- Only approved WSRs are retrieved.
- PM-only insights, rejected drafts, and audit notes are excluded.
- Retrieved source IDs are stored in workflow metadata.

Gherkin:

```gherkin
Feature: Account project retrieval
  Scenario: Workflow retrieves approved history
    Given approved WSRs exist for multiple projects
    When generation starts for Account A Project 1
    Then only approved WSRs for Account A Project 1 are retrieved
    And retrieved source IDs are stored on the workflow run
```

Pytest coverage:
- Retrieval query account/project isolation test.
- Approved-only filter test.
- Redaction test for PM-only insight fields.

#### Story 6.3: Use Grok and DeepSeek Through Provider Adapters

As a platform admin, I want generation to use configured Grok and DeepSeek providers so that provider policy is runtime-configurable.

Acceptance criteria:
- Provider adapters live in the agent layer.
- Graph nodes call provider-neutral interfaces.
- Primary and fallback model IDs come from admin settings or environment defaults.
- Provider failures are normalized into controlled errors.

Gherkin:

```gherkin
Feature: LLM provider fallback
  Scenario: Primary provider has retryable failure
    Given Grok is configured as primary
    And DeepSeek is configured as fallback
    When Grok returns a retryable provider error
    Then the workflow retries using DeepSeek
    And the workflow records provider metadata without secrets
```

Pytest coverage:
- Provider selection test.
- Fallback on retryable error test.
- Non-retryable error test.
- Secret redaction in provider metadata test.

#### Story 6.4: Generate Deterministic PM Quality Insight Signals

As a PM, I want AI insights grounded in deterministic quality signals so that suggestions are actionable, evidence-backed, and relevant to customer-ready reporting.

Acceptance criteria:
- Green RAG with completion below 70% creates a high-severity discrepancy signal.
- Green RAG with active high-severity risks creates a high-severity discrepancy signal.
- Green RAG with spillover above 20% creates at least a medium-severity discrepancy signal.
- Risks open more than 30 days, overdue risks, weak mitigation text, and unclear business impact create risk insight signals.
- Achievements without measurable impact, vague progress updates, and next-week plans without owner, timing, or concrete outcome create quality insight signals.
- Internal-only wording, unclear acronyms, or customer-sensitive language create customer-safety insight signals.
- Each generated PM insight includes type, severity, description, evidence, recommendation, and suggested edit when applicable.

Gherkin:

```gherkin
Feature: PM quality insight signals
  Scenario: Green status conflicts with low completion
    Given a WSR has Green RAG status
    And completion percentage is below 70
    When insight signals are generated
    Then a high-severity discrepancy insight is produced
    And the insight includes metric evidence and a recommended action
```

Pytest coverage:
- Green with completion below 70 discrepancy test.
- Green with active high-risk discrepancy test.
- Spillover above 20 severity test.
- Risk aging and overdue signal tests.
- Weak mitigation and missing impact signal tests.
- Achievement, progress, and plan quality signal tests.
- Customer-sensitive wording signal test.
- Insight output schema completeness test.

### Phase 7 Stories: Human-in-the-Loop Review

#### Story 7.1: Show Collapsible Read-Only AI Insights

As a PM, I want to view AI insights as collapsible read-only guidance while editing the ready-to-share WSR preview so that the final customer-facing WSR reflects my judgment.

Acceptance criteria:
- AI insights are shown as collapsible read-only PM-only guidance.
- Insight cards include severity, type, evidence, recommendation, and suggested edit when applicable.
- AI insights are visually separate from the customer-facing WSR preview.
- PM applies insight guidance by editing ready-to-share WSR preview fields, not by accepting or rejecting insight cards.

Gherkin:

```gherkin
Feature: Collapsible read-only AI insights
  Scenario: PM edits WSR preview using insight guidance
    Given AI insights and ready-to-share WSR preview sections are available
    When the PM reviews the insights
    Then insight cards are collapsible and read-only
    And editable WSR preview sections remain available
```

Pytest coverage:
- Insight response read-only contract test.
- WSR preview payload includes all editable customer-facing sections.
- Collapsible insights layout behavior covered by frontend component or E2E tests.
- Audit event records that insights were viewed.

#### Story 7.2: Resume Graph After WSR Preview Review

As a PM, I want to review and edit generated customer-ready content before approval so that the WSR is customer-share ready.

Acceptance criteria:
- WSR preview review supports saving edited customer-facing content.
- Resume API requires workflow status `WAITING_FOR_PM_WSR_REVIEW`.
- Edited content becomes a `wsr_content_versions` row.
- WSR preview review is not the same as formal approval.

Gherkin:

```gherkin
Feature: PM WSR preview review checkpoint
  Scenario: PM edits ready-to-share WSR before approval
    Given generation is waiting for PM WSR review
    When the PM saves edited ready-to-share WSR sections
    Then a content version is created
    And the report is not yet approved
```

Pytest coverage:
- WSR preview review creates content version.
- WSR preview review does not create approval event.
- Completed workflow resume rejection test.

#### Story 7.3: Edit Ready-to-Share WSR Before Approval

As a PM, I want to edit the ready-to-share Weekly Status Report before approval so that I can verify and polish exactly what the customer-facing report will look like.

Acceptance criteria:
- Ready-to-share preview is available after generation and before approval.
- Preview renders customer-facing report sections in editable report format.
- Preview is generated from PM-entered facts and AI-assisted drafting.
- PM can edit executive summary, progress update, achievements, risks/dependencies summary, next week focus/actions, and remarks in the preview.
- Preview excludes PM-only insights, discrepancy evidence, suggestions, internal comments, and AI metadata.
- Approval controls remain separate from preview.

Gherkin:

```gherkin
Feature: Ready-to-share WSR preview
  Scenario: PM edits customer-facing WSR before approval
    Given the ready-to-share WSR preview exists
    When the PM updates the executive summary and next week focus
    Then the report is shown in editable customer-facing format
    And the PM changes are saved as the approvable WSR version
    And PM-only insights are not visible in the preview
    And the report is not approved yet
```

Pytest coverage:
- Preview DTO excludes PM-only insight fields.
- Preview source uses PM-entered facts and AI-assisted drafting.
- Preview edit persistence test.
- Ready-to-share WSR content schema version test.
- WSR review request rejects missing required content sections.
- Preview before approval does not create approval event.
- Customer-safe filtering test for preview payload.

### Phase 8 Stories: Approval, Export, and Dashboard

#### Story 8.1: Approve Immutable Content Version

As a PM, I want to approve a reviewed content version so that it becomes the official customer-facing WSR.

Acceptance criteria:
- Approval is allowed only from `IN_REVIEW`.
- Approval records actor, timestamp, decision, WSR ID, and content version ID.
- Approved content version becomes immutable.
- Editing after approval creates a new content version requiring re-approval.

Gherkin:

```gherkin
Feature: WSR approval
  Scenario: PM approves reviewed WSR content
    Given a WSR is in review
    And a content version is selected
    When the PM approves the WSR
    Then the content version is marked Approved
    And an approval event references the content version
```

Pytest coverage:
- Approve from valid state test.
- Reject approve from invalid state test.
- Immutable approved version test.
- Edit after approval creates new version test.

#### Story 8.2: Reject or Approve With Edits

As a PM, I want to approve with final edits or reject with feedback so that the WSR lifecycle captures my review decision accurately.

Acceptance criteria:
- Approval requires explicit confirmation.
- Approve with edits creates or updates the selected review content version before approval.
- Rejection requires feedback.
- Rejected drafts remain governed by retention policy.
- Approval and rejection events include actor, timestamp, decision, reason when provided, and content version reference where applicable.

Gherkin:

```gherkin
Feature: Review decision variants
  Scenario: PM rejects a generated WSR draft
    Given a WSR is in review
    When the PM rejects the draft with feedback
    Then the report status becomes Rejected
    And the rejection reason is stored in approval events
```

Pytest coverage:
- Approve with edits creates approved content version test.
- Reject requires feedback test.
- Rejected draft retention marker test.
- Approval confirmation required test.
- Approval event content version reference test.

#### Story 8.3: Export Approved WSR to PPTX

As a PM, I want to export the approved WSR to PPTX so that I can share a customer-safe report.

Acceptance criteria:
- Export is allowed only after approval.
- Export reads approved `wsr_content_versions`, not `ai_drafts`.
- PM-only insights never appear in export DTOs.
- Export attempts are tracked with status, object key, error code, and requester.

Gherkin:

```gherkin
Feature: Customer-safe PPTX export
  Scenario: PM exports approved WSR
    Given a WSR has an approved content version
    When the PM requests PPTX export
    Then the export service reads the approved content version
    And PM-only insights are excluded
    And an export attempt is recorded
```

Pytest coverage:
- Export before approval blocked test.
- Export source is approved content version test.
- PM-only insight exclusion test.
- Export idempotency test.

#### Story 8.4: View Executive Dashboard

As a delivery executive, I want to see WSR health across authorized projects so that I can quickly identify delivery concerns.

Acceptance criteria:
- Dashboard shows latest approved WSR status.
- Dashboard shows delivery metric health, active high risks, overdue risks, pending approvals, and export status.
- Filters include account, project, reporting week, delivery model, status, and risk severity.
- Dashboard respects authorization.

Gherkin:

```gherkin
Feature: Executive dashboard
  Scenario: Executive filters dashboard by account
    Given the executive is authorized for Account A
    When the executive filters dashboard by Account A
    Then only Account A project health appears
    And high risks and overdue risks are summarized
```

Pytest coverage:
- Dashboard authorization test.
- Latest approved WSR selection test.
- Risk severity aggregation test.
- Pending approval count test.

### Phase 9 Stories: Observability, Security, and Retention

#### Story 9.1: Propagate Correlation IDs

As an operator, I want every workflow action to carry a correlation ID so that incidents can be traced end to end.

Acceptance criteria:
- API creates or accepts a correlation ID.
- Correlation ID flows through validation, persistence, Celery, LangGraph, LLM calls, audit, and export.
- Error responses include correlation ID.
- Logs use structured fields.

Gherkin:

```gherkin
Feature: Correlation ID tracing
  Scenario: Generation fails in provider call
    Given a WSR generation request has a correlation ID
    When the LLM provider fails
    Then the API error includes the correlation ID
    And workflow logs include the same correlation ID
```

Pytest coverage:
- Middleware correlation ID test.
- Service log context test.
- Worker correlation propagation test.
- Error envelope correlation ID test.

#### Story 9.2: Apply Retention and Secret-Safe Logging

As a platform admin, I want retention and secret-safe logging so that operational data is governed properly.

Acceptance criteria:
- Retention jobs process drafts, rejected reports, checkpoints, generated artifacts, exports, and audit records according to policy.
- Provider secrets never appear in logs, audit events, graph state, or API responses.
- Prompt-injection-like content is sanitized before logging.

Gherkin:

```gherkin
Feature: Retention and secret safety
  Scenario: Retention job removes expired checkpoints
    Given workflow checkpoints older than retention policy exist
    When the retention job runs
    Then expired checkpoints are archived or deleted according to policy
    And approved WSR audit history is preserved
```

Pytest coverage:
- Retention selection test.
- Approved history preservation test.
- Secret redaction test.
- Prompt content sanitization test.

#### Story 9.3: Review Audit History as PMO

As a PMO analyst, I want to review read-only audit history so that reporting quality, approvals, edits, exports, and insight review can be verified.

Acceptance criteria:
- Audit history is filterable by account, project, WSR, user, event type, and date range.
- Audit events include data entry, draft save, validation failure, generation request, generated draft, AI insights viewed, PM edits, comments, approval, rejection, export request, export success, and export failure.
- Non-admin users cannot modify audit records.
- Audit access respects account/project authorization.

Gherkin:

```gherkin
Feature: PMO audit history review
  Scenario: PMO filters audit history by WSR
    Given the PMO analyst is authorized for the project
    When the analyst filters audit history by WSR ID
    Then matching lifecycle events are returned
    And the records are read-only
```

Pytest coverage:
- Audit filter by WSR test.
- Audit filter by event type and date range test.
- Read-only audit repository/API test.
- Audit authorization scope test.

#### Story 9.4: Monitor Operational Health

As a platform admin, I want operational health visibility so that generation, export, provider, queue, and latency issues can be detected quickly.

Acceptance criteria:
- Admin health view includes API health, database health, Redis/Celery queue health, model-provider health, object storage health, and configuration status.
- Metrics include generation failures, export failures, model-provider errors, queue depth, request latency, generation latency, export latency, and validation failure rate.
- Health responses hide secrets and return controlled degradation status.
- Operational health endpoints require platform-admin authorization.

Gherkin:

```gherkin
Feature: Admin operational monitoring
  Scenario: Admin checks model provider health
    Given the admin is authorized
    When the admin opens operational health
    Then model-provider status and recent failures are shown
    And provider secrets are not shown
```

Pytest coverage:
- Admin health authorization test.
- Healthy dependency status test.
- Degraded dependency status test.
- Metrics payload shape test.
- Secret redaction in health response test.

### Phase 10 Stories: Release Readiness

#### Story 10.1: Complete Automated Test Coverage

As a delivery team, I want automated tests across domain, API, agent, and UI flows so that release risk is visible.

Acceptance criteria:
- Pytest covers backend domain, services, repositories, API contracts, authorization, and agent nodes.
- E2E coverage includes Sprint WSR, PI WSR, generation, HITL review, approval, rejection, and export.
- Contract tests verify OpenAPI payloads.
- Tests can run without real provider credentials by using stubs.

Gherkin:

```gherkin
Feature: Release test coverage
  Scenario: CI runs release test suite
    Given the release branch is ready
    When CI runs automated tests
    Then Pytest unit and integration tests pass
    And E2E critical paths pass
    And no real LLM credentials are required for tests
```

Pytest coverage:
- Coverage threshold check.
- Provider stub test.
- OpenAPI contract snapshot test.
- Critical backend flow integration tests.

#### Story 10.2: Prepare Pilot Deployment

As a platform owner, I want deployment documentation and runbooks so that the pilot can be operated safely.

Acceptance criteria:
- Environment variables are documented.
- Deployment units are documented.
- Rollback and incident triage steps are documented.
- Health checks cover API, worker, database, Redis, object storage, and provider configuration.

Gherkin:

```gherkin
Feature: Pilot deployment readiness
  Scenario: Operator checks system health
    Given the pilot environment is deployed
    When the operator opens the health endpoint
    Then API, database, Redis, worker, object storage, and provider configuration health are reported
```

Pytest coverage:
- Health endpoint test with healthy dependencies.
- Health endpoint test with failed dependency.
- Configuration validation test for missing required environment values.

#### Story 10.3: Govern Release Branch, Tag, and Merge to Main

As a technical lead, I want each release to follow Git Flow release governance so that production-ready code is reviewed, tagged, documented, and recoverable.

Acceptance criteria:
- Release branch is cut from `develop` using `release/{version}`.
- Release PR targets `main` and includes release notes, migration notes, operational changes, known issues, and rollback guidance.
- Required CI checks pass before merge.
- Required approvals are present before merge.
- `main` is tagged with the semantic version after merge.
- Release branch changes are merged or cherry-picked back to `develop`.
- Hotfix branches cut from `main` and merge back into both `main` and `develop`.

Gherkin:

```gherkin
Feature: Git Flow release governance
  Scenario: Release PR is ready to merge to main
    Given a release branch exists from develop
    And all required CI checks pass
    And required approvals are present
    When the release PR is merged to main
    Then the main branch is tagged with the release version
    And release changes are reconciled back to develop
```

Pytest coverage:
- No product behavior required.
- CI policy check can verify required release-note files and version metadata.

#### Story 10.4: Validate Performance and Load Targets

As a delivery team, I want automated performance checks for key workflows so that MVP release meets the PRD operating targets.

Acceptance criteria:
- Dashboard portfolio view loads within 3 seconds at p95 for an authorized scope up to 500 projects.
- Risk table loads within 2 seconds at p95 for projects with up to 100 active risks.
- Standard PPTX export preparation completes within 5 seconds at p95.
- WSR draft save, validation, generation status polling, and export status polling have documented p95 targets.
- Test results are captured as release evidence.

Gherkin:

```gherkin
Feature: MVP performance targets
  Scenario: Dashboard portfolio load test
    Given an executive is authorized for 500 projects
    When the dashboard portfolio endpoint is tested under expected MVP load
    Then the p95 response time is less than 3 seconds
    And the result is stored as release evidence
```

Pytest coverage:
- Pytest performance smoke test for dashboard query shape.
- Pytest performance smoke test for risk table query shape.
- Pytest export timing test with deterministic PPTX fixture.
- Integration test verifies load-test fixtures match PRD scale assumptions.
