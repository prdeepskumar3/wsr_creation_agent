import { StatusBadge } from "./FormPrimitives";

type RiskRow = {
  id: number;
  description: string;
  severity: "High" | "Medium" | "Low";
  status: "Open" | "In-Progress" | "Closed";
  owner: string;
  mitigation: string;
  closureDate: string;
  remark: string;
};

const riskRows: RiskRow[] = [
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
  return (
    <div className="risk-grid" aria-labelledby="risk-grid-title">
      <div className="risk-grid__toolbar">
        <div>
          <h3 id="risk-grid-title">Risks and dependencies</h3>
          <p>Active risks require owner, mitigation, and planned closure date.</p>
        </div>
        <button className="button button--secondary" type="button">
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
            </tr>
          </thead>
          <tbody>
            {riskRows.map((risk) => (
              <tr key={risk.id}>
                <td>{risk.id}</td>
                <td>
                  <textarea
                    aria-label={`Risk ${risk.id} description`}
                    defaultValue={risk.description}
                    rows={3}
                  />
                </td>
                <td>
                  <select aria-label={`Risk ${risk.id} severity`} defaultValue={risk.severity}>
                    <option>High</option>
                    <option>Medium</option>
                    <option>Low</option>
                  </select>
                </td>
                <td>
                  <select aria-label={`Risk ${risk.id} status`} defaultValue={risk.status}>
                    <option>Open</option>
                    <option>In-Progress</option>
                    <option>Closed</option>
                  </select>
                </td>
                <td>
                  <textarea
                    aria-label={`Risk ${risk.id} mitigation`}
                    defaultValue={risk.mitigation}
                    rows={3}
                  />
                </td>
                <td>
                  <input aria-label={`Risk ${risk.id} owner`} defaultValue={risk.owner} />
                </td>
                <td>
                  <input
                    aria-label={`Risk ${risk.id} closure date`}
                    defaultValue={risk.closureDate}
                    type="date"
                  />
                </td>
                <td>
                  <input aria-label={`Risk ${risk.id} remark`} defaultValue={risk.remark} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="risk-grid__status">
        <StatusBadge label="1 high active" tone="danger" />
        <StatusBadge label="0 overdue" tone="success" />
      </div>
    </div>
  );
}
