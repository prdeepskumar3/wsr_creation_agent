import { useMemo, useState } from "react";

import { StatusBadge } from "./FormPrimitives";

export type RiskRow = {
  id: number;
  description: string;
  severity: "High" | "Medium" | "Low";
  status: "Open" | "In-Progress" | "Closed";
  owner: string;
  mitigation: string;
  closureDate: string;
  remark: string;
};

const initialRiskRows: RiskRow[] = [
  {
    id: 1,
    description: "Vendor API documentation dependency may delay final validation.",
    severity: "High",
    status: "In-Progress",
    owner: "Priya Rao",
    mitigation: "Parallel validation interface is active while vendor clarification is pending.",
    closureDate: "2025-07-04",
    remark: "",
  },
  {
    id: 2,
    description: "Dashboard contract review needs stakeholder confirmation.",
    severity: "Medium",
    status: "Open",
    owner: "Arjun Kapoor",
    mitigation: "Review session is scheduled with product and integration teams.",
    closureDate: "2025-07-05",
    remark: "",
  },
];

export function RiskGrid() {
  const [riskRows, setRiskRows] = useState<RiskRow[]>(initialRiskRows);
  const riskSummary = useMemo(() => summarizeRisks(riskRows), [riskRows]);

  function updateRiskRow(id: number, patch: Partial<RiskRow>) {
    setRiskRows((currentRows) =>
      currentRows.map((risk) => (risk.id === id ? { ...risk, ...patch } : risk)),
    );
  }

  function addRiskRow() {
    setRiskRows((currentRows) => appendRiskRow(currentRows));
  }

  function removeRiskRow(id: number) {
    setRiskRows((currentRows) => removeRiskRowById(currentRows, id));
  }

  return (
    <div className="risk-grid" aria-labelledby="risk-grid-title">
      <div className="risk-grid__toolbar">
        <div>
          <h3 id="risk-grid-title">Risks and dependencies</h3>
          <p>Active risks require owner, mitigation, and planned closure date.</p>
        </div>
        <button className="button button--secondary" type="button" onClick={addRiskRow}>
          + Add risk row
        </button>
      </div>

      <div className="risk-grid__scroll" role="region" aria-label="Risk rows">
        <table>
          <thead>
            <tr>
              <th scope="col">#</th>
              <th scope="col">Risk description</th>
              <th scope="col">Severity</th>
              <th scope="col">Status</th>
              <th scope="col">Mitigation</th>
              <th scope="col">Owner</th>
              <th scope="col">Closure date</th>
              <th scope="col">Remark</th>
              <th scope="col">Actions</th>
            </tr>
          </thead>
          <tbody>
            {riskRows.map((risk) => (
              <tr key={risk.id}>
                <td>{risk.id}</td>
                <td>
                  <textarea
                    aria-label={`Risk ${risk.id} description`}
                    value={risk.description}
                    onChange={(event) =>
                      updateRiskRow(risk.id, { description: event.target.value })
                    }
                    rows={3}
                  />
                </td>
                <td>
                  <select
                    aria-label={`Risk ${risk.id} severity`}
                    value={risk.severity}
                    onChange={(event) =>
                      updateRiskRow(risk.id, {
                        severity: event.target.value as RiskRow["severity"],
                      })
                    }
                  >
                    <option>High</option>
                    <option>Medium</option>
                    <option>Low</option>
                  </select>
                </td>
                <td>
                  <select
                    aria-label={`Risk ${risk.id} status`}
                    value={risk.status}
                    onChange={(event) =>
                      updateRiskRow(risk.id, {
                        status: event.target.value as RiskRow["status"],
                      })
                    }
                  >
                    <option>Open</option>
                    <option>In-Progress</option>
                    <option>Closed</option>
                  </select>
                </td>
                <td>
                  <textarea
                    aria-label={`Risk ${risk.id} mitigation`}
                    value={risk.mitigation}
                    onChange={(event) =>
                      updateRiskRow(risk.id, { mitigation: event.target.value })
                    }
                    rows={3}
                  />
                </td>
                <td>
                  <input
                    aria-label={`Risk ${risk.id} owner`}
                    value={risk.owner}
                    onChange={(event) => updateRiskRow(risk.id, { owner: event.target.value })}
                  />
                </td>
                <td>
                  <input
                    aria-label={`Risk ${risk.id} closure date`}
                    value={risk.closureDate}
                    onChange={(event) =>
                      updateRiskRow(risk.id, { closureDate: event.target.value })
                    }
                    type="date"
                  />
                </td>
                <td>
                  <input
                    aria-label={`Risk ${risk.id} remark`}
                    value={risk.remark}
                    required={risk.status === "Closed"}
                    aria-invalid={risk.status === "Closed" && risk.remark.trim().length === 0}
                    onChange={(event) => updateRiskRow(risk.id, { remark: event.target.value })}
                  />
                  {risk.status === "Closed" && risk.remark.trim().length === 0 ? (
                    <p className="risk-grid__inline-error">Remark required to close.</p>
                  ) : null}
                </td>
                <td>
                  <button
                    className="risk-grid__remove"
                    type="button"
                    aria-label={`Remove risk ${risk.id}`}
                    onClick={() => removeRiskRow(risk.id)}
                    disabled={riskRows.length === 1}
                  >
                    Remove
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="risk-grid__status">
        <StatusBadge label={`${riskSummary.highActiveCount} high active`} tone="danger" />
        <StatusBadge label="0 overdue" tone="success" />
      </div>
    </div>
  );
}

export function appendRiskRow(currentRows: RiskRow[]): RiskRow[] {
  const nextId = Math.max(0, ...currentRows.map((risk) => risk.id)) + 1;

  return [
    ...currentRows,
    {
      id: nextId,
      description: "",
      severity: "Medium",
      status: "Open",
      owner: "",
      mitigation: "",
      closureDate: "",
      remark: "",
    },
  ];
}

export function removeRiskRowById(currentRows: RiskRow[], id: number): RiskRow[] {
  if (currentRows.length === 1) {
    return currentRows;
  }

  return currentRows.filter((risk) => risk.id !== id);
}

export function requiresClosureRemark(risk: RiskRow): boolean {
  return risk.status === "Closed" && risk.remark.trim().length === 0;
}

export function summarizeRisks(riskRows: RiskRow[]) {
  return {
    highActiveCount: riskRows.filter(
      (risk) => risk.severity === "High" && risk.status !== "Closed",
    ).length,
    requiresClosureRemarkCount: riskRows.filter(requiresClosureRemark).length,
  };
}
