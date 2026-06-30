import type { ReactNode } from "react";

type BadgeTone = "neutral" | "success" | "warning" | "danger" | "info";

type FormSectionProps = {
  step: number;
  title: string;
  subtitle: string;
  badgeLabel?: string;
  badgeTone?: BadgeTone;
  children: ReactNode;
};

type FieldFrameProps = {
  id: string;
  label: string;
  required?: boolean;
  error?: string;
  hint?: string;
  children: ReactNode;
};

type TextInputFieldProps = {
  id: string;
  label: string;
  value: string;
  required?: boolean;
  error?: string;
  hint?: string;
};

type SelectFieldProps = TextInputFieldProps & {
  options: string[];
};

type TextareaFieldProps = TextInputFieldProps & {
  rows?: number;
};

type MetricCardProps = {
  label: string;
  value: string;
  caption: string;
};

type ActionBarProps = {
  children: ReactNode;
};

export function StatusBadge({ label, tone = "neutral" }: { label: string; tone?: BadgeTone }) {
  return <span className={`status-badge status-badge--${tone}`}>{label}</span>;
}

export function FormSection({
  step,
  title,
  subtitle,
  badgeLabel,
  badgeTone = "neutral",
  children,
}: FormSectionProps) {
  return (
    <section className="form-section" aria-labelledby={`section-${step}-title`}>
      <header className="form-section__header">
        <div className="form-section__title-row">
          <span className="form-section__step" aria-hidden="true">
            {step}
          </span>
          <div>
            <h2 id={`section-${step}-title`}>{title}</h2>
            <p>{subtitle}</p>
          </div>
        </div>
        {badgeLabel ? <StatusBadge label={badgeLabel} tone={badgeTone} /> : null}
      </header>
      <div className="form-section__body">{children}</div>
    </section>
  );
}

export function FieldFrame({
  id,
  label,
  required = false,
  error,
  hint,
  children,
}: FieldFrameProps) {
  const hintId = hint ? `${id}-hint` : undefined;
  const errorId = error ? `${id}-error` : undefined;

  return (
    <div className="field">
      <label className="field__label" htmlFor={id}>
        {label}
        {required ? <span className="field__required"> Required</span> : null}
      </label>
      {children}
      {hint ? (
        <p className="field__hint" id={hintId}>
          {hint}
        </p>
      ) : null}
      {error ? (
        <p className="field__error" id={errorId}>
          {error}
        </p>
      ) : null}
    </div>
  );
}

export function TextInputField(props: TextInputFieldProps) {
  const describedBy = describedByFor(props.id, props.hint, props.error);

  return (
    <FieldFrame {...props}>
      <input
        id={props.id}
        className="control"
        defaultValue={props.value}
        aria-invalid={Boolean(props.error)}
        aria-describedby={describedBy}
        required={props.required}
      />
    </FieldFrame>
  );
}

export function SelectField({ options, ...props }: SelectFieldProps) {
  const describedBy = describedByFor(props.id, props.hint, props.error);

  return (
    <FieldFrame {...props}>
      <select
        id={props.id}
        className="control"
        defaultValue={props.value}
        aria-invalid={Boolean(props.error)}
        aria-describedby={describedBy}
        required={props.required}
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </FieldFrame>
  );
}

export function TextareaField({ rows = 4, ...props }: TextareaFieldProps) {
  const describedBy = describedByFor(props.id, props.hint, props.error);

  return (
    <FieldFrame {...props}>
      <textarea
        id={props.id}
        className="control control--textarea"
        defaultValue={props.value}
        rows={rows}
        aria-invalid={Boolean(props.error)}
        aria-describedby={describedBy}
        required={props.required}
      />
    </FieldFrame>
  );
}

export function MetricCard({ label, value, caption }: MetricCardProps) {
  return (
    <article className="metric-card" aria-label={`${label}: ${value}`}>
      <p className="metric-card__label">{label}</p>
      <strong>{value}</strong>
      <span>{caption}</span>
    </article>
  );
}

export function ActionBar({ children }: ActionBarProps) {
  return <div className="action-bar">{children}</div>;
}

function describedByFor(id: string, hint?: string, error?: string): string | undefined {
  const ids = [hint ? `${id}-hint` : undefined, error ? `${id}-error` : undefined].filter(
    Boolean,
  );
  return ids.length ? ids.join(" ") : undefined;
}
