---
stepsCompleted:
  - initialized-from-user-ui-reference
  - captured-visual-direction
  - defined-wsr-creation-screen
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - WSRCreation_Agent_PRD.md
  - WSRCreation_Agent_SystemDesign.md
  - _bmad-output/planning-artifacts/bmad-analysis-2026-06-27.md
workflowType: ux-design
status: Draft
date: "2026-06-27"
---

# UX Design Specification wsr_creation_agent

**Author:** Prdeepskumar  
**Date:** 2026-06-27

## UX Direction

The WSR creation experience should feel like a compact enterprise workbench: structured, form-forward, calm, and fast to scan. The reference UI uses stacked accordion sections, numbered steps, required/completion badges, compact inputs, status chips, and inline validation cues. This is the right direction for the product because PMs repeat the workflow weekly and need efficient data entry more than a marketing-style experience.

The screen must feel like a top-tier internal product, not a demo form. Components should align to a consistent grid, section headers should have the same height, form controls should share sizing and rhythm, and table columns should be intentionally sized instead of relying on accidental horizontal scrolling.

## Primary Screen

The first implementation target is `Create weekly status report`.

Screen goals:

- Let PM create a complete WSR from top to bottom without leaving the page.
- Show progress through ordered sections.
- Make required work visible.
- Preserve previous-week prefill context.
- Keep AI and system status visible without distracting from data entry.
- Support dense entry of delivery metrics and risks.

## Layout Model

Use a single-column, scrollable form layout with a sticky top command bar.

Top command bar:

- Left: product area label `Weekly reports`.
- Middle: current flow label `New WSR`.
- Right: status chip `Draft`, action buttons `Preview` and `History`.

Page header:

- Title: `Create weekly status report`.
- Metadata line: reporting week range and last saved timestamp.

Prefill banner:

- Green-tinted success state.
- Message: previous week data and sprint/report context prefilled.
- Must be dismissible only if product decides prefill is optional; default MVP keeps it visible.

Accordion form sections:

1. Account and project
2. Delivery model
3. Sprint setup or model-specific setup
4. Delivery progress
5. Risks and dependencies
6. AI insights and suggestions
7. Review and approval

Each section header includes:

- Numbered circular step indicator.
- Section title.
- Short subtitle or summary.
- Right-side badge for state: `Required`, `Sprint based`, `Prefilled`, `RAG: Amber`, `1 high`, `Ready`.
- Collapse/expand icon.

Production alignment rules:

- Use adaptive field grids with consistent gaps and minimum field widths.
- Keep section body padding consistent across all panels.
- Align helper panels with the controls they describe.
- Avoid forced horizontal scrolling for core fields on standard laptop widths.
- Risk table columns must use explicit widths for index, severity, status, owner, date, and actions.
- Long text cells should use textarea controls with consistent row height.

## Visual Style

Tone:

- Enterprise SaaS.
- Quiet, structured, and reliable.
- Dense but not cramped.

Recommended styling:

- Background: light neutral `#f7f8fa`.
- Surface: white panels with `1px` neutral border.
- Border radius: 8px maximum.
- Primary action blue: `#2f78d6`.
- Success green: `#4b8f2f`.
- Warning amber: `#a46100`.
- Danger red: `#b42318`.
- Text primary: `#171717`.
- Text secondary: `#6f7377`.

Typography:

- Use system font stack.
- Page title: 18-20px, semibold.
- Section title: 15-16px, semibold.
- Labels: 12-13px.
- Inputs: 15-16px.
- Avoid oversized hero typography.

## Component Requirements

### Header Bar

Required elements:

- Breadcrumb-style label: `Weekly reports / New WSR`.
- Draft chip.
- Preview button.
- History button.

Interaction:

- Preview opens report preview using current saved/generated state.
- History opens audit/history panel.
- Draft chip reflects current report lifecycle state: Draft, Generated, Pending Approval, Approved, Rejected.

### Prefill Banner

States:

- Success: prefill applied.
- Info: no previous approved WSR available.
- Warning: previous WSR found but cannot prefill due to execution model change.

Content format:

- `Previous week data (Sprint 13) prefilled. Review and update before submitting.`

### Account and Project Section

Fields:

- Account, required select.
- Project, required select.
- WSR date, required date.
- Reporting period, read-only derived range.
- Report prepared by, read-only user display.

Validation:

- Project disabled until account is selected.
- WSR date required.
- Account/project choices must reflect authorization.

### Delivery Model Section

Controls:

- Single required dropdown for Sprint based and PI based in MVP.
- Future delivery models such as Milestone, Support, Infrastructure, Kanban, and POC must not appear as selectable options until their forms, validation, calculations, and tests are designed.
- Adjacent helper panel explaining the selected model and the metrics it activates.

Behavior:

- Saved execution model is selected in the dropdown.
- Saved model is treated as project configuration.
- Changing model requires explicit confirmation because metrics change.
- Section header badge and subtitle update to match the selected model.

### Model Setup Section

For Sprint MVP:

- Sprint name or number.
- Start date.
- End date.
- Planned stories.
- Planned story points.
- Planned effort hours.
- DOR percentage.

For PI based:

- PI name or number.
- PI start date.
- PI end date.
- Total sprints or iterations.
- Planned story points or planned scope.
- Committed features.
- Target release.
- PI objectives summary.

PI setup behavior:

- PI setup is one-time or rarely edited.
- PI setup should be prefilled after the first PI report.
- PI setup should be visually separate from weekly PI progress.
- System-calculated PI health fields should not require weekly PM entry.

States:

- `Prefilled` badge when copied from previous approved WSR.
- Required markers on fields that block generation.

### Delivery Progress Section

Sprint weekly fields:

- High-level progress update, required textarea.
- Stories completed.
- Story points completed.
- Effort burned hours.
- Unplanned stories.
- Unplanned story points.

PI weekly fields:

- PI progress update, required textarea.
- Current sprint or iteration.
- Story points completed this week.
- Features completed this week.
- Delayed scope items.
- Blockers or dependencies count.
- Next week plan.
- Remarks or notes.

PI system-calculated fields:

- PI completion percentage.
- Remaining story points.
- Required velocity.
- Average velocity.
- Confidence level.

Calculation formulas:

| Field | Formula | Source |
|---|---|---|
| Sprint completion % | `min(stories_completed / planned_stories * 100, 100)` | Planned stories and weekly completed stories |
| Sprint point completion % | `min(story_points_completed / planned_story_points * 100, 100)` | Planned story points and weekly completed story points |
| Sprint effort usage % | `min(effort_burned_hours / planned_effort_hours * 100, 999)` | Planned sprint effort and weekly burned effort |
| PI completed to date | `prior_completed_story_points + story_points_completed_this_week` | Prior approved WSR/system context plus PM weekly entry |
| PI completion % | `completed_to_date_story_points / planned_story_points * 100` | System calculated |
| PI remaining story points | `max(planned_story_points - completed_to_date_story_points, 0)` | System calculated |
| PI sprints remaining | `max(total_sprints - current_sprint, 1)` | PI setup and PM current sprint |
| PI required velocity | `remaining_story_points / sprints_remaining` | System calculated |
| PI average velocity | `completed_to_date_story_points / current_sprint` | System calculated |
| PI confidence | High when average velocity >= required velocity; Medium when average velocity >= 80% of required velocity; Low otherwise | System calculated |

Calculation behavior:

- PM should not enter calculated fields manually.
- Prior completed story points should be read-only and sourced from the last approved WSR or integrated delivery source.
- Calculated fields update immediately when PM changes planned story points, total sprints, current sprint, or this-week completed story points.
- Calculated fields should be visually read-only but still easy to scan.

Shared fields:

- Overall RAG status dropdown: Green - on track, Amber - at risk, Red - off track.
- Next week plan textarea.
- Remarks/notes textarea.

Behavior:

- Delivery model selection controls which setup and progress fields are visible.
- Sprint based shows Sprint setup and Sprint delivery metrics.
- PI based shows PI setup and weekly PI update metrics.
- Other delivery models should not show Sprint or PI fields until those model forms are designed.
- RAG chip in section header updates based on selected status.
- RAG helper text explains the selected status in plain delivery language.
- Delivery metric cards are compact, fixed-width, and do not shift layout.
- Numeric fields reject invalid negative values.

### Risks and Dependencies Section

Default layout:

- Table for active risks and dependencies.
- Columns: number, risk description, severity, status, mitigation, owner, planned closure date, remarks.
- Compact dropdowns for severity and status.
- Top-right `Add risk row` action.
- Editable textarea cells for risk description and mitigation.
- Editable owner and planned closure date fields.
- Remove action per row, disabled or ignored when only one row remains.
- Table uses explicit column sizing and fits within the card on standard desktop widths.
- Inputs inside the table are borderless at rest and show a clear focus state during editing.

Required risk behavior:

- High severity risks show red count badge in section header.
- Adding a row appends an empty editable row and focuses the risk description field.
- Risk row numbering updates after add/remove.
- High severity count updates when severity dropdowns change.
- Closed risks require remarks.
- Open to Closed transition is blocked.
- Closed risks cannot be reopened.
- Overdue risks show warning state.

### AI Insights Section

Layout:

- AI insights appear as a collapsed PM-only advisory section above the ready-to-share WSR preview.
- Each insight appears as a compact read-only row/card with severity, type, evidence, recommendation, and suggested edit when applicable.
- Insight categories include consistency, completeness, metric evidence, risk communication, customer-ready wording, actionability, and trend awareness.
- Discrepancy is only one insight category; the main purpose is helping PMs make the WSR enterprise-quality and customer-share ready.
- Wording improvement insights should show the original field context and a PM-reviewable suggested edit, but the actual change is applied by editing the ready-to-share WSR preview.
- Insights based on history use approved WSR context for the same account and project.

Actions:

- No direct actions on insight cards in MVP.
- PM applies insight guidance by editing ready-to-share WSR preview sections.
- The ready-to-share WSR preview must expose editable fields for each customer-facing section: executive summary, progress update, achievements, risks/dependencies, next week focus/actions, and remarks.
- On desktop and mobile, insights remain separate from the editable WSR preview and do not compete with the main editing surface.

Customer-safety:

- Clear visual distinction: PM-only content is never part of exported customer report.

### Review and Approval Section

Controls:

- Generate WSR.
- Save draft.
- Ready-to-share preview.
- Approve.
- Reject.
- Export PPTX.

State rules:

- Generate disabled until required fields pass.
- Approve disabled until generation exists.
- Export disabled until approval is recorded.
- Ready-to-share preview is available after generation and before approval.
- Preview renders the customer-facing WSR as an editable report-style surface, not as a duplicate raw data-entry form.
- Preview presents an executive-ready progress picture with account/project context, reporting period, delivery model, RAG status, executive summary, metric cards, sprint/PI progress, achievements, risks/dependencies, next week focus/actions, and remarks.
- Preview uses dense but readable report composition so approvers can understand progress, risk, and required attention without reading the full data-entry form.
- Preview excludes PM-only insights, discrepancy evidence, internal comments, and AI metadata.
- On desktop and mobile, PM edits the ready-to-share WSR preview directly before approval.

## Responsive Behavior

Desktop:

- Center content in a max-width work area.
- Use two to five columns for compact field groups depending on available width.
- Risk table scrolls horizontally if needed.

Mobile:

- Single-column field layout.
- Header action buttons remain visible but can wrap.
- Risk table uses horizontal scroll.
- Section headers must keep badge visible and avoid text overlap.

## Accessibility

- Every input has a visible label.
- Required fields use text marker and validation message, not color alone.
- Status chips include text.
- Buttons have accessible labels.
- Keyboard users can tab through fields and accordion controls in logical order.
- Error messages are associated with fields.

## Prototype Reference

A static HTML prototype is available at:

`_bmad-output/planning-artifacts/wsr-ui-prototype.html`

Use it as a visual direction artifact, not final production code.
