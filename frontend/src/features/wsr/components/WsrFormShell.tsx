import { useMemo, useState } from "react";

import type { DeliveryModel } from "../types/wsr.types";
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

type WsrFormShellProps = {
  initialDeliveryModel?: DeliveryModel;
};

const deliveryModelLabels: Record<DeliveryModel, string> = {
  SPRINT: "Sprint based",
  PI: "PI based",
};

export function WsrFormShell({ initialDeliveryModel = "SPRINT" }: WsrFormShellProps) {
  const [deliveryModel, setDeliveryModel] = useState<DeliveryModel>(initialDeliveryModel);
  const deliveryMetrics = useMemo(() => calculateModelMetrics(deliveryModel), [deliveryModel]);

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
          badgeLabel={deliveryModelLabels[deliveryModel]}
          badgeTone="info"
        >
          <div className="model-row">
            <SelectField
              id="delivery-model"
              label="Delivery model"
              options={["Sprint based", "PI based"]}
              required
              value={deliveryModelLabels[deliveryModel]}
              onChange={(value) => {
                setDeliveryModel(value === "PI based" ? "PI" : "SPRINT");
              }}
            />
            <p className="model-row__summary">
              {deliveryModel === "SPRINT"
                ? "Sprint-based reporting captures sprint dates, planned scope, completed scope, spillover, effort, and RAG status."
                : "PI-based reporting captures PI dates, total scope, delivered scope, current sprint, remaining scope, velocity, and confidence."}
            </p>
          </div>
        </FormSection>

        {deliveryModel === "SPRINT" ? <SprintSetupSection /> : <PiSetupSection />}

        <FormSection
          step={4}
          title="Delivery progress"
          subtitle={
            deliveryModel === "SPRINT"
              ? "Current week actuals and customer-safe progress narrative"
              : "Current PI progress, scope movement, dependencies, and customer-safe narrative"
          }
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
            {deliveryMetrics.map((metric) => (
              <MetricCard
                key={metric.label}
                label={metric.label}
                value={metric.value}
                caption={metric.caption}
              />
            ))}
          </div>
          {deliveryModel === "SPRINT" ? <SprintProgressFields /> : <PiProgressFields />}
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

function SprintSetupSection() {
  return (
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
  );
}

function PiSetupSection() {
  return (
    <FormSection
      step={3}
      title="PI setup"
      subtitle="PI 2025 Q3 · Jun 1 - Aug 31"
      badgeLabel="Prefilled"
      badgeTone="success"
    >
      <div className="field-grid field-grid--five">
        <TextInputField id="pi-name" label="PI name / number" required value="PI 2025 Q3" />
        <TextInputField id="pi-start-date" label="PI start date" required value="2025-06-01" />
        <TextInputField id="pi-end-date" label="PI end date" required value="2025-08-31" />
        <TextInputField id="total-sprints" label="Total sprints in PI" value="5" />
        <TextInputField id="current-sprint" label="Current sprint" value="2" />
        <TextInputField id="pi-planned-points" label="Planned PI story points" value="120" />
        <TextInputField id="pi-completed-to-date" label="Completed points to date" value="60" />
      </div>
    </FormSection>
  );
}

function SprintProgressFields() {
  return (
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
  );
}

function PiProgressFields() {
  return (
    <div className="field-grid field-grid--five">
      <TextInputField id="pi-current-sprint-progress" label="Current sprint" value="2" />
      <TextInputField id="points-completed-this-week" label="Points completed this week" value="18" />
      <TextInputField id="features-completed" label="Features completed this week" value="2" />
      <TextInputField id="delayed-scope" label="Delayed scope items" value="1" />
      <TextInputField id="blockers-dependencies" label="Blockers / dependencies" value="1" />
      <SelectField
        id="pi-rag-status"
        label="Overall RAG status"
        options={["Green", "Amber", "Red"]}
        required
        value="Amber"
      />
    </div>
  );
}

function calculateModelMetrics(deliveryModel: DeliveryModel) {
  if (deliveryModel === "PI") {
    const plannedPoints = 120;
    const priorCompleted = 60;
    const completedThisWeek = 18;
    const completedToDate = priorCompleted + completedThisWeek;
    const remainingPoints = Math.max(plannedPoints - completedToDate, 0);
    const currentSprint = 2;
    const totalSprints = 5;
    const remainingSprints = Math.max(totalSprints - currentSprint, 1);
    const requiredVelocity = Math.round((remainingPoints / remainingSprints) * 10) / 10;
    const averageVelocity = Math.round((completedToDate / currentSprint) * 10) / 10;

    return [
      {
        label: "PI completion",
        value: `${Math.round((completedToDate / plannedPoints) * 100)}%`,
        caption: `${completedToDate} of ${plannedPoints} points completed`,
      },
      {
        label: "Remaining points",
        value: String(remainingPoints),
        caption: `${remainingSprints} sprints remaining`,
      },
      {
        label: "Required velocity",
        value: String(requiredVelocity),
        caption: "Points per remaining sprint",
      },
      {
        label: "Average velocity",
        value: String(averageVelocity),
        caption: "Current PI average velocity",
      },
    ];
  }

  return [
    { label: "Story completion", value: "67%", caption: "12 of 18 planned stories" },
    { label: "Story points", value: "48 / 70", caption: "22 points remaining" },
    { label: "Effort usage", value: "60%", caption: "96 of 160 hours burned" },
    { label: "DOR adherence", value: "85%", caption: "Healthy readiness" },
  ];
}
