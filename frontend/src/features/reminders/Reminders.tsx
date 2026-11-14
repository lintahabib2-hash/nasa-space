import { useEffect, useId, useState } from "react";
import { localDay } from "../checkin/checkinSchema";

// Local daily reminder (Member 5). Works while the page is open. No server or background push.
export const REMINDER_KEY = "crew-vitals.reminder.v1";

export const PROMPTS = [
  "Take a moment to check in with yourself.",
  "What is one thing that would help you feel supported today?",
  "Notice how you are feeling. There is no right answer.",
  "A small pause can be part of a good routine.",
  "Take a breath, then share what feels useful today.",
  "How has your energy felt so far today?",
  "Make space for a quick check-in when you are ready.",
];

interface Settings { enabled: boolean; time: string }

function readSettings(): Settings {
  try {
    const raw = localStorage.getItem(REMINDER_KEY);
    if (!raw) return { enabled: false, time: "09:00" };
    const s = JSON.parse(raw) as Settings;
    if (typeof s.enabled !== "boolean" || typeof s.time !== "string") throw new Error("unexpected format");
    return s;
  } catch {
    return { enabled: false, time: "09:00" };
  }
}

function msUntil(time: string, now = new Date()): number {
  const [h, m] = time.split(":").map(Number);
  const due = new Date(now);
  due.setHours(h || 0, m || 0, 0, 0);
  if (due <= now) due.setDate(due.getDate() + 1);
  return due.getTime() - now.getTime();
}

export function Reminders({ prompt, onPrompt }: { prompt: string; onPrompt: (text: string) => void }) {
  const [settings, setSettings] = useState<Settings>(readSettings);
  const [note, setNote] = useState(settings.enabled ? "Reminder is active while this page is open." : "");
  const [tick, setTick] = useState(0);
  const timeId = useId();

  useEffect(() => {
    if (!settings.enabled) return;
    let lastDay = "";
    const id = window.setTimeout(() => {
      const today = localDay();
      if (lastDay !== today) {
        lastDay = today;
        onPrompt("Your daily check-in is ready whenever you are.");
        setNote("Your daily check-in is ready.");
        if ("Notification" in window && Notification.permission === "granted") {
          new Notification("NASA Space Health Monitoring Agent", { body: "Your daily check-in is ready whenever you are." });
        }
      }
      setTick((t) => t + 1); // schedule the next day
    }, msUntil(settings.time));
    return () => window.clearTimeout(id);
  }, [settings, tick, onPrompt]);

  function persist(next: Settings, message: string) {
    try {
      localStorage.setItem(REMINDER_KEY, JSON.stringify(next));
      setSettings(next);
      setNote(message);
    } catch (e) {
      setNote(`Could not save reminder settings: ${(e as Error).message}`);
    }
  }

  async function toggle(enabled: boolean) {
    persist({ ...settings, enabled }, enabled ? "Reminder is active while this page is open." : "Daily reminder is off.");
    if (enabled && "Notification" in window && Notification.permission === "default") {
      const permission = await Notification.requestPermission();
      if (permission === "denied") setNote("In-page reminders still work while this page is open.");
    }
  }

  return (
    <section className="card ci-panel" aria-labelledby="routine-title">
      <span className="eyebrow">Small steps, daily</span>
      <h2 id="routine-title">Your routine</h2>
      <p className="muted small">A gentle nudge can help you remember. Reminders work while this page is open.</p>
      <label className="ci-toggle">
        <span><strong>Daily reminder</strong><small>On this device only</small></span>
        <input type="checkbox" checked={settings.enabled} onChange={(e) => void toggle(e.target.checked)} />
      </label>
      <div className="ci-field">
        <label htmlFor={timeId}>Reminder time</label>
        <input
          id={timeId}
          type="time"
          value={settings.time}
          disabled={!settings.enabled}
          onChange={(e) => persist({ ...settings, time: e.target.value }, "Reminder time saved for while this page is open.")}
        />
      </div>
      <p className="small ci-note" role="status" aria-live="polite">{note}</p>
      <div className="ci-prompt">
        <span aria-hidden="true">✧</span>
        <div><strong>Today&apos;s prompt</strong><p>{prompt}</p></div>
      </div>
    </section>
  );
}
