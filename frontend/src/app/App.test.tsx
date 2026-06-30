import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";

import { App } from "./App";
import { WsrFormShell } from "../features/wsr/components/WsrFormShell";

describe("App", () => {
  it("is defined", () => {
    expect(App).toBeDefined();
  });

  it("renders the production WSR form shell", () => {
    const markup = renderToStaticMarkup(<App />);

    expect(markup).toContain("Create weekly status report");
    expect(markup).toContain("Account and project");
    expect(markup).toContain("Delivery model");
    expect(markup).toContain("Sprint setup");
    expect(markup).toContain("Delivery progress");
    expect(markup).toContain("Risks and dependencies");
    expect(markup).toContain("Narrative details");
    expect(markup).toContain("AI review and ready-to-share preview");
    expect(markup).toContain("Save draft");
    expect(markup).toContain("Generate WSR");
  });

  it("marks required fields and exposes accessible risk row labels", () => {
    const markup = renderToStaticMarkup(<App />);

    expect(markup).toContain("Required");
    expect(markup).toContain('aria-label="Risk 1 description"');
    expect(markup).toContain('aria-label="Risk rows"');
    expect(markup).toContain('aria-label="Weekly status report form"');
  });

  it("renders PI fields and hides Sprint-only fields when PI is selected", () => {
    const markup = renderToStaticMarkup(<WsrFormShell initialDeliveryModel="PI" />);

    expect(markup).toContain("PI setup");
    expect(markup).toContain("PI completion");
    expect(markup).toContain("Required velocity");
    expect(markup).not.toContain("Sprint setup");
    expect(markup).not.toContain("Stories completed");
  });

  it("renders read-only AI insights and editable ready-to-share preview", () => {
    const markup = renderToStaticMarkup(<App />);

    expect(markup).toContain("AI insights");
    expect(markup).toContain("View-only PM guidance");
    expect(markup).toContain("Read only");
    expect(markup).toContain("<details");
    expect(markup).toContain("Ready-to-share WSR preview");
    expect(markup).toContain("Editable customer-facing content");
    expect(markup).toContain('id="preview-executive-summary"');
    expect(markup).toContain('id="preview-next-actions"');
  });
});
