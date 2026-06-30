import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";

import {
  appendRiskRow,
  removeRiskRowById,
  requiresClosureRemark,
  RiskGrid,
  summarizeRisks,
  type RiskRow,
} from "./RiskGrid";

const baseRisk: RiskRow = {
  id: 1,
  description: "Vendor dependency may delay validation.",
  severity: "High",
  status: "In-Progress",
  owner: "Priya Rao",
  mitigation: "Parallel validation path is active.",
  closureDate: "2025-07-04",
  remark: "",
};

describe("RiskGrid", () => {
  it("renders add and remove controls for editable WSR risk rows", () => {
    const markup = renderToStaticMarkup(<RiskGrid />);

    expect(markup).toContain("+ Add risk row");
    expect(markup).toContain("Remove risk 1");
    expect(markup).toContain("Remark");
  });

  it("appends a blank editable risk row with the next stable id", () => {
    const rows = appendRiskRow([baseRisk]);

    expect(rows).toHaveLength(2);
    expect(rows[1]).toMatchObject({
      id: 2,
      severity: "Medium",
      status: "Open",
      description: "",
      remark: "",
    });
  });

  it("keeps one row on screen when removing the final row", () => {
    const rows = removeRiskRowById([baseRisk], baseRisk.id);

    expect(rows).toEqual([baseRisk]);
  });

  it("requires remark when a risk is closed", () => {
    expect(requiresClosureRemark({ ...baseRisk, status: "Closed", remark: "" })).toBe(true);
    expect(requiresClosureRemark({ ...baseRisk, status: "Closed", remark: "Completed" })).toBe(
      false,
    );
  });

  it("summarizes active high risks only", () => {
    const summary = summarizeRisks([
      baseRisk,
      { ...baseRisk, id: 2, status: "Closed", remark: "Closed with mitigation." },
      { ...baseRisk, id: 3, severity: "Medium" },
    ]);

    expect(summary.highActiveCount).toBe(1);
    expect(summary.requiresClosureRemarkCount).toBe(0);
  });
});
