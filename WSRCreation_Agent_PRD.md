# WSR Agent - Complete Product Requirements Document
## Version 3.0 - Enhanced with AI Insights & Audit Trail

---

**Document Version:** 3.0  
**Status:** Active  
**Owner:** Product Delivery Intelligence Team  
**Last Updated:** 2026-06-21  
**Next Review:** 2026-07-21  
**Confidentiality:** Internal Use Only

---

# Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Product Overview](#2-product-overview)
3. [User Personas](#3-user-personas)
4. [User Journey](#4-user-journey)
5. [Functional Requirements](#5-functional-requirements)
6. [Risk Management Module](#6-risk-management-module)
7. [AI Insights & Suggestions Module](#7-ai-insights--suggestions-module)
8. [Audit Trail Module](#8-audit-trail-module)
9. [Non-Functional Requirements](#9-non-functional-requirements)
10. [Technical Architecture](#10-technical-architecture)
11. [Data Model](#11-data-model)
12. [Validation Rules](#12-validation-rules)
13. [Implementation Roadmap](#13-implementation-roadmap)
14. [Success Metrics](#14-success-metrics)
15. [Open Questions](#15-open-questions)
16. [Appendices](#16-appendices)

---

# 1. Executive Summary

## 1.1 Product Vision

WSR Agent is an enterprise-grade AI-powered platform that transforms how Project Managers create weekly status reports. By combining deterministic business rules with intelligent agent orchestration, the system reduces manual effort by 50 percent, ensures data quality, and produces executive-ready reports with human approval gates.

## 1.2 Problem Statement

Project Managers spend 1-2 hours weekly creating status reports manually. Reports often contain inconsistencies, missing data, and formatting issues. Risk tracking is inconsistent. There is no standardized process for report generation, validation, and approval.

## 1.3 Solution Overview

WSR Agent provides:
- Automated WSR generation using AI agents
- Deterministic validation rules for data quality
- Multiple delivery model support (Sprint, PI, Kanban, Support, Infrastructure, POC)
- Mandatory risk governance with closure remarks
- Human-in-the-loop approval workflow
- PPTX export capabilities
- AI-powered insights and suggestions for PM review
- Complete audit trail for compliance and analysis
- Executive dashboard with discrepancy detection

## 1.4 Key Benefits

| Benefit | Impact |
|---------|--------|
| 50% reduction in drafting time | PMs save 10 mins weekly |
| 100% data validation | No incomplete or inconsistent reports |
| Standardized reporting | Consistent format across all projects |
| Risk governance | All risks tracked with mandatory closure remarks |
| Executive visibility | Real-time project health and discrepancy detection |
| Audit trail | Complete history of all changes and approvals |
| AI Insights | Data-driven suggestions to improve report accuracy |
| Escalation prevention | Early detection of PM-reported vs. actual status discrepancies |

---

# 2. Product Overview

## 2.1 What It Is

WSR Agent is an enterprise-grade weekly status report generation platform that:

- Automates the creation of consistent, high-quality WSRs
- Validates inputs through deterministic rule engines
- Orchestrates specialized AI agents for drafting and review
- Enforces human approval before export
- Maintains full auditability and traceability
- Supports multiple delivery models
- Enforces risk governance with mandatory closure remarks
- Provides AI-powered insights and suggestions for PM review
- Maintains complete audit trail for compliance

## 2.2 What It Is Not

WSR Agent is not:
- A replacement for PM accountability and judgment
- A standalone identity management system
- A portfolio management system of record
- A tool to override PM decisions

## 2.3 Key Differentiators

| Feature | Benefit |
|---------|---------|
| Controlled-Agentic Architecture | LLMs write; rules verify facts |
| Pluggable Tracking Models | Supports Sprint, PI, Kanban, Support, Infrastructure, POC |
| Human-in-the-Loop Approval | PM controls final output |
| Risk Lifecycle Governance | Open, In-Progress, Closed with mandatory closure remarks |
| Prefill from Approved WSR | Reduces repetitive data entry |
| Enterprise-Scale Ready | Designed for 500 PMs weekly |
| AI Insights & Suggestions | Data-driven recommendations for PM review |
| Complete Audit Trail | Full traceability for compliance and analysis |
| Discrepancy Detection | Data reveals reality vs. PM-reported status |

---

# 3. User Personas

## 3.1 Project Manager (Primary User)

**Role:** Creates weekly status reports for assigned projects

**Goals:**
- Create WSRs quickly and efficiently
- Ensure data accuracy and completeness
- Track and manage project risks
- Get AI assistance for report generation
- Maintain consistent reporting standards
- Review AI insights and incorporate relevant suggestions

**Pain Points:**
- Repetitive data entry every week
- Inconsistent report formats
- Time-consuming manual formatting
- Missing risk documentation
- No structured approval workflow
- No AI assistance for content improvement
- No Previous week WSR Context

**Success Metrics:**
- Time to create WSR reduced by 50%
- 100% of reports validated before generation
- All risks tracked with proper closure documentation
- 80% of AI insights incorporated into final report

## 3.2 Delivery Executive

**Role:** Consumes approved WSRs and makes decisions

**Goals:**
- Get real project health without relying only on PM reports
- Identify discrepancies between reported and actual status
- Detect escalation risks before they become client escalations
- Make informed decisions based on real data

**Pain Points:**
- PMs reporting everything is fine when it is not
- Surprise escalations
- Inconsistent or missing information
- No visibility into risk status

**Success Metrics:**
- 100% visibility into project health
- Zero surprise escalations
- Data-driven decision making

## 3.3 PMO Analyst

**Role:** Reviews trends and reporting consistency

**Goals:**
- Analyze delivery trends across projects
- Ensure reporting standards are followed
- Identify pattern of risks and issues
- Generate insights from historical data
- Audit PM reporting accuracy

**Pain Points:**
- Inconsistent data across reports
- Missing audit trails
- No standardization in risk tracking
- Difficulty in trend analysis

**Success Metrics:**
- 100% reporting consistency
- Complete audit trail for all reports
- Actionable insights from analytics

## 3.4 Platform Admin

**Role:** Configures and maintains the system

**Goals:**
- Manage LLM model keys and configurations
- Configure webhook endpoints for analytics
- Monitor system health and performance
- Manage deployment and versioning

**Pain Points:**
- Complex configurations
- Limited observability
- Difficulty in troubleshooting

**Success Metrics:**
- System uptime greater than 99.9%
- Quick deployment and rollback
- Complete observability

## 3.5 Risk Owner

**Role:** Manages specific risks assigned to them

**Goals:**
- Update risk status regularly
- Provide mitigation updates
- Close risks with proper documentation

**Pain Points:**
- No visibility into assigned risks
- Manual updates required
- No reminder for overdue risks

**Success Metrics:**
- Risks closed within target date
- Proper documentation for all closed risks

---

# 4. User Journey

## 4.1 Primary Flow

### Step 1: Login and Authentication
1. PM opens the enterprise web portal
2. PM enters email and password
3. System authenticates the user
4. Default page opens: Weekly Status Report creation

### Step 2: Account and Project Selection
1. PM selects an Account from dropdown (shows only mapped accounts)
2. System enables Project dropdown
3. PM selects a Project (shows only mapped projects)
3.1. PM selects the Project Execution Model from dropdown (one time activity after once selection it should show in disable mode) and there should show edit button. when user click on edit it should prompt user earlier you submitted data in the {selected Execution model}, change model will change the metrices.
3.2. System dynamically shows relevant metrics based on selection.
4. System updates breadcrumb with selected account and project
5. System displays a prefilled banner with previous approved week status report data

### Step 3: Data Entry
PM enters all required data including:
- Project Overview
- Delivery Metrics (model-specific) and remarks related to Metrics.
- Key Achievements this week.
- Risks and Dependencies with mandatory closure remarks multiline can be added.
- Next Week Plan. free text field
- Additional Notes.free text field

### Step 4 Generate WSR
1. PM clicks "Generate WSR" button
2. System performs validation checks
3. If validation passes:
   a. System orchestrates LangGraph agents
   b. Agents generate enhanced report content
   c. System generates AI Insights and Suggestions
   d. System creates Enhanced Draft for PM preview
4. If validation fails:
   a. System displays error messages
   b. PM must fix issues before retrying

### Step 5: Preview and Review
1. System displays Enhanced Draft with:
   - Generated report content (editable)
   - AI Insights (PM-only view) i.e Discrepancy detection alerts
   - AI Suggestions (PM-only view)
   - 
2. PM reviews all sections
3. PM can:
   - Edit generated content directly
   - Accept or reject AI suggestions by editing manually
   - Add comments for audit trail
   - Incorporate relevant insights

### Step 6: PM Approval
1. PM clicks "Approve" button
2. System records approval with timestamp and user
3. System stores final approved version
4. System saves audit trail of all changes

### Step 7: Export
1. Approved reports can be exported to PPTX
2. System generates export file
3. System records export in audit trail

## 4.2 AI Insights & Suggestions Flow

### Insight Generation
1. System analyzes PM-entered data:
   - Overall Status
   - Delivery metrics
   - Achievements
   - Risks
   - Plan
   - Historical trends

2. System identifies discrepancies:
   - Status vs. Delivery Metrics mismatch
   - Risks not properly documented. Like Mitigation not defined, owner missing, Planned Closer date is not added, Closer date is old then generated week etc.
   - Achievements without metrics
   - Plan items without clear ownership

3. System generates AI Insights:
   - Status Discrepancy: "PM reports Green but delivery completion is 62%. Consider updating status to Amber."
   - Risk Alert: "2 High severity risks require immediate attention."
   - Achievement Enhancement: "Add metrics to achievements for better impact."
   - Plan Optimization: "Consider prioritizing top 3 items."
   - Sentence improvements etc. but PM entered sentence should be base and no drastic changes.

### PM Review Process
1. PM reviews AI Insights in dedicated section
2. PM can:
   - Accept insight (by editing manually that particular section.
   - Ignore insight (for future reference)

3. All PM actions are recorded in audit trail:
   - PM comments on decisions
   - Timestamp of actions

## 4.3 Audit Trail Flow

### What is Captured
| Event Type | Data Captured | Purpose |
|------------|---------------|---------|
| Data Entry | All PM-entered fields | Baseline for analysis |
| Auto-Calculations | System-calculated values | Verify consistency |
| AI Generation | Draft content, insights, suggestions | Quality review |
| PM Edits | All content changes | Track improvements |
| PM Decisions | Approved, rejected, modified | Audit compliance |
| Risk Changes | Status transitions, remarks | Risk governance |
| Exports | File generation, download | Distribution tracking |

### Audit Trail Usage
1. **Compliance:** Verify all approvals documented
2. **Escalation Analysis:** Identify where communication failed
3. **Performance Review:** Track PM decision quality
4. **Training:** Identify areas for improvement
5. **Dispute Resolution:** Reconstruct decision history

---

# 5. Functional Requirements

## 5.1 Authentication and Authorization

### FR-AUTH-001: User Login
The system shall provide a login page with email and password fields.

### FR-AUTH-002: Session Management
The system shall maintain user session until logout or timeout.

### FR-AUTH-003: Authorization
The system shall enforce access control based on user role and project assignment.

### FR-AUTH-004: Account Mapping
The system shall display only accounts mapped to the logged-in user.

### FR-AUTH-005: Project Mapping
The system shall display only projects mapped to the selected account and user.

## 5.2 Account and Project Selection

### FR-ACC-001: Account Dropdown
The system shall display a dropdown of accounts mapped to the logged-in user.

### FR-ACC-002: Project Dropdown
The system shall display a dropdown of projects mapped to the selected account and user.

### FR-ACC-003: Project Dropdown Enablement
The system shall enable the Project dropdown only after an Account is selected.

### FR-ACC-004: Breadcrumb Update
The system shall update the breadcrumb with the selected account and project names.

### FR-ACC-005: Prefill Banner
The system shall display a banner showing data source for prefill.

## 5.3 Delivery Model Selection

### FR-MOD-001: Model Dropdown
The system shall provide a dropdown with delivery models.

### FR-MOD-002: Dynamic Metrics
The system shall display relevant metrics based on the selected delivery model.

### FR-MOD-003: Model-Specific Validation
The system shall apply validation rules specific to the selected model.

## 5.4 Delivery Metrics Entry

### FR-MET-001: Sprint Model Setup
The system shall capture Sprint Configuration.

### FR-MET-002: Sprint Lock Functionality
The system shall allow locking of Sprint Configuration.

### FR-MET-003: Sprint Weekly Entry
The system shall capture weekly sprint progress.

### FR-MET-004: Sprint Auto-Calculations
The system shall auto-calculate remaining metrics, completion percentage, and velocity.

### FR-MET-005: PI Model Setup
The system shall capture PI Configuration.

### FR-MET-006: PI Weekly Entry
The system shall capture weekly PI progress.

### FR-MET-007: PI Auto-Calculations
The system shall auto-calculate delivered scope, remaining scope, PI completion, and required velocity.

### FR-MET-008: Spillover Detection
The system shall detect and alert when spillover exists and requires remarks.

### FR-MET-009: Spillover Remarks
The system shall require remarks when spillover is greater than zero.

## 5.5 Key Achievements

### FR-ACH-001: Achievements List
The system shall display an editable list of achievements.

### FR-ACH-002: Add Achievement
The system shall allow adding new achievements.

### FR-ACH-003: Edit Achievement
The system shall allow editing existing achievements.

### FR-ACH-004: Delete Achievement
The system shall allow deleting achievements with confirmation.

### FR-ACH-005: Minimum Achievements
The system shall require a minimum of 3 achievements.

## 5.6 Risk Management

Risk Management requirements are detailed in [Section 6: Risk Management Module](#6-risk-management-module).

## 5.7 Next Week Plan

### FR-PLN-001: Plan List
The system shall display an editable list of next week plan items.

### FR-PLN-002: Add Plan Item
The system shall allow adding new plan items.

### FR-PLN-003: Edit Plan Item
The system shall allow editing existing plan items.

### FR-PLN-004: Delete Plan Item
The system shall allow deleting plan items with confirmation.

### FR-PLN-005: Minimum Plan Items
The system shall require a minimum of 3 plan items.

## 5.8 Additional Notes

### FR-NOT-001: Notes Field
The system shall provide an optional text area for additional PM notes.

## 5.9 Generate WSR

### FR-GEN-001: Generate Button
The system shall provide a "Generate WSR" button.

### FR-GEN-002: Validation Before Generation
The system shall validate all required fields before generation.

### FR-GEN-003: Validation Failure Handling
The system shall display validation errors and prevent generation.

### FR-GEN-004: Context Retrieval
The system shall retrieve relevant historical project context.

### FR-GEN-005: Enhanced Draft Generation
The system shall generate an enhanced draft with:
- Report content (editable sections)
- AI Insights (PM-only view)
- AI Suggestions (PM-only view)
- Discrepancy detection alerts

### FR-GEN-006: Progress Indicator
The system shall show progress during generation.

### FR-GEN-007: Generation Timeout
The system shall timeout generation after configured duration.

### FR-GEN-008: Enhanced Draft Storage
The system shall store the enhanced draft for PM review.

## 5.10 Preview and Review

### FR-PRV-001: Enhanced Draft Display
The system shall display the enhanced draft for PM review.

### FR-PRV-002: Editable Content
The system shall allow PM to edit generated content directly.

### FR-PRV-003: AI Insights Section
The system shall display AI Insights in a dedicated section.

### FR-PRV-004: AI Suggestions Section
The system shall display AI Suggestions in a dedicated section.

### FR-PRV-005: Discrepancy Alerts
The system shall display discrepancy detection alerts.

### FR-PRV-006: Insight Acceptance
The system shall allow PM to accept AI insights.

### FR-PRV-007: Insight Rejection
The system shall allow PM to reject AI insights with reason.

### FR-PRV-008: Insight Modification
The system shall allow PM to modify insights before acceptance.

### FR-PRV-009: Comment Addition
The system shall allow PM to add comments for audit trail.

## 5.11 PM Approval

### FR-APP-001: Approve Button
The system shall provide an "Approve" button.

### FR-APP-002: Approval Confirmation
The system shall require confirmation before final approval.

### FR-APP-003: Approval Recording
The system shall record approval with:
- Approver name
- Approval timestamp
- Approval status
- Final version of content

### FR-APP-004: Approve with Edits
The system shall support approval with edits.

### FR-APP-005: Reject
The system shall support rejection with feedback.

### FR-APP-006: Rejection Feedback
The system shall require rejection reason.

### FR-APP-007: Final Version Storage
The system shall store the final approved version.

## 5.12 Export

### FR-EXP-001: PPTX Export
The system shall generate PPTX export of approved reports.

### FR-EXP-002: Export Gate
The system shall disable export until human approval is recorded.

### FR-EXP-003: Customer-Safe Output
The system shall exclude AI Insights and Suggestions from customer-facing exports.

### FR-EXP-004: Export Tracking
The system shall track all export attempts.

## 5.13 AI Insights & Suggestions

### FR-AIS-001: Insight Types
The system shall generate the following insight types:
- Status Discrepancy Detection
- Risk Alert
- Achievement Enhancement
- Plan Optimization
- Metric Consistency Check
- Historical Trend Analysis

### FR-AIS-002: Insight Generation
The system shall generate insights based on:
- PM-entered data
- Delivery metrics
- Risk data
- Historical trends
- Best practices

### FR-AIS-003: Insight Display
The system shall display insights with:
- Clear description
- Severity indicator
- Recommended action
- Data evidence

### FR-AIS-004: PM Action Recording
The system shall record PM actions on insights:
- Accepted
- Rejected with reason
- Modified
- Ignored

### FR-AIS-005: Insight Storage
The system shall store all insights for audit.

### FR-AIS-006: Insight Exclusion from Export
The system shall exclude insights from customer-facing exports.

---

# 6. Risk Management Module

## 6.1 Module Overview

The Risk Management Module enables Project Managers to track, monitor, and manage project risks and dependencies throughout the project lifecycle. The module provides structured risk governance with mandatory validation rules to ensure data quality and proper risk closure documentation.

## 6.2 Risk Data Model

### 6.2.1 Risk Fields

| Field Name | Type | Required | Description | Validation Rules |
|------------|------|----------|-------------|------------------|
| Risk ID | Auto-generated | Yes | Unique identifier | System generated, sequential |
| Risk Description | Text | Yes | Clear description of the risk | Minimum 10 characters, no duplicates |
| Risk Status | Dropdown | Yes | Current status of the risk | Open, In-Progress, Closed |
| Severity | Dropdown | Yes | Impact level of the risk | High, Medium, Low |
| Risk Owner | Text | Yes | Person responsible for the risk | Minimum 2 characters, valid user |
| Risk Mitigation | Text | Yes | Plan to mitigate the risk | Minimum 10 characters |
| Planned Closure Date | Date | Yes | Target date for risk closure | Must be a future date |
| Remark | Text | Conditional | Additional notes about the risk | Mandatory when status is Closed, minimum 5 characters |
| Created At | Timestamp | Auto | Date and time of risk creation | System generated |
| Updated At | Timestamp | Auto | Date and time of last update | System generated |

### 6.2.2 Risk Status Definitions

| Status | Description | Color Code |
|--------|-------------|------------|
| Open | Risk has been identified but no action taken yet | Red |
| In-Progress | Risk is being actively managed | Amber/Yellow |
| Closed | Risk has been resolved or mitigated | Green |

### 6.2.3 Risk Severity Definitions

| Severity | Description | Examples | Color Code |
|----------|-------------|----------|------------|
| High | Significant impact on project timeline, budget, or quality | Production outage, data loss, compliance violation | Red |
| Medium | Moderate impact that can be managed with mitigation | Delivery delay, resource constraints | Amber/Yellow |
| Low | Minor impact with minimal effect on project | Minor bugs, documentation issues | Green |

### 6.2.4 Risk Status Transition Rules

| From Status | To Status | Allowed | Validation |
|-------------|-----------|---------|------------|
| Open | In-Progress | Yes | No validation required |
| Open | Closed | No | Must go through In-Progress first |
| In-Progress | Open | Yes | Can reopen if needed |
| In-Progress | Closed | Yes | Remark is mandatory |
| Closed | Open | No | Cannot reopen closed risks |
| Closed | In-Progress | No | Cannot reopen closed risks |

## 6.3 Risk Functional Requirements

### FR-RSK-001: Display Risk Table
The system shall display all risks in a tabular format with all required columns.

### FR-RSK-002: Add New Risk
The system shall provide an Add Risk button that opens a form with all required fields.

### FR-RSK-003: Remark Field Behavior
The system shall enforce mandatory remark when status is Closed.

### FR-RSK-004: Duplicate Prevention
The system shall prevent the creation of risks with duplicate descriptions.

### FR-RSK-005: Future Date Validation
The system shall enforce that the Planned Closure Date must be in the future.

### FR-RSK-006: Edit Risk
The system shall allow editing of all risk fields.

### FR-RSK-007: Status Change Validation
The system shall enforce status transition rules.

### FR-RSK-008: Delete Risk
The system shall allow deletion of risks with confirmation.

### FR-RSK-009: Load Risks from Previous WSR
The system shall provide functionality to load risks from the previous approved WSR.

### FR-RSK-010: Risk Summary
The system shall display a summary of risks.

### FR-RSK-011: Risk Validation Messages
The system shall display clear validation messages for all rules.

---

# 7. AI Insights & Suggestions Module

## 7.1 Module Overview

The AI Insights & Suggestions Module provides data-driven recommendations to PMs for improving report accuracy and completeness. Insights are generated based on analysis of PM-entered data, delivery metrics, risks, and historical trends. All insights are PM-only and excluded from customer-facing exports.

## 7.2 Insight Types

### 7.2.1 Status Discrepancy Detection

**Trigger:** PM reports Green but delivery metrics indicate risk

**Analysis Logic:**
```
IF PM_Status = 'Green' AND Completion_Percentage < 70% THEN
    Insight: "Status Discrepancy Detected"
    Severity: High
    Recommendation: "PM reports Green but delivery completion is [X]%. Consider updating status to Amber."
    Evidence: "Completion is [X]% based on [Planned - Completed] data"
```

**IF PM_Status = 'Green' AND High_Risks_Open > 0 THEN**
    Insight: "Risk Discrepancy Detected"
    Severity: High
    Recommendation: "PM reports Green but [X] high severity risks are open. Consider updating status to Amber."
    Evidence: "[X] high severity risks require attention"

**IF PM_Status = 'Green' AND Spillover > 20% THEN**
    Insight: "Delivery Discrepancy Detected"
    Severity: Medium
    Recommendation: "PM reports Green but spillover is [X]%. Consider providing recovery plan."
    Evidence: "[X] tasks spilled over from planned scope"

### 7.2.2 Risk Alert

**Trigger:** Risks require attention

**Analysis Logic:**
```
IF High_Risks_Open > 2 THEN
    Insight: "Multiple High Risks"
    Severity: High
    Recommendation: "[X] high severity risks require immediate attention."
    Evidence: "List of high risks: [Risk 1], [Risk 2]"

IF Risk_Aging > 30_Days THEN
    Insight: "Aging Risks"
    Severity: Medium
    Recommendation: "[X] risks have been open for more than 30 days. Consider escalating."
    Evidence: "Risks open since [Date]"

IF Risk_Closure_Date_Overdue THEN
    Insight: "Overdue Risks"
    Severity: High
    Recommendation: "[X] risks have passed planned closure date. Immediate action required."
    Evidence: "Risks overdue by [X] days"
```

### 7.2.3 Achievement Enhancement

**Trigger:** Achievements lack metrics or specificity

**Analysis Logic:**
```
IF Achievement_Without_Metrics THEN
    Insight: "Add Metrics to Achievements"
    Severity: Low
    Recommendation: "Achievement '[X]' lacks measurable metrics. Consider adding story points or impact."
    Evidence: "Achievement description does not contain numbers or metrics"

IF Achievement_Count < 3 THEN
    Insight: "More Achievements Needed"
    Severity: Medium
    Recommendation: "Only [X] achievements added. Consider adding more to show project progress."
    Evidence: "Minimum 3 achievements recommended"

IF Achievement_Description_Short THEN
    Insight: "Detail Achievements"
    Severity: Low
    Recommendation: "Achievement '[X]' is brief. Consider adding more details."
    Evidence: "Achievement is less than 20 characters"
```

### 7.2.4 Plan Optimization

**Trigger:** Plan items need prioritization or clarity

**Analysis Logic:**
```
IF Plan_Items > 5 THEN
    Insight: "Prioritize Plan Items"
    Severity: Low
    Recommendation: "You have [X] plan items. Consider prioritizing top 3-4 items."
    Evidence: "List of all plan items"

IF Plan_Items_Without_Ownership THEN
    Insight: "Assign Ownership"
    Severity: Medium
    Recommendation: "Plan items lack clear ownership. Consider assigning owners."
    Evidence: "Items without ownership: [Item 1], [Item 2]"

IF Plan_Items_Without_Deadline THEN
    Insight: "Add Deadlines"
    Severity: Low
    Recommendation: "Plan items lack deadlines. Consider adding target dates."
    Evidence: "Items without dates: [Item 1], [Item 2]"
```

### 7.2.5 Metric Consistency Check

**Trigger:** Inconsistent or incomplete metrics

**Analysis Logic:**
```
IF Completed > Planned THEN
    Insight: "Metric Inconsistency"
    Severity: High
    Recommendation: "Completed tasks ([X]) exceed planned tasks ([Y]). Please verify."
    Evidence: "Data inconsistency detected"

IF Spillover_Without_Remarks THEN
    Insight: "Missing Spillover Remarks"
    Severity: High
    Recommendation: "Spillover detected ([X] tasks) but no remarks provided."
    Evidence: "Remarks field is empty"

IF Velocity_Declining THEN
    Insight: "Declining Velocity"
    Severity: Medium
    Recommendation: "Velocity has declined from [X] to [Y]. Consider investigating causes."
    Evidence: "3-week trend: [Week1], [Week2], [Week3]"
```

### 7.2.6 Historical Trend Analysis

**Trigger:** Patterns detected in historical data

**Analysis Logic:**
```
IF Status_Changing_Frequently THEN
    Insight: "Unstable Status"
    Severity: Medium
    Recommendation: "Status has changed [X] times in last 4 weeks. Consider stabilizing."
    Evidence: "Status trend: [Week1], [Week2], [Week3], [Week4]"

IF Risks_Increasing THEN
    Insight: "Increasing Risk Trend"
    Severity: High
    Recommendation: "Risks have increased from [X] to [Y] in last 4 weeks. Review risk management."
    Evidence: "Risk trend: [Week1], [Week2], [Week3], [Week4]"

IF Achievements_Consistent THEN
    Insight: "Consistent Achievement Pattern"
    Severity: Low
    Recommendation: "You consistently deliver [X] story points per week. Good consistency."
    Evidence: "4-week achievement trend: [Week1], [Week2], [Week3], [Week4]"
```

## 7.3 Insight Format

### 7.3.1 Display Format

Each insight shall be displayed with:
1. **Severity Indicator:** High, Medium, Low
2. **Type:** Category of insight
3. **Description:** Clear explanation of the issue
4. **Evidence:** Data supporting the insight
5. **Recommendation:** Suggested action for PM
6. **Action Buttons:** Accept, Reject, Modify

### 7.3.2 Insight UI Layout

```
+--------------------------------------------------+
|  🔍 AI Insights & Suggestions                    |
|  (PM-Only - Not included in exports)             |
+--------------------------------------------------+
|  🔴 High: Status Discrepancy Detected            |
|  ──────────────────────────────────────────────────|
|  PM reports Green but delivery completion is 62% |
|                                                    |
|  Evidence: Completion based on planned vs         |
|  completed tasks.                                 |
|                                                    |
|  Recommendation: Consider updating status to      |
|  Amber and provide recovery plan.                |
|                                                    |
|  [Accept] [Reject] [Modify]                      |
+--------------------------------------------------+
|  🟡 Medium: Risk Alert - 2 High Severity Risks   |
|  ──────────────────────────────────────────────────|
|  2 high severity risks require immediate          |
|  attention.                                       |
|                                                    |
|  Evidence: Payment Gateway Issues, SSL           |
|  Certificate Expiry                               |
|                                                    |
|  Recommendation: Review mitigation plans and      |
|  escalate if needed.                             |
|                                                    |
|  [Accept] [Reject] [Modify]                      |
+--------------------------------------------------+
```

## 7.4 PM Action Recording

### 7.4.1 Action Types

| Action | Description | Audit Data |
|--------|-------------|------------|
| Accept | PM accepts insight and applies to report | Insight ID, PM, Timestamp |
| Reject | PM rejects insight with reason | Insight ID, PM, Reason, Timestamp |
| Modify | PM modifies insight before accepting | Original Insight, Modified Version, PM, Timestamp |
| Ignore | PM ignores insight (no immediate action) | Insight ID, PM, Timestamp |

### 7.4.2 Audit Trail for Insights

Each insight action shall be stored with:
- Insight ID
- PM User ID
- Action Type
- Action Timestamp
- Reason (for Reject)
- Modified Content (for Modify)
- Final Report Version (if accepted)

---

# 8. Audit Trail Module

## 8.1 Module Overview

The Audit Trail Module captures and stores all actions, changes, and decisions made during the WSR lifecycle. This provides complete traceability for compliance, escalation analysis, and performance review.

## 8.2 Audit Events

### 8.2.1 Data Entry Events

| Event | Data Captured | Purpose |
|-------|---------------|---------|
| PM Data Entry | All field values entered by PM | Baseline for analysis |
| Auto-Calculation | System-calculated values | Verify consistency |
| Save Draft | Draft version with timestamp | Track progress |
| Field Changes | Before/After values | Track modifications |

### 8.2.2 AI Generation Events

| Event | Data Captured | Purpose |
|-------|---------------|---------|
| Generation Request | PM, Timestamp, Input Data | Track generation |
| AI Draft | Generated content | Quality review |
| AI Insights | Generated insights | Track recommendations |
| AI Suggestions | Generated suggestions | Track recommendations |
| QA Score | Quality score and feedback | Quality measurement |

### 8.2.3 PM Review Events

| Event | Data Captured | Purpose |
|-------|---------------|---------|
| Content Edits | Before/After values | Track changes |
| Insight Acceptance | Insight ID, PM, Timestamp | Track decisions |
| Insight Rejection | Insight ID, PM, Reason, Timestamp | Track decisions |
| Insight Modification | Original, Modified, PM, Timestamp | Track improvements |
| Comments Added | Comment text, PM, Timestamp | Additional context |

### 8.2.4 Approval Events

| Event | Data Captured | Purpose |
|-------|---------------|---------|
| Approve | PM, Timestamp, Final Content | Approval proof |
| Approve with Edits | PM, Edits, Timestamp | Approval with changes |
| Reject | PM, Reason, Timestamp | Rejection proof |

### 8.2.5 Export Events

| Event | Data Captured | Purpose |
|-------|---------------|---------|
| Export Request | PM, Format, Timestamp | Export tracking |
| Export Success | File ID, Location, Timestamp | Export proof |
| Export Failure | Error, Timestamp | Troubleshooting |

## 8.3 Audit Trail Storage

### 8.3.1 Core Audit Table

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| wsr_id | UUID | Associated WSR |
| user_id | UUID | User who performed action |
| event_type | VARCHAR(50) | Type of event |
| action | VARCHAR(50) | Specific action |
| before_data | JSONB | Data before change |
| after_data | JSONB | Data after change |
| metadata | JSONB | Additional context |
| created_at | TIMESTAMP | Event timestamp |

### 8.3.2 Insight Audit Table

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| wsr_id | UUID | Associated WSR |
| insight_id | UUID | Insight identifier |
| insight_type | VARCHAR(50) | Type of insight |
| severity | VARCHAR(20) | High, Medium, Low |
| description | TEXT | Insight description |
| evidence | TEXT | Supporting data |
| recommendation | TEXT | Suggested action |
| pm_action | VARCHAR(20) | Accept, Reject, Modify, Ignore |
| pm_reason | TEXT | Reason for action |
| modified_content | TEXT | Modified insight (if applicable) |
| created_at | TIMESTAMP | Insight creation |
| updated_at | TIMESTAMP | Last update |

## 8.4 Audit Trail Usage

### 8.4.1 Compliance Reporting
- Verify all approvals documented
- Confirm export gates enforced
- Validate risk closure remarks

### 8.4.2 Escalation Analysis
- Identify where communication failed
- Reconstruct decision history
- Pinpoint missing warnings

### 8.4.3 Performance Review
- Track PM decision quality
- Measure insight acceptance rate
- Identify training needs

### 8.4.4 Dispute Resolution
- Reconstruct full history
- Verify data integrity
- Provide evidence trail

---

# 9. Non-Functional Requirements

## 9.1 Performance

| Metric | Target |
|--------|--------|
| Prefill API Response | Less than 1 second |
| Generation Time | Less than 30 seconds |
| Insight Generation | Less than 5 seconds |
| Dashboard Load Time | Less than 3 seconds |
| Risk Table Load Time | Less than 2 seconds |
| Concurrent Users | 100 PMs daily |
| UI Responsiveness | Less than 200ms |
| Export Download Time | Less than 5 seconds |

## 9.2 Reliability

- Model failures surface clear user-facing errors
- Graceful degradation when services unavailable
- Retry logic with idempotency for exports
- State persistence for recovery
- Data cutoff consistently applied
- Discrepancy detection real-time

## 9.3 Security

- Secrets in .env or managed secret stores
- No secrets in code or logs
- Server-side authorization on every request
- Account and project isolation for all data
- Insights and suggestions PM-only
- Audit trail secured from unauthorized access

## 9.4 Data Management

- All records include account_id and project_id
- Audit logs for all actions
- Retention policies for drafts, checkpoints, exports
- Rejected reports archived or deleted based on policy
- Insight data retained for audit
- Data cutoff auditable and consistent

## 9.5 Observability

- Correlation IDs for all workflows
- Structured logging for:
  - Generation stages
  - LLM calls
  - Validation failures
  - Persistence actions
  - Export attempts
  - Approval events
  - Insight generation
  - Audit trail writes
- Fallback behavior explicit in logs

## 9.6 Maintainability

- Modular agent architecture
- Single responsibility principle
- DRY across calculations
- Prompts versioned and testable
- Utility functions for common operations
- Pytest unit tests for all rules
- Insight generation logic testable

## 9.7 Compliance

- PPTX exports require recorded human approval
- Customer-safe output (insights excluded)
- Audit trail for all actions
- Remark mandatory for risk closure
- Insight decisions recorded for audit

---

# 10. Technical Architecture

## 10.1 Technology Stack

| Layer | Technology | Version |
|-------|------------|---------|
| Frontend | React + TypeScript | 19.x / 5.9 |
| Build Tool | Vite | 7.x |
| Backend | Python + FastAPI | 3.12 / 0.115+ |
| Workflow | LangGraph | 1.0+ |
| LLM Framework | LangChain | 1.0+ |
| LLM Providers | DeepSeek, Groq | Configurable |
| Database | PostgreSQL + pgvector | 16+ |
| Cache | Redis | 7.0+ |
| File Storage | S3/MinIO | - |
| Export | python-pptx | - |

## 10.2 Architecture Layers

```
+--------------------------------------------------+
|              PRESENTATION LAYER                    |
|  React UI -> WsrCreationPage -> Login Page        |
|  AI Insights Display -> Audit Trail View          |
+--------------------------------------------------+
|                        |                           |
+--------------------------------------------------+
|                   API LAYER                        |
|  FastAPI Routes -> Authentication                 |
|  Authorization -> Request Validation              |
+--------------------------------------------------+
|                        |                           |
+--------------------------------------------------+
|               APPLICATION LAYER                    |
|  WSR Services -> Orchestrator                     |
|  Insight Service -> Audit Service                 |
|  Repository Facade -> Validation Service          |
+--------------------------------------------------+
|                        |                           |
+--------------------------------------------------+
|                WORKFLOW LAYER                      |
|  LangGraph Orchestration -> Nodes                 |
|  Agents -> Review Loop -> Insight Generation      |
+--------------------------------------------------+
|                        |                           |
+--------------------------------------------------+
|                 DOMAIN LAYER                       |
|  Delivery Intelligence -> Risk Rules              |
|  Insight Rules -> Audit Rules                     |
|  Semantic Roles -> Rule Engine                    |
+--------------------------------------------------+
|                        |                           |
+--------------------------------------------------+
|               PERSISTENCE LAYER                    |
|  PostgreSQL Repositories -> Audit Logs            |
|  Redis Cache -> Export Store -> Insight Store     |
+--------------------------------------------------+
```

## 10.3 Workflow Graph

```
Input -> Validate -> Route Model -> Analyze Model -> Analyze Delivery/Risk/Quality
                         |
                         v
                   Write Sections
                         |
                         v
              +---------+---------+
              |  Generate Insights |
              +---------+---------+
                         |
                         v
              +---------+---------+
              |  QA Loop          |<-----+
              +---------+---------+      |
                        |                  |
                   Score >= 0.8?         |
                  /         \            |
               Yes           No----------+
                 |
                 v
        +--------+--------+
        |  PM Preview     |
        |  - Edit Content |
        |  - Review AI    |
        |    Insights     |
        |  - Accept/Reject|
        +--------+--------+
                 |
                 v
          PM Approval
                 |
        +--------+--------+
        |        |        |
   Approve   Reject  Edit
        |        |        |
        +--------+--------+
                 |
                 v
          Export & Publish
```

## 10.4 Insight Generation Flow

```
+--------------------------------------------------+
|              INSIGHT GENERATION FLOW               |
+--------------------------------------------------+
|                                                    |
|  1. Data Collection                                |
|     - PM-entered data                             |
|     - Delivery metrics                            |
|     - Risk data                                   |
|     - Historical trends                           |
|                                                    |
|  2. Rule Analysis                                 |
|     - Status vs Metrics comparison                |
|     - Risk assessment                             |
|     - Achievement quality                         |
|     - Plan completeness                           |
|                                                    |
|  3. Pattern Detection                             |
|     - Trends identification                       |
|     - Anomaly detection                           |
|     - Pattern recognition                         |
|                                                    |
|  4. Insight Generation                            |
|     - Status discrepancy alerts                   |
|     - Risk recommendations                        |
|     - Achievement enhancements                    |
|     - Plan optimizations                          |
|                                                    |
|  5. PM Review                                     |
|     - Accept / Reject / Modify                    |
|     - Record decision for audit                   |
|                                                    |
|  6. Storage                                       |
|     - Insight data stored                         |
|     - PM actions recorded                         |
|     - Audit trail updated                         |
|                                                    |
+--------------------------------------------------+
```

---

# 11. Data Model

## 11.1 Core Tables

### 11.1.1 Accounts Table

```sql
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 11.1.2 Projects Table

```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    delivery_model VARCHAR(50) NOT NULL,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 11.1.3 WSR Reports Table

```sql
CREATE TABLE wsr_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    reporting_week DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    tracking_model VARCHAR(50) NOT NULL,
    model_payload JSONB NOT NULL DEFAULT '{}',
    model_metrics JSONB NOT NULL DEFAULT '{}',
    model_findings JSONB NOT NULL DEFAULT '[]',
    overall_status VARCHAR(10) NOT NULL,
    release_milestone VARCHAR(255),
    pm_highlights TEXT,
    pm_next_plan TEXT,
    pm_notes TEXT,
    ai_executive_summary TEXT,
    ai_risk_analysis TEXT,
    ai_next_week TEXT,
    ai_qa_score DECIMAL(3,2),
    ai_qa_feedback TEXT,
    approval_status VARCHAR(20) DEFAULT 'pending',
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP,
    exported_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT check_overall_status CHECK (overall_status IN ('Green', 'Amber', 'Red')),
    CONSTRAINT check_approval_status CHECK (approval_status IN ('draft', 'pending', 'approved', 'rejected'))
);
```

### 11.1.4 Risks Table

```sql
CREATE TABLE risks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wsr_id UUID NOT NULL REFERENCES wsr_reports(id) ON DELETE CASCADE,
    risk_id VARCHAR(10) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) NOT NULL,
    severity VARCHAR(10) NOT NULL,
    owner VARCHAR(100) NOT NULL,
    mitigation TEXT NOT NULL,
    planned_closure_date DATE NOT NULL,
    remark TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT check_status CHECK (status IN ('Open', 'In-Progress', 'Closed')),
    CONSTRAINT check_severity CHECK (severity IN ('High', 'Medium', 'Low')),
    CONSTRAINT check_description_length CHECK (char_length(description) >= 10),
    CONSTRAINT check_owner_length CHECK (char_length(owner) >= 2),
    CONSTRAINT check_mitigation_length CHECK (char_length(mitigation) >= 10),
    CONSTRAINT check_remark_for_closed 
        CHECK (status != 'Closed' OR (status = 'Closed' AND remark IS NOT NULL AND char_length(remark) >= 5)),
    CONSTRAINT check_closure_date_future CHECK (planned_closure_date >= CURRENT_DATE)
);

CREATE UNIQUE INDEX idx_risks_wsr_description ON risks(wsr_id, description);
CREATE INDEX idx_risks_wsr_id ON risks(wsr_id);
CREATE INDEX idx_risks_status ON risks(status);
CREATE INDEX idx_risks_severity ON risks(severity);
```

### 11.1.5 AI Insights Table

```sql
CREATE TABLE ai_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wsr_id UUID NOT NULL REFERENCES wsr_reports(id) ON DELETE CASCADE,
    insight_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    description TEXT NOT NULL,
    evidence TEXT,
    recommendation TEXT NOT NULL,
    pm_action VARCHAR(20),
    pm_reason TEXT,
    modified_content TEXT,
    accepted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_insights_wsr_id ON ai_insights(wsr_id);
CREATE INDEX idx_ai_insights_type ON ai_insights(insight_type);
CREATE INDEX idx_ai_insights_severity ON ai_insights(severity);
```

### 11.1.6 Audit Logs Table

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wsr_id UUID NOT NULL REFERENCES wsr_reports(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    before_data JSONB,
    after_data JSONB,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_wsr_id ON audit_logs(wsr_id);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_event_type ON audit_logs(event_type);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
```

### 11.1.7 Approval Events Table

```sql
CREATE TABLE approval_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wsr_id UUID NOT NULL REFERENCES wsr_reports(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    action VARCHAR(20) NOT NULL,
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 11.1.8 Export Attempts Table

```sql
CREATE TABLE export_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wsr_id UUID NOT NULL REFERENCES wsr_reports(id) ON DELETE CASCADE,
    format VARCHAR(10) NOT NULL,
    status VARCHAR(20) NOT NULL,
    file_path VARCHAR(500),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
```

## 11.2 Entity Relationship Diagram

```
+----------+     +----------+     +-------------+
| Accounts |<----| Projects |<----| WSR Reports |
+----------+     +----------+     +-------------+
                                           |
                                           |
                      +--------------------+--------------------+
                      |                    |                    |
                      v                    v                    v
                +----------+     +------------------+  +--------------+
                |  Risks   |     | Delivery Metrics |  | AI Insights  |
                +----------+     +------------------+  +--------------+
                      |                    |                    |
                      +--------------------+--------------------+
                                           |
                                           v
                                    +-------------+
                                    | Audit Logs  |
                                    +-------------+
```

---

# 12. Validation Rules

## 12.1 Field Level Validation

| Field | Validation Rule | Error Message |
|-------|----------------|---------------|
| Account | Must be selected | "Please select an account" |
| Project | Must be selected | "Please select a project" |
| Delivery Model | Must be selected | "Please select a delivery model" |
| Overall Status | Must be valid value | "Overall status is required" |
| Risk Description | Required, min 10 chars | "Risk description required (min 10 characters)" |
| Risk Status | Required | "Risk status is required" |
| Risk Severity | Required | "Risk severity is required" |
| Risk Owner | Required, min 2 chars | "Risk owner required (min 2 characters)" |
| Risk Mitigation | Required, min 10 chars | "Risk mitigation required (min 10 characters)" |
| Planned Closure Date | Required, future date | "Planned closure date required and must be future" |
| Remark | Mandatory when Closed | "Remark mandatory when risk is Closed" |

## 12.2 Business Rule Validation

| Rule ID | Description | Validation Logic |
|---------|-------------|------------------|
| BR-001 | Spillover Remarks | Spillover > 0 requires remarks |
| BR-002 | Risk Status Transition | Open to Closed not allowed |
| BR-003 | Remark on Risk Closure | Status = Closed requires remark |
| BR-004 | Reopen Closed Risks | Closed risks cannot be reopened |
| BR-005 | Duplicate Risk Descriptions | No duplicates within WSR |
| BR-006 | Future Date | Planned Closure Date must be future |
| BR-007 | Minimum Achievements | At least 3 achievements required |
| BR-008 | Minimum Plan Items | At least 3 plan items required |

## 12.3 Cross-Field Validation

| Rule ID | Description | Validation Logic |
|---------|-------------|------------------|
| CR-001 | Risk Data Completeness | All mandatory fields filled |
| CR-002 | Sprint Date Validity | Start date before end date |
| CR-003 | PI Sprint Validity | Current sprint <= Total sprints |
| CR-004 | Completed <= Planned | Completed tasks <= Planned tasks |
| CR-005 | High Risk Requirements | High risk requires owner, mitigation, date |

---

# 13. Implementation Roadmap

## Phase 1: Core Infrastructure (Week 1-2)

| Task | Description | Priority |
|------|-------------|----------|
| Database Setup | PostgreSQL schema creation | High |
| Authentication | Login and session management | High |
| Account/Project Selection | Dynamic dropdowns with mapping | High |
| Delivery Model Selection | Model dropdown with options | High |

## Phase 2: Delivery Metrics (Week 2-3)

| Task | Description | Priority |
|------|-------------|----------|
| Sprint Model | Complete sprint metrics with auto-calculations | High |
| PI Model | Complete PI metrics with auto-calculations | High |
| Other Models | Kanban, Support, Infrastructure, POC | High |

## Phase 3: Risk Management (Week 3-4)

| Task | Description | Priority |
|------|-------------|----------|
| Risk Data Model | Database schema for risks | High |
| Risk CRUD | Create, read, update, delete | High |
| Risk Validation | All validation rules implemented | High |
| Remark on Closure | Mandatory remark for closed risks | High |

## Phase 4: AI Generation (Week 4-5)

| Task | Description | Priority |
|------|-------------|----------|
| LangGraph Setup | Workflow orchestration | High |
| Agent Implementation | Summary, risk, plan agents | High |
| QA Review | Scoring and feedback loop | High |
| Generation UI | Progress indicator | High |

## Phase 5: AI Insights & Suggestions (Week 5-6)

| Task | Description | Priority |
|------|-------------|----------|
| Insight Rules Engine | Define all insight rules | High |
| Status Discrepancy Detection | Green vs metrics comparison | High |
| Risk Alert Generation | Risk-based insights | High |
| Achievement Enhancement | Achievement quality insights | High |
| Plan Optimization | Plan completeness insights | High |
| Insight UI | Display and action interface | High |
| Insight Storage | Database for insights | High |

## Phase 6: PM Review & Approval (Week 6-7)

| Task | Description | Priority |
|------|-------------|----------|
| Enhanced Draft Display | Edit and preview UI | High |
| Insight Action Recording | Accept/Reject/Modify | High |
| Approval Workflow | Approve, Approve with Edits, Reject | High |
| Audit Trail | All actions recorded | High |

## Phase 7: Export & Dashboard (Week 7-8)

| Task | Description | Priority |
|------|-------------|----------|
| PPTX Export | Native PowerPoint generation | High |
| Executive Dashboard | Data-driven project health | High |
| Discrepancy Detection | PM vs Reality comparison | High |

## Phase 8: Testing & Deployment (Week 8-9)

| Task | Description | Priority |
|------|-------------|----------|
| Unit Tests | Pytest for backend | High |
| Integration Tests | API end-to-end | High |
| E2E Tests | Full user journey | High |
| Deployment | Production deployment | High |

---

# 14. Success Metrics

## 14.1 Primary Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| PM Drafting Time Reduction | 50% | Compare time from start to approval vs. manual |
| Prefill API Response Time | < 1 second | 95th percentile |
| Reports Validated Before Generation | 100% | Validation blocks invalid submissions |
| Drafts Passing QA in 2 Attempts | 80% | QA score >= 0.8 threshold |
| Approved Reports Exported | 100% | No export without approval |
| Cross-Account Retrieval Incidents | 0 | Audit logs and security monitoring |

## 14.2 AI Insights Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Insight Accuracy | > 90% | Insights correctly identifying issues |
| Insight Acceptance Rate | > 75% | PMs accepting AI insights |
| Status Discrepancy Detection | 100% | All discrepancies flagged |
| Risk Alert Accuracy | > 95% | Correctly identifying critical risks |
| PM Action Recording | 100% | All insight actions recorded |

## 14.3 Audit Trail Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Event Capture Rate | 100% | All actions audited |
| Audit Trail Completeness | 100% | All required fields captured |
| Export Tracking | 100% | All exports logged |
| Compliance Reporting | 100% | All approvals documented |

## 14.4 Quality Metrics

| Metric | Target |
|--------|--------|
| Data consistency across UI/backend | 100% |
| Prompt version audit coverage | 100% |
| Unit test coverage for rules | > 90% |
| Export success rate | > 99% |
| API availability | > 99.9% |
| Risk completeness | 100% |
| Remark compliance on risk closure | 100% |

---

# 15. Open Questions

## 15.1 Technical Questions

| Question | Status | Owner |
|----------|--------|-------|
| Which portal API provides assigned accounts? | Open | Product |
| Which portal API provides assigned projects? | Open | Product |
| Which service validates project belongs to account? | Open | Product |
| Is PostgreSQL acceptable as production database? | In Progress | Architecture |

## 15.2 Business Questions

| Question | Status | Owner |
|----------|--------|-------|
| Who can approve final WSRs: PM only or manager? | Decided (PM only) | Product |
| What retention period for drafts and exports? | Open | Product |
| Should rejected reports be archived or deleted? | Open | Product |
| Maximum number of risks per WSR? | Open | Product |
| Should risk owners receive notifications? | Open | Product |

## 15.3 Policy Questions

| Question | Status | Owner |
|----------|--------|-------|
| Vector retrieval scope (same project vs. same account)? | Open | Product |
| Customer-safe status controls? | In Progress | Product |
| Risk escalation workflow? | Open | Product |

---

# 16. Appendices

## Appendix A: Key Terminology

| Term | Definition |
|------|------------|
| WSR | Weekly Status Report |
| PM | Project Manager |
| AI Insight | Data-driven recommendation for PM review |
| AI Suggestion | Specific action recommendation |
| Enhanced Draft | AI-generated report with insights for PM review |
| Discrepancy | Difference between PM-reported and actual status |
| Audit Trail | Complete record of all actions and changes |
| Risk Status | Open, In-Progress, Closed |
| Risk Severity | High, Medium, Low |
| Remark | Additional notes, mandatory when closing risks |

## Appendix B: Insight Types Summary

| Insight Type | Trigger | Severity | Action |
|--------------|---------|----------|--------|
| Status Discrepancy | Green status with low completion | High | Update status |
| Risk Alert | Multiple high risks | High | Review mitigation |
| Achievement Enhancement | Achievements without metrics | Low | Add metrics |
| Plan Optimization | Too many plan items | Low | Prioritize |
| Metric Consistency | Inconsistent data | High | Verify data |
| Historical Trend | Pattern detection | Medium | Investigate |

## Appendix C: Audit Event Types

| Event Category | Event Types | Purpose |
|----------------|-------------|---------|
| Data Entry | Field changes, saves | Track PM input |
| AI Generation | Draft creation, insights | Track AI output |
| PM Review | Edits, comments | Track PM decisions |
| Approval | Approve, Reject | Track approval |
| Export | Export request, success | Track distribution |

---

# 17. Document Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-29 | Product Team | Initial document creation |
| 2.0 | 2026-06-21 | Product Team | Added Risk Management Module, updated validation rules |
| 3.0 | 2026-06-21 | Product Team | Added AI Insights & Suggestions Module, Audit Trail Module, Enhanced Draft flow |

---

**Document Owner:** Product Delivery Intelligence Team  
**Status:** Active  
**Last Updated:** 2026-06-21  
**Next Review:** 2026-07-21  
**Confidentiality:** Internal Use Only

---

*This document supersedes all previous versions. For questions or clarifications, contact the Product Delivery Intelligence team.*