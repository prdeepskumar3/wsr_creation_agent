---
stepsCompleted:
  - generated-from-existing-prd
  - incorporated-system-design-context
  - incorporated-bmad-analysis
inputDocuments:
  - WSRCreation_Agent_PRD.md
  - WSRCreation_Agent_SystemDesign.md
  - _bmad-output/planning-artifacts/bmad-analysis-2026-06-27.md
workflowType: prd
status: Draft
documentVersion: "4.0"
date: "2026-06-27"
---

# Product Requirements Document - WSR Agent

**Author:** Prdeepskumar  
**Date:** 2026-06-27  
**Status:** Draft  
**Confidentiality:** Internal Use Only

## Executive Summary

WSR Agent is an enterprise weekly status report platform for Project Managers, delivery executives, PMO analysts, and platform administrators. It reduces weekly report creation effort, standardizes delivery reporting, validates project health data, governs risk closure inside WSR preparation, generates AI-assisted report drafts, surfaces discrepancy insights, enforces human approval, exports customer-safe PPTX reports, and maintains a complete audit trail.

The product combines deterministic business rules with AI-assisted drafting. PM-entered facts remain the source of truth. AI improves clarity, detects inconsistencies, suggests improvements, and drafts executive-ready language. Business rules validate required fields, delivery metrics, risk status transitions, spillover remarks, approval gates, export safety, and audit requirements.

The differentiator is controlled-agentic reporting: AI writes and recommends, while deterministic validation, PM approval, and audit controls preserve accountability and compliance.

## Product Vision

Project Managers can generate accurate, consistent, executive-ready weekly status reports in less than half their current effort while delivery leaders gain reliable visibility into project health, risks, discrepancies, and reporting quality.

## Problem Statement

Project Managers spend 1-2 hours each week creating WSRs manually. Reports vary by format, omit required information, contain inconsistent metrics, and often understate delivery risk. Risk closure documentation is inconsistent. Executives lack reliable early warning signals when PM-reported status differs from delivery reality. PMO teams lack clean audit trails for approval, edits, exports, and insight review.

## Target Users

| Persona | Primary Goals | Key Pain Points |
|---|---|---|
| Project Manager | Create accurate WSRs quickly, reuse prior context, validate data, review AI suggestions, approve final report | Repetitive data entry, formatting effort, missing prior-week context, inconsistent risk capture |
| Delivery Executive | See true project health, detect status discrepancies, identify escalation risks early | Surprise escalations, overly optimistic PM status, inconsistent reporting |
| PMO Analyst | Monitor reporting consistency, analyze delivery trends, audit report quality | Inconsistent data, limited audit history, manual trend analysis |
| Platform Admin | Configure system settings, integration endpoints, model provider settings, observability, and operational controls | Complex configuration, limited monitoring, difficult troubleshooting |

## Success Criteria

| Success Metric | Target | Measurement |
|---|---:|---|
| PM drafting-time reduction | >= 50% reduction versus manual baseline | Median time from WSR start to PM approval |
| Validated reports before generation | 100% | Generation blocked when required validation fails |
| Approved reports export gate | 100% | PPTX export impossible without recorded approval |
| Customer-safe exports | 100% | Export excludes PM-only insights, suggestions, and internal discrepancy notes |
| Risk closure compliance | 100% | Closed risks include closure remark, owner/contact, mitigation, and closure date history |
| Insight evidence coverage | 100% | Each generated insight includes evidence and recommended action |
| Audit event capture | 100% | Data entry, generation, edit, insight decision, approval, rejection, and export events recorded |
| Cross-account data leakage | 0 incidents | Authorization monitoring and audit review |
| API availability | >= 99.9% monthly | Production monitoring |
| Rules test coverage | >= 90% | Automated test coverage for validation and insight rules |

## Product Scope

### MVP Scope

MVP includes:

- Login and enterprise user session handling.
- Account and project selection restricted to user assignments.
- One-time project execution model selection with guarded edit flow.
- WSR data entry for project overview, delivery metrics, achievements, risks, next-week plan, and additional notes.
- Delivery model support for Sprint and PI.
- Deterministic validation for required fields, delivery metrics, spillover remarks, achievements, plan items, and risk fields.
- Risk governance fields inside WSR creation: owner/contact, severity, mitigation, planned closure date, status transition rules, overdue detection, and closure remarks.
- Previous approved WSR prefill for reusable context.
- AI-assisted draft generation.
- AI insights and suggestions for PM-only review.
- PM edit, comment, approve, reject, and approve-with-edits workflows.
- PPTX export after approval.
- Customer-safe export rules.
- Audit trail for all core lifecycle events.
- Executive dashboard for project health, status discrepancy alerts, overdue risks, and export/approval status.

### Growth Scope

Growth includes:

- Kanban, Support, Infrastructure, and POC delivery models.
- PMO trend analytics.
- Advanced historical trend analysis.
- Configurable insight rules by account or delivery organization.
- Template management for PPTX exports.
- Admin configuration for model-provider policy, secret references, webhook endpoints, retention policy, and observability.
- Executive dashboard filters by account, project, delivery model, status, risk severity, and reporting period.

### Out of Scope

The product is not:

- A replacement for PM accountability or final judgment.
- The enterprise identity provider.
- The enterprise project management system of record.
- A portfolio planning tool.
- A system that automatically changes customer-facing status without PM approval.
- A tool that exposes PM-only AI insights to customers.

## Product Decisions

| Decision | Product Requirement |
|---|---|
| Risk handling | Risks are captured as part of WSR preparation, not as a standalone risk-tracker workflow. Owner/contact is a required field on each risk row so the PM can document accountability, mitigation, and closure context. |
| Final WSR approver | PM approval is required for MVP. Manager approval can be added later as a configurable policy. |
| AI authority | AI can draft and suggest, but PM-approved content is the final report source of truth. |
| Customer-safe output | Customer-facing exports must exclude internal insights, discrepancy alerts, suggestions, PM comments, and AI evidence fields. |
| Retrieval scope | MVP retrieves approved WSR history only when both account ID and project ID match the current WSR and user authorization scope. |
| Delivery model edit | Execution model is selected once per project and can be changed only after confirmation because metrics and validation rules change. |

## User Journeys

### Journey 1: PM Creates and Approves a Weekly Status Report

1. PM logs into the enterprise portal.
2. PM selects an assigned account.
3. PM selects an assigned project under that account.
4. If the project execution model is unset, PM selects Sprint or PI in MVP.
5. If the execution model was previously set, the selected model appears read-only with an edit action.
6. If PM edits the execution model, the product warns that model-specific metrics and validation rules will change.
7. The product pre-fills reusable data from the latest approved WSR for the same account and project.
8. PM enters project overview, model-specific delivery metrics, achievements, risks, next-week plan, and notes.
9. PM clicks Generate WSR.
10. The product validates all required data.
11. If validation fails, PM sees field-level and summary-level errors and cannot generate.
12. If validation passes, the product generates an enhanced draft and PM-only insights.
13. PM reviews generated sections, insights, and suggestions.
14. PM reviews read-only insights, edits generated customer-facing report sections, and adds comments when needed.
15. PM approves or rejects the draft.
16. Approved WSR becomes the final version for export and future prefill.
17. PM exports the approved report to PPTX.

### Journey 2: PM Manages Risks During WSR Creation

1. PM adds a risk with description, status, severity, owner, mitigation, and planned closure date.
2. The product prevents duplicate risk descriptions within the active project lifecycle.
3. The product blocks risks missing required owner, mitigation, severity, status, or planned closure date.
4. PM moves risk from Open to In-Progress when mitigation begins.
5. PM can move In-Progress back to Open if active mitigation stops.
6. PM can close only In-Progress risks.
7. The product requires a closure remark when status changes to Closed.
8. Closed risks cannot be reopened; PM creates a new linked risk if the issue recurs.
9. Overdue risks and high-severity open risks appear in PM insights and executive dashboard.

### Journey 3: Delivery Executive Reviews Health and Discrepancies

1. Delivery executive opens the dashboard.
2. The dashboard shows project status, delivery metric health, high-severity risks, overdue risks, pending approvals, and latest export state.
3. The dashboard flags status discrepancies such as Green status with low completion, open high risks, overdue risks, or high spillover.
4. Delivery executive filters by account, project, delivery model, status, severity, and reporting week.
5. Delivery executive drills into approved WSRs and audit-safe summary data.

### Journey 4: PMO Analyst Audits Reporting Quality

1. PMO analyst views reporting consistency across projects.
2. The product shows report completion, approval status, export status, risk completeness, insight acceptance rate, and repeated discrepancy patterns.
3. PMO analyst reviews audit trail for selected reports.
4. PMO analyst exports audit evidence for compliance review.

### Journey 5: Platform Admin Configures Operations

1. Admin manages integration settings for enterprise auth, account/project sources, email notifications, export storage, BI/webhook endpoints, and LLM provider configuration.
2. Admin configures retention policy for drafts, generated content, exports, and audit records.
3. Admin monitors health, errors, generation latency, failed exports, and model-provider failures.

## Functional Requirements

### Authentication and Authorization

**FR-AUTH-001:** Users can log in with enterprise-approved credentials.

Acceptance criteria:
- Login requires a valid enterprise user identity.
- Invalid credentials return a clear error without exposing sensitive details.
- Successful login starts a user session.

**FR-AUTH-002:** Users can log out and end the active session.

Acceptance criteria:
- Logout invalidates the current session.
- Session timeout returns the user to login before protected data is shown.

**FR-AUTH-003:** Users can access only accounts, projects, reports, risks, insights, and dashboards permitted by role and assignment.

Acceptance criteria:
- PMs see only assigned accounts and projects.
- Delivery executives see only authorized portfolio/account scope.
- PMO analysts see only authorized audit/reporting scope.
- Unauthorized access attempts are denied and audited.

### Account, Project, and Delivery Model Selection

**FR-ACC-001:** PMs can select from accounts mapped to their user identity.

Acceptance criteria:
- Account dropdown excludes unmapped accounts.
- Empty account assignment shows a clear no-access state.

**FR-ACC-002:** PMs can select from projects mapped to the selected account and their user identity.

Acceptance criteria:
- Project dropdown stays disabled until account selection.
- Project list excludes unmapped projects.
- Breadcrumb updates after account and project selection.

**FR-MOD-001:** PMs can select one MVP execution model per project from Sprint and PI.

Acceptance criteria:
- First selection saves the execution model for the project.
- Saved model appears read-only on future WSRs.
- Edit action requires confirmation and explains metric impact.
- Kanban, Support, Infrastructure, POC, and other delivery models are not selectable in MVP and belong to growth scope.

**FR-MOD-002:** The product displays delivery metrics specific to the selected execution model.

Acceptance criteria:
- Sprint model captures sprint configuration, planned items, completed items, spillover, blockers, velocity, and remarks.
- PI model captures PI configuration, total scope, delivered scope, current sprint, remaining scope, required velocity, and remarks.
- Growth-scope delivery model metrics must be defined in PRD, UX, architecture, DTOs, validation, calculations, and tests before those models are enabled.

**FR-MOD-003:** The product auto-calculates derived delivery metrics from PM-entered values and approved historical context.

Acceptance criteria:
- PMs enter weekly actuals; PMs do not manually enter completion percentage, remaining scope, required velocity, average velocity, or confidence.
- Sprint completion percentage is calculated as `min(stories_completed / planned_stories * 100, 100)` when planned stories are greater than zero.
- Sprint point completion percentage is calculated as `min(story_points_completed / planned_story_points * 100, 100)` when planned story points are greater than zero.
- Sprint effort usage percentage is calculated as `effort_burned_hours / planned_effort_hours * 100` when planned effort hours are greater than zero.
- PI completed-to-date story points are calculated as `prior_completed_story_points + story_points_completed_this_week`.
- PI completion percentage is calculated as `completed_to_date_story_points / planned_story_points * 100` when planned story points are greater than zero.
- PI remaining story points are calculated as `max(planned_story_points - completed_to_date_story_points, 0)`.
- PI sprints remaining are calculated as `max(total_sprints - current_sprint, 1)`.
- PI required velocity is calculated as `remaining_story_points / sprints_remaining`.
- PI average velocity is calculated as `completed_to_date_story_points / current_sprint`.
- PI confidence is High when average velocity is greater than or equal to required velocity, Medium when average velocity is at least 80% of required velocity, and Low otherwise.
- Prior completed story points come from the last approved WSR or integrated delivery source and appear as read-only context.

### WSR Data Entry

**FR-WSR-001:** PMs can enter project overview data for the selected reporting week.

Acceptance criteria:
- Required fields include reporting week, overall status, release or milestone, and summary context.
- Overall status accepts only Green, Amber, or Red.

**FR-WSR-002:** PMs can enter at least three key achievements.

Acceptance criteria:
- Generation is blocked when fewer than three achievements are present.
- Each achievement supports free text.
- AI insights flag achievements without measurable impact.

**FR-WSR-003:** PMs can enter at least three next-week plan items.

Acceptance criteria:
- Generation is blocked when fewer than three plan items are present.
- AI insights flag plan items without owner or target timing when detectable.

**FR-WSR-004:** PMs can enter optional additional notes.

Acceptance criteria:
- Notes can be saved with drafts and approved WSRs.
- Notes are included in AI drafting context.

**FR-WSR-005:** PMs can save WSR drafts before generation.

Acceptance criteria:
- Draft saves current field values.
- Draft save creates an audit event.
- Draft can be resumed by the same authorized PM.

### Prefill and Historical Context

**FR-PRE-001:** PMs can prefill reusable fields from the latest approved WSR for the same account and project.

Acceptance criteria:
- Prefill source is displayed with reporting week and approval timestamp.
- PM can edit prefilled content before generation.
- Prefill does not copy prior PM-only insight content into customer-facing report content.

**FR-PRE-002:** AI generation can use approved Account + Project historical WSR context.

Acceptance criteria:
- Retrieval scope is limited to approved WSRs where both account ID and project ID match the current WSR in MVP.
- Retrieved context respects account and project authorization.
- Retrieval usage is logged with report ID and correlation ID.

### Risk Lifecycle Management

**FR-RSK-001:** PMs can add risks and dependencies during WSR data entry.

Acceptance criteria:
- Required fields: description, status, severity, owner, mitigation, planned closure date.
- Description minimum length is 10 characters.
- Owner minimum length is 2 characters.
- Mitigation minimum length is 10 characters.

**FR-RSK-002:** Risks support statuses Open, In-Progress, and Closed.

Acceptance criteria:
- Open to In-Progress is allowed.
- Open to Closed is blocked.
- In-Progress to Open is allowed.
- In-Progress to Closed is allowed only with closure remark.
- Closed to Open or In-Progress is blocked.

**FR-RSK-003:** Closed risks require closure remarks.

Acceptance criteria:
- Closure remark minimum length is 5 characters.
- Closure timestamp and user are captured.
- Missing closure remark blocks save and generation.

**FR-RSK-004:** Every active risk requires owner/contact, mitigation, severity, status, and planned closure date.

Acceptance criteria:
- High active risks without owner/contact, mitigation, or planned closure date block generation.
- High active risks appear in AI insights and executive dashboard.

**FR-RSK-005:** PMs can load active risks from the previous approved WSR.

Acceptance criteria:
- Open and In-Progress risks can carry forward.
- Closed risks appear in history but do not auto-load as active risks.
- Carry-forward action is audited.

**FR-RSK-006:** PMs can edit active risk details while preparing the WSR.

Acceptance criteria:
- PMs can update risk description, severity, status, owner/contact, mitigation, planned closure date, and closure remark inside the WSR form.
- Owner/contact is captured for accountability in the report but does not create a separate risk-owner workspace in MVP.
- Overdue risks are highlighted inside the WSR form and executive dashboard.

**FR-RSK-007:** The product prevents duplicate active risk descriptions for the same project.

Acceptance criteria:
- Duplicate check is case-insensitive and trims whitespace.
- Duplicate risk attempt returns a clear validation message.

### Validation

**FR-VAL-001:** The product validates required fields before WSR generation.

Acceptance criteria:
- Generation is blocked until all required fields pass validation.
- Validation errors identify field, rule, and corrective action.

**FR-VAL-002:** The product validates model-specific delivery metrics.

Acceptance criteria:
- Sprint completed items cannot exceed planned items unless an explicit over-delivery reason is provided.
- Spillover greater than zero requires remarks.
- PI current sprint cannot exceed total sprint count.
- PI planned story points must be greater than zero before PI completion and velocity calculations are shown.
- PI completed-to-date story points cannot exceed planned story points unless an explicit scope-change reason is provided.
- Negative metric values are rejected.

**FR-VAL-003:** The product validates cross-field consistency before generation.

Acceptance criteria:
- Green status with critical delivery gaps generates a high-severity insight.
- Green status with active high-severity risks generates a high-severity insight.
- Overdue high-severity risks generate a high-severity insight.

### AI Draft Generation

**FR-AIG-001:** PMs can generate an AI-assisted enhanced draft after validation passes.

Acceptance criteria:
- Generation starts only after validation success.
- Draft includes executive summary, Week Progress Update, risks, delivery health, next-week plan, and customer-safe wording.
- Generation progress is visible to PM.
- Generation timeout is 30 seconds for MVP.

**FR-AIG-002:** AI draft content remains editable before approval.

Acceptance criteria:
- PM can edit all generated customer-facing sections.
- Edits are captured in audit trail with before and after values.

**FR-AIG-003:** AI generation failures show recoverable errors.

Acceptance criteria:
- Model-provider failure returns a clear retry message.
- Failed generation does not erase saved PM input.
- Failure event includes correlation ID in logs.

### AI Insights and Suggestions

**FR-AIS-001:** The product generates PM-only insights from PM-entered data, delivery metrics, risk data, and approved Account + Project history.

Acceptance criteria:
- Each insight includes type, severity, description, evidence, and recommended action.
- Insights are not included in customer-facing exports.

**FR-AIS-002:** The product detects status discrepancies.

Acceptance criteria:
- Green status with completion below 70% creates a high-severity discrepancy insight.
- Green status with one or more active high-severity risks creates a high-severity discrepancy insight.
- Green status with spillover above 20% creates at least a medium-severity discrepancy insight.

**FR-AIS-003:** The product detects risk alerts.

Acceptance criteria:
- More than two active high-severity risks creates a high-severity insight.
- Risks open more than 30 days create an aging-risk insight.
- Risks past planned closure date create an overdue-risk insight.

**FR-AIS-004:** The product detects achievement quality issues.

Acceptance criteria:
- Fewer than three achievements blocks generation.
- Achievements without measurable impact create an enhancement insight.
- Very short achievement text creates a low-severity detail insight.

**FR-AIS-005:** The product detects plan quality issues.

Acceptance criteria:
- More than five plan items creates a prioritization suggestion.
- Plan items without detectable ownership create a medium-severity ownership insight.
- Plan items without target timing create a low-severity timing insight.

**FR-AIS-006:** PMs can view AI insights as collapsible, read-only guidance while editing the ready-to-share WSR preview.

Acceptance criteria:
- Insights are displayed as PM-only advisory content with severity, type, evidence, recommendation, and suggested edit when applicable.
- Insights are collapsed by default or available in a collapsible view so the WSR editing surface remains primary.
- Insights do not require accept, reject, modify, or ignore actions.
- PMs apply any desired changes by editing the ready-to-share customer-facing WSR preview.
- Insight view events and WSR preview edits are auditable.

### PM Review and Approval

**FR-APR-001:** PMs can preview the enhanced draft before approval.

Acceptance criteria:
- Preview includes an editable, ready-to-share customer-facing view showing how the Weekly Status Report will look before approval/export.
- Ready-to-share preview is optimized for executive/customer review and is the primary PM editing surface after generation.
- Ready-to-share preview shows account, project, reporting period, delivery model, RAG status, executive summary, progress metrics, key achievements, risks/dependencies, next week focus/actions, and customer-facing remarks.
- Ready-to-share preview is generated from PM-entered facts and AI-assisted drafting, then can be edited by the PM before approval.
- Preview keeps PM-only insights in a separate collapsible advisory area.
- Customer-facing and PM-only content are visually distinct.
- Ready-to-share preview excludes PM-only insights, discrepancy evidence, suggestions, comments, and internal AI metadata.

**FR-APR-002:** PMs can approve, approve with edits, or reject a draft.

Acceptance criteria:
- Approval requires confirmation.
- Approval records approver, timestamp, approval status, and final content version.
- Rejection requires feedback.
- Rejected drafts remain governed by retention policy.

**FR-APR-003:** Approved WSRs become immutable customer-facing records.

Acceptance criteria:
- Changes after approval create a new version or require re-approval.
- Approved version is used for export and future prefill.

### Export

**FR-EXP-001:** PMs can export approved WSRs to PPTX.

Acceptance criteria:
- Export is disabled until approval is recorded.
- Export includes approved customer-facing content.
- Export excludes PM-only insights, suggestions, comments, discrepancy evidence, and internal AI metadata.

**FR-EXP-002:** Export attempts are tracked.

Acceptance criteria:
- Export request, success, failure, file reference, user, and timestamp are recorded.
- Export failure preserves approved report state.

### Executive Dashboard

**FR-DASH-001:** Delivery executives can view project health across authorized projects.

Acceptance criteria:
- Dashboard shows latest approved WSR status, delivery metric health, active high risks, overdue risks, pending approvals, and export status.
- Dashboard supports filters for account, project, reporting week, delivery model, status, and risk severity.

**FR-DASH-002:** Dashboard shows discrepancy signals.

Acceptance criteria:
- Discrepancy count is visible per project.
- Users can drill into evidence for authorized projects.
- Customer-facing exports remain unaffected by internal discrepancy signals.

### Audit Trail

**FR-AUD-001:** The product records audit events for WSR lifecycle actions.

Acceptance criteria:
- Events include data entry, draft save, validation failure, generation request, generated draft, AI insights viewed, PM edits, comments, approval, rejection, export request, export success, and export failure.
- Events include user, timestamp, WSR ID, action, before data when applicable, after data when applicable, and metadata.

**FR-AUD-002:** Authorized PMO users can review audit history.

Acceptance criteria:
- Audit history is filterable by account, project, WSR, user, event type, and date range.
- Audit records are read-only for non-admin users.

### Platform Administration

**FR-ADM-001:** Admins can configure integration endpoints.

Acceptance criteria:
- Admins can configure enterprise auth, account/project source, email/notification service, BI/webhook endpoints, export storage, model-provider policy, model IDs, fallback rules, and secret references.
- Provider API keys are managed through approved secret storage and are not persisted in application settings, workflow state, prompts, logs, or audit payloads.
- Configuration changes are audited.

**FR-ADM-002:** Admins can configure retention policy.

Acceptance criteria:
- Retention settings cover drafts, rejected reports, approved reports, exports, checkpoints, insights, and audit logs.
- Retention changes are audited.

**FR-ADM-003:** Admins can monitor operational health.

Acceptance criteria:
- Admin view includes API health, generation failures, export failures, model-provider errors, queue health, and latency metrics.

## Non-Functional Requirements

### Performance

| Requirement | Target | Measurement |
|---|---:|---|
| Prefill response time | < 1 second at p95 under normal business load | APM timing |
| WSR generation time | < 30 seconds at p95 for validated input | Workflow telemetry |
| Insight generation time | < 5 seconds at p95 | Workflow telemetry |
| Dashboard load time | < 3 seconds at p95 for authorized portfolio scope | Frontend and API telemetry |
| Risk table load time | < 2 seconds at p95 for projects with up to 100 active risks | API telemetry |
| UI interaction response | < 200 ms for local form interactions | Browser performance measurement |
| Export download preparation | < 5 seconds at p95 for standard PPTX reports | Export telemetry |

### Scale

| Requirement | Target | Measurement |
|---|---:|---|
| Daily PM usage | 100 PMs daily in MVP | Active usage analytics |
| Weekly report volume | 500 WSRs weekly | Application metrics |
| Active risks per project | Up to 100 active risks | Load test |
| Dashboard portfolio view | Up to 500 projects per authorized executive scope | Load test |

### Reliability

**NFR-REL-001:** The product shall maintain 99.9% monthly API availability measured by production monitoring.

**NFR-REL-002:** The product shall preserve PM-entered data during AI generation failures as verified by failed-generation recovery tests.

**NFR-REL-003:** The product shall retry export generation with idempotency for transient failures and prevent duplicate final export records.

**NFR-REL-004:** The product shall surface model-provider failures to users with a recoverable message and correlation ID.

### Security

**NFR-SEC-001:** The product shall enforce server-side authorization on 100% of protected API requests as measured by automated authorization tests.

**NFR-SEC-002:** The product shall isolate account and project data so users cannot retrieve unmapped data through UI or API paths.

**NFR-SEC-003:** The product shall prevent secrets from appearing in source code, user-visible errors, or application logs as verified by secret scanning and log review.

**NFR-SEC-004:** The product shall restrict PM-only insights, suggestions, comments, and discrepancy evidence to authorized internal users.

### Data Management and Retention

**NFR-DATA-001:** The product shall attach account ID and project ID to every WSR, risk, insight, audit event, approval event, and export event.

**NFR-DATA-002:** The product shall retain approved WSRs, risk history, approvals, exports, and audit records according to admin-configured retention policy.

**NFR-DATA-003:** The product shall archive or purge rejected drafts according to admin-configured retention policy.

**NFR-DATA-004:** The product shall track data cutoff timestamp for each generated report.

### Observability

**NFR-OBS-001:** The product shall generate a correlation ID for 100% of WSR generation workflows and propagate it through API logs, workflow logs, validation events, LLM calls, persistence actions, and export attempts.

**NFR-OBS-002:** The product shall emit structured logs for validation failures, generation stages, model calls, insight generation, audit writes, approval events, and export attempts.

**NFR-OBS-003:** The product shall expose operational metrics for request latency, generation latency, model-provider failure rate, export failure rate, validation failure rate, and queue depth.

### Compliance and Auditability

**NFR-COMP-001:** The product shall preserve an immutable audit trail for approved WSR lifecycle events.

**NFR-COMP-002:** The product shall block customer-facing export until approval is recorded.

**NFR-COMP-003:** The product shall exclude PM-only insight content from 100% of customer-facing exports as verified by export tests.

**NFR-COMP-004:** The product shall record closure remarks for 100% of closed risks.

## Domain Requirements

The product operates in an enterprise delivery governance context. Compliance focus areas are:

- Access control by user role, account, and project assignment.
- Complete audit trail for data entry, AI generation, PM insight viewing, PM edits, approvals, rejections, and exports.
- Customer-safe output controls.
- Retention policy for drafts, generated content, approved records, exports, risks, and audit events.
- No customer exposure of internal discrepancy analysis unless explicitly approved through future policy.
- Traceable risk governance with owner, mitigation, planned closure date, status transitions, closure remarks, and overdue detection.

## Project-Type Requirements

The product is a web-based enterprise application with:

- Role-based workflows.
- Data-entry-heavy PM experience.
- Dashboard views for executives and PMO users.
- AI-assisted generation with deterministic rule validation.
- Export workflow with customer-safe output constraints.
- Integration with enterprise identity, account/project source systems, notification services, model providers, file storage, and optional BI/webhook endpoints.

## Innovation Analysis

WSR Agent differs from basic report generators through:

- Controlled-agentic architecture: AI drafts; rules validate; PM approves.
- Delivery model awareness for Sprint and PI in MVP, with an extension path for Kanban, Support, Infrastructure, and POC.
- Built-in discrepancy detection between reported status and metric/risk reality.
- Risk lifecycle governance embedded in WSR creation and executive visibility.
- PM-only AI insights separated from customer-facing exports.
- Complete audit trail across human and AI-assisted decisions.

## Requirement Traceability

| Product Objective | Supporting Requirements |
|---|---|
| Reduce PM effort | FR-PRE-001, FR-PRE-002, FR-AIG-001, FR-AIG-002 |
| Improve report quality | FR-VAL-001, FR-VAL-002, FR-VAL-003, FR-AIS-001 through FR-AIS-006 |
| Govern risks | FR-RSK-001 through FR-RSK-007, NFR-COMP-004 |
| Preserve accountability | FR-APR-001 through FR-APR-003, FR-AUD-001, FR-AUD-002 |
| Protect customer-facing output | FR-EXP-001, NFR-COMP-002, NFR-COMP-003 |
| Provide executive visibility | FR-DASH-001, FR-DASH-002 |
| Support enterprise operations | FR-ADM-001 through FR-ADM-003, NFR-SEC-001 through NFR-SEC-004 |

## MVP Acceptance Checklist

- PM can create a WSR for an assigned project.
- Sprint and PI delivery models validate required metrics.
- Active risks can be created, carried forward, updated, closed with remarks, and shown on dashboards.
- Validation blocks incomplete reports before generation.
- AI generates an editable enhanced draft.
- AI generates PM-only evidence-backed insights.
- PM can view collapsible insights as read-only guidance and edit the ready-to-share WSR preview.
- PM can approve or reject the draft.
- Approved report exports to customer-safe PPTX.
- Audit events cover the WSR lifecycle.
- Executive dashboard shows project health, status discrepancies, overdue risks, and approval/export status.
- Admin can configure core integrations and monitor operational health.

## Future Considerations

- Manager approval workflow as configurable policy.
- Account-level historical retrieval after privacy and relevance controls are approved.
- Advanced PMO analytics and trend exports.
- BI platform push integration.
- Configurable customer-safe status controls.
- Custom report templates per account.
- Multi-language report generation.
