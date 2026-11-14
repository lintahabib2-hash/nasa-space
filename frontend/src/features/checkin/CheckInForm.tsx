import { useRef, useState, type FormEvent } from "react";
import { KNOWLEDGE } from "../dashboard/dataSource";
import { buildCheckin, FIELDS, type CheckinRecord, type CollectionMethod, type FieldDef } from "./checkinSchema";

interface Props {
  /** Persist the record. Throw to report a save error. */
  onSave: (record: CheckinRecord) => void;
}

function Field({ f, invalid }: { f: FieldDef; invalid: boolean }) {
  const id = `ci-${f.measurement}`;
  const hintId = `${id}-hint`;
  const why = KNOWLEDGE.indicators[f.measurement]?.why;
  const common = {
    id, name: f.measurement, required: f.required,
    "aria-invalid": invalid || undefined, "aria-describedby": hintId,
  };
  return (
    <div className="ci-field">
      <label htmlFor={id}>
        {f.label} <span className="ci-unit">{f.unitLabel}</span>
        {f.required && <span className="ci-required" aria-hidden="true">*</span>}
      </label>
      {f.options ? (
        <select {...common} defaultValue="">
          <option value="">Choose one</option>
          {f.options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
      ) : (
        <input {...common} type="number" inputMode="decimal" min={f.min} max={f.max} step={f.step} placeholder={f.required ? undefined : "Optional"} />
      )}
      <small id={hintId}>
        {f.hint}
        {why && <span className="ci-why"> · Why: {why}</span>}
      </small>
    </div>
  );
}

/** Daily check-in form (Member 5, ported from index.html/app.js). */
export function CheckInForm({ onSave }: Props) {
  const formRef = useRef<HTMLFormElement>(null);
  const [error, setError] = useState<{ message: string; field?: string } | null>(null);
  const [success, setSuccess] = useState("");

  function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setSuccess("");
    const data = new FormData(e.currentTarget);
    const raw: Record<string, string> = {};
    for (const f of FIELDS) raw[f.measurement] = String(data.get(f.measurement) ?? "");
    const result = buildCheckin(raw, { method: (data.get("method") as CollectionMethod) || "self_reported" });
    if (!result.ok) {
      setError({ message: result.message, field: result.field });
      if (result.field) formRef.current?.querySelector<HTMLElement>(`[name="${result.field}"]`)?.focus();
      return;
    }
    try {
      onSave(result.record);
      setError(null);
      formRef.current?.reset();
      setSuccess("Check-in saved on this device.");
    } catch (err) {
      setError({ message: (err as Error).message });
    }
  }

  const core = FIELDS.filter((f) => f.group === "core");
  const vitals = FIELDS.filter((f) => f.group === "vitals");

  return (
    <section className="card ci-panel" aria-labelledby="checkin-title">
      <div className="ci-heading">
        <div>
          <span className="eyebrow">About a minute</span>
          <h2 id="checkin-title">How are you today?</h2>
        </div>
      </div>
      <p className="muted small">
        Share a few self-reported details. Required items are marked with <span aria-hidden="true">*</span>
        <span className="sr-only">an asterisk</span>. Limits check the format of what you type. They are not health thresholds.
      </p>

      <form ref={formRef} onSubmit={submit} noValidate>
        <div className="ci-grid">
          {core.map((f) => <Field key={f.measurement} f={f} invalid={error?.field === f.measurement} />)}
        </div>

        <details className="ci-optional">
          <summary>Optional: add vital readings</summary>
          <p className="muted small">Only enter a value you already have.</p>
          <div className="ci-grid">
            {vitals.map((f) => <Field key={f.measurement} f={f} invalid={error?.field === f.measurement} />)}
          </div>
        </details>

        <div className="ci-field ci-method">
          <label htmlFor="ci-method">How did you collect these readings?</label>
          <select id="ci-method" name="method" defaultValue="self_reported">
            <option value="self_reported">Self-reported</option>
            <option value="device_measured">Device-measured (vitals only)</option>
          </select>
        </div>

        {error && <p className="ci-error" role="alert">{error.message}</p>}
        <div className="ci-footer">
          <span className="small muted">Saved only in this browser</span>
          <button className="btn btn--primary" type="submit">Save today&apos;s check-in</button>
        </div>
        <p className="ci-success" role="status" aria-live="polite">{success}</p>
      </form>
    </section>
  );
}
