import {
  ActionBar,
  FormSection,
  MetricCard,
  SelectField,
  StatusBadge,
  TextareaField,
  TextInputField,
} from "./FormPrimitives";
import { RiskGrid } from "./RiskGrid";

export function WsrFormShell() {
  return (
    <main className="wsr-page">
      <header className="wsr-header">
        <div>
          <p className="wsr-header__crumb">Weekly reports / New WSR</p>
          <h1>Create weekly status report</h1>
          <p className="wsr-header__meta">
            Week of Jun 23 - Jun 27, 2025 · Last saved 14 min ago
          </p>
        </div>
        <div className="wsr-header__actions" aria-label="Report actions">
          <StatusBadge label="Draft" tone="warning" />
          <button className="button button--secondary" type="button">
            Preview
          </button>
          <button className="button button--secondary" type="button">
            History
          </button>
        </div>
      </header>

      <div className="prefill-alert" role="status">
        Previous week data prefilled. Review and update before submitting.
      </div>

      <form className="wsr-form" aria-label="Weekly status report form">
        <FormSection
          step={1}
          title="Account and project"
          subtitle="Select the account and project for this report"
          badgeLabel="Required"
          badgeTone="info"
        >
          <div className="field-grid field-grid--four">
            <SelectField
              id="account"
              label="Account"
              options={["TechCorp Inc."]}
              required
              value="TechCorp Inc."
            />
            <SelectField
              id="project"
              label="Project"
              options={["TechCorp Portal Revamp"]}
              required
              value="TechCorp Portal Revamp"
            />
            <TextInputField id="reporting-week" label="WSR date" required value="2025-06-27" />
            <TextInputField id="prepared-by" label="Prepared by" required value="Arjun Kapoor" />
          </div>
        </FormSection>

        <FormSection
          step={2}
          title="Delivery model"
          subtitle="Model selection controls visible fields and validation"
          badgeLabel="Sprint based"
          badgeTone="info"
        >
          <div className="model-row">
            <SelectField
              id="delivery-model"
              label="Delivery model"
              options={["Sprint based", "PI based"]}
              required
              value="Sprint based"
            />
            <p className="model-row__summary">
              Sprint-based reporting captures sprint dates, planned scope, completed scope,
              spillover, effort, and RAG status.
            </p>
          </div>
        </FormSection>

        <FormSection
          step={3}
          title="Sprint setup"
          subtitle="Sprint 14 · Jun 23 - Jul 4"
          badgeLabel="Prefilled"
          badgeTone="success"
        >
          <div className="field-grid field-grid--five">
            <TextInputField id="sprint-name" label="Sprint name / number" required value="Sprint 14" />
            <TextInputField id="start-date" label="Start date" required value="2025-06-23" />
            <TextInputField id="end-date" label="End date" required value="2025-07-04" />
            <TextInputField id="planned-stories" label="Planned stories" value="18" />
            <TextInputField id="planned-points" label="Planned story points" value="70" />
            <TextInputField id="planned-effort" label="Planned effort (hrs)" value="160" />
            <TextInputField id="dor" label="DOR %" value="85" />
          </div>
        </FormSection>

        <FormSection
          step={4}
          title="Delivery progress"
          subtitle="Current week actuals and customer-safe progress narrative"
          badgeLabel="RAG: Amber"
          badgeTone="warning"
        >
          <TextareaField
            id="progress-update"
            label="High-level progress update"
            required
            rows={4}
            value="Authentication module completed and API integration progressed with controlled mitigation for vendor documentation dependency."
          />
          <div className="metric-grid" aria-label="Calculated delivery metrics">
            <MetricCard label="Story completion" value="67%" caption="12 of 18 planned stories" />
            <MetricCard label="Story points" value="48 / 70" caption="22 points remaining" />
            <MetricCard label="Effort usage" value="60%" caption="96 of 160 hours burned" />
            <MetricCard label="DOR adherence" value="85%" caption="Healthy readiness" />
          </div>
          <div className="field-grid field-grid--five">
            <TextInputField id="stories-completed" label="Stories completed" value="12" />
            <TextInputField id="points-completed" label="Story points completed" value="48" />
            <TextInputField id="effort-burned" label="Effort burned (hrs)" value="96" />
            <TextInputField id="unplanned-stories" label="Unplanned stories" value="2" />
            <SelectField
              id="rag-status"
              label="Overall RAG status"
              options={["Green", "Amber", "Red"]}
              required
              value="Amber"
            />
          </div>
        </FormSection>

        <FormSection
          step={5}
          title="Risks and dependencies"
          subtitle="Risks remain part of this WSR and do not become a separate tracker"
          badgeLabel="1 high"
          badgeTone="danger"
        >
          <RiskGrid />
        </FormSection>

        <FormSection
          step={6}
          title="Narrative details"
          subtitle="Business context used for AI generation and customer-ready drafting"
          badgeLabel="Required"
          badgeTone="info"
        >
          <div className="field-grid field-grid--two">
            <TextareaField
              id="overview"
              label="Project overview"
              required
              value="Portal revamp sprint delivery is controlled with manageable integration risk."
            />
            <TextareaField
              id="achievements"
              label="Key achievements"
              required
              value={"- Authentication module completed\n- API integration baseline established\n- Sprint dependency mitigation confirmed"}
            />
            <TextareaField
              id="next-week-focus"
              label="Next week focus and actions"
              required
              value={"- Complete integration validation; Owner: Priya; Target: Tue\n- Review dashboard API contract; Owner: Arjun; Target: Wed\n- Prepare sprint closure note; Owner: Neha; Target: Fri"}
            />
            <TextareaField
              id="remarks"
              label="Remarks / notes"
              value="Delivery remains under active control with clear ownership for the integration dependency."
            />
          </div>
        </FormSection>

        <ActionBar>
          <button className="button button--secondary" type="button">
            Save draft
          </button>
          <button className="button button--secondary" type="button">
            Validate
          </button>
          <button className="button button--primary" type="button">
            Generate WSR
          </button>
        </ActionBar>
      </form>
    </main>
  );
}
