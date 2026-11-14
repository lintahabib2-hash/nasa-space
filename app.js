"use strict";

const STORAGE_KEY = "crew-vitals.member5.v1";
const REMINDER_KEY = "crew-vitals.member5.reminder.v1";
const prompts = [
  "Take a moment to check in with yourself.",
  "What is one thing that would help you feel supported today?",
  "Notice how you are feeling—there is no right answer.",
  "A small pause can be part of a good routine.",
  "Take a breath, then share what feels useful today.",
  "How has your energy felt so far today?",
  "Make space for a quick check-in when you are ready."
];

const form = document.querySelector("#checkin-form");
const errorNode = document.querySelector("#checkin-error");
const successNode = document.querySelector("#checkin-success");
const historyNode = document.querySelector("#history-list");
const reminderToggle = document.querySelector("#reminder-enabled");
const reminderTime = document.querySelector("#reminder-time");
const reminderNote = document.querySelector("#reminder-note");
const reactionStart = document.querySelector("#reaction-start");
const reactionTarget = document.querySelector("#reaction-target");
const reactionInstruction = document.querySelector("#reaction-instruction");
const reactionStatus = document.querySelector("#reaction-status");
const reactionError = document.querySelector("#reaction-error");

let activity = null;
let waitTimer = null;
let nextRoundTimer = null;
let reminderTimer = null;
let lastReminderDay = "";

function readRecords() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { checkins: [], reactionTests: [] };
    const parsed = JSON.parse(raw);
    if (!parsed || !Array.isArray(parsed.checkins) || !Array.isArray(parsed.reactionTests)) {
      throw new Error("Stored data does not match the Crew Vitals format.");
    }
    return parsed;
  } catch (error) {
    throw new Error(`Could not read saved data: ${error.message}`);
  }
}

function saveRecords(records) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(records));
  } catch (error) {
    throw new Error(`Could not save data in this browser: ${error.message}`);
  }
}

function makeObservation(measurement, value, units, timestamp) {
  return {
    source_id: "crew-vitals-daily-check-in",
    provenance_kind: "manually_entered",
    subject_id: null,
    study_id: null,
    measurement,
    value,
    units,
    timestamp_utc: timestamp,
    quality_state: "valid",
    reference_url: null
  };
}

function localDay(date = new Date()) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function calculateStreak(checkins) {
  const days = new Set(checkins.map((record) => record.local_day).filter(Boolean));
  let cursor = new Date();
  if (!days.has(localDay(cursor))) cursor.setDate(cursor.getDate() - 1);
  let count = 0;
  while (days.has(localDay(cursor))) {
    count += 1;
    cursor.setDate(cursor.getDate() - 1);
  }
  return count;
}

function updateStreak(checkins) {
  const count = calculateStreak(checkins);
  document.querySelector("#streak-count").textContent = `${count} ${count === 1 ? "day" : "days"} streak`;
  document.querySelector("#streak-detail").textContent = count
    ? "Nice work showing up for your routine."
    : "A check-in a day keeps your routine going.";
}

function formatDay(isoTimestamp) {
  return new Intl.DateTimeFormat(undefined, { weekday: "short", month: "short", day: "numeric" })
    .format(new Date(isoTimestamp));
}

function renderHistory(records) {
  const sorted = [...records.checkins].sort((a, b) => b.timestamp_utc.localeCompare(a.timestamp_utc));
  historyNode.replaceChildren();
  if (sorted.length === 0) {
    const empty = document.createElement("p");
    empty.className = "muted";
    empty.textContent = "Your saved check-ins will appear here.";
    historyNode.append(empty);
    return;
  }
  for (const record of sorted.slice(0, 5)) {
    const item = document.createElement("article");
    item.className = "history-item";
    const title = document.createElement("div");
    const date = document.createElement("strong");
    date.textContent = formatDay(record.timestamp_utc);
    const provenance = document.createElement("span");
    provenance.textContent = "manually_entered";
    title.append(date, provenance);
    const values = document.createElement("div");
    values.className = "history-values";
    const indicators = record.indicators;
    const summary = [
      `${indicators.sleep_hours.value} h sleep`,
      `mood ${indicators.mood.value}/5`
    ];
    if (indicators.blood_pressure_systolic) {
      summary.push(
        `BP ${indicators.blood_pressure_systolic.value}/${indicators.blood_pressure_diastolic.value} mmHg`
      );
    }
    if (indicators.blood_glucose) summary.push(`glucose ${indicators.blood_glucose.value} mg/dL`);
    values.textContent = summary.join(" · ");
    item.append(title, values);
    historyNode.append(item);
  }
}

function refreshPage() {
  const records = readRecords();
  renderHistory(records);
  updateStreak(records.checkins);
}

function readOptionalNumber(data, name, measurement, units, timestamp, min, max) {
  const raw = data.get(name);
  if (raw === "") return null;
  const value = Number(raw);
  if (!Number.isFinite(value) || value < min || value > max) {
    throw new Error(`${measurement.replaceAll("_", " ")} must be between ${min} and ${max} ${units}.`);
  }
  return makeObservation(measurement, value, units, timestamp);
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  errorNode.textContent = "";
  successNode.textContent = "";

  if (!form.reportValidity()) return;

  try {
    const data = new FormData(form);
    const timestamp = new Date().toISOString();
    const sleep = Number(data.get("sleep_hours"));
    const mood = Number(data.get("mood"));
    const stress = Number(data.get("stress"));
    const exercise = Number(data.get("exercise_minutes"));
    if (!Number.isFinite(sleep) || sleep < 0 || sleep > 24) throw new Error("Sleep must be between 0 and 24 hours.");
    if (!Number.isInteger(mood) || mood < 1 || mood > 5) throw new Error("Mood must be a whole-number rating from 1 to 5.");
    if (!Number.isInteger(stress) || stress < 0 || stress > 10) throw new Error("Stress must be a whole-number rating from 0 to 10.");
    if (!Number.isInteger(exercise) || exercise < 0 || exercise > 1440) throw new Error("Exercise must be a whole number from 0 to 1,440 minutes.");

    const indicators = {
      sleep_hours: makeObservation("sleep_hours", sleep, "hours", timestamp),
      mood: makeObservation("mood", mood, "self_rating_1_to_5", timestamp),
      stress: makeObservation("stress", stress, "self_rating_0_to_10", timestamp),
      exercise_minutes: makeObservation("exercise_minutes", exercise, "minutes", timestamp)
    };
    const optionalReadings = [
      readOptionalNumber(data, "heart_rate_bpm", "heart_rate", "bpm", timestamp, 20, 250),
      readOptionalNumber(data, "temperature_c", "body_temperature", "celsius", timestamp, 25, 45),
      readOptionalNumber(data, "spo2_percent", "oxygen_saturation", "percent", timestamp, 50, 100),
      readOptionalNumber(data, "blood_glucose_mg_dl", "blood_glucose", "mg/dL", timestamp, 10, 1000)
    ];
    for (const reading of optionalReadings) {
      if (reading) indicators[reading.measurement] = reading;
    }

    const systolicRaw = data.get("blood_pressure_systolic_mmhg");
    const diastolicRaw = data.get("blood_pressure_diastolic_mmhg");
    if ((systolicRaw === "") !== (diastolicRaw === "")) {
      throw new Error("Enter both systolic and diastolic blood pressure, or leave both blank.");
    }
    if (systolicRaw !== "") {
      const systolic = Number(systolicRaw);
      const diastolic = Number(diastolicRaw);
      if (!Number.isInteger(systolic) || systolic < 40 || systolic > 300) {
        throw new Error("Systolic blood pressure must be a whole number from 40 to 300 mmHg.");
      }
      if (!Number.isInteger(diastolic) || diastolic < 20 || diastolic > 200) {
        throw new Error("Diastolic blood pressure must be a whole number from 20 to 200 mmHg.");
      }
      if (systolic <= diastolic) {
        throw new Error("Systolic blood pressure must be greater than diastolic.");
      }
      indicators.blood_pressure_systolic = makeObservation("blood_pressure_systolic", systolic, "mmHg", timestamp);
      indicators.blood_pressure_diastolic = makeObservation("blood_pressure_diastolic", diastolic, "mmHg", timestamp);
    }

    const record = {
      record_id: globalThis.crypto?.randomUUID ? crypto.randomUUID() : `${timestamp}-${Math.random().toString(16).slice(2)}`,
      timestamp_utc: timestamp,
      local_day: localDay(),
      indicators,
      method: data.get("method"),
      provenance_kind: "manually_entered"
    };
    const records = readRecords();
    records.checkins.push(record);
    saveRecords(records);
    refreshPage();
    form.reset();
    successNode.textContent = "Check-in saved on this device.";
    document.querySelector("#daily-prompt").textContent = "Thanks for checking in. Take a moment for yourself.";
  } catch (error) {
    errorNode.textContent = error.message;
  }
});

function showReminderNote(message) {
  reminderNote.textContent = message;
}

function getReminderSettings() {
  try {
    const value = localStorage.getItem(REMINDER_KEY);
    if (!value) return { enabled: false, time: "09:00" };
    const parsed = JSON.parse(value);
    if (typeof parsed.enabled !== "boolean" || typeof parsed.time !== "string") {
      throw new Error("Reminder settings have an unexpected format.");
    }
    return parsed;
  } catch (error) {
    throw new Error(`Could not read reminder settings: ${error.message}`);
  }
}

function saveReminderSettings(settings) {
  try {
    localStorage.setItem(REMINDER_KEY, JSON.stringify(settings));
  } catch (error) {
    throw new Error(`Could not save reminder settings: ${error.message}`);
  }
}

function notifyReminder() {
  const today = localDay();
  if (lastReminderDay === today) return;
  lastReminderDay = today;
  document.querySelector("#daily-prompt").textContent = "Your daily check-in is ready whenever you are.";
  showReminderNote("Your daily check-in is ready.");
  if ("Notification" in window && Notification.permission === "granted") {
    new Notification("Crew Vitals", { body: "Your daily check-in is ready whenever you are." });
  }
}

function scheduleReminder() {
  window.clearTimeout(reminderTimer);
  if (!reminderToggle.checked) return;
  const [hours, minutes] = reminderTime.value.split(":").map(Number);
  const now = new Date();
  const due = new Date(now);
  due.setHours(hours, minutes, 0, 0);
  if (due <= now) due.setDate(due.getDate() + 1);
  reminderTimer = window.setTimeout(() => {
    notifyReminder();
    scheduleReminder();
  }, due.getTime() - now.getTime());
}

function setupReminder() {
  const settings = getReminderSettings();
  reminderToggle.checked = settings.enabled;
  reminderTime.value = settings.time;
  reminderTime.disabled = !settings.enabled;
  if (settings.enabled) {
    showReminderNote("Reminder is active while this page is open.");
    scheduleReminder();
  }

  reminderToggle.addEventListener("change", async () => {
    reminderTime.disabled = !reminderToggle.checked;
    try {
      const current = { enabled: reminderToggle.checked, time: reminderTime.value };
      saveReminderSettings(current);
      if (current.enabled && "Notification" in window && Notification.permission === "default") {
        const permission = await Notification.requestPermission();
        if (permission === "denied") showReminderNote("In-page reminders still work while this page is open.");
      }
      if (current.enabled) showReminderNote("Reminder is active while this page is open.");
      else showReminderNote("Daily reminder is off.");
      scheduleReminder();
    } catch (error) {
      reminderToggle.checked = false;
      reminderTime.disabled = true;
      showReminderNote(error.message);
    }
  });

  reminderTime.addEventListener("change", () => {
    try {
      saveReminderSettings({ enabled: reminderToggle.checked, time: reminderTime.value });
      scheduleReminder();
      showReminderNote(reminderToggle.checked ? "Reminder time saved for while this page is open." : "Reminder time saved.");
    } catch (error) {
      showReminderNote(error.message);
    }
  });
}

function finishActivity() {
  const readings = activity.readings;
  const sorted = [...readings].sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  const median = sorted.length % 2 ? sorted[middle] : Math.round((sorted[middle - 1] + sorted[middle]) / 2);
  const record = {
    record_id: globalThis.crypto?.randomUUID ? crypto.randomUUID() : `${new Date().toISOString()}-${Math.random().toString(16).slice(2)}`,
    source_id: "crew-vitals-reaction-activity",
    provenance_kind: "manually_entered",
    subject_id: null,
    study_id: null,
    measurement: "visual_reaction_time_median",
    task: "five_round_visual_response",
    score: median,
    units: "milliseconds",
    timestamp_utc: new Date().toISOString(),
    quality_state: "valid",
    reference_url: null,
    method: "browser_performance_api; click_or_touch"
  };
  try {
    const records = readRecords();
    records.reactionTests.push(record);
    saveRecords(records);
    reactionInstruction.textContent = `Activity complete. Median response: ${median} ms.`;
    reactionStatus.textContent = "Saved on this device. This is not a standardized score.";
    reactionStart.textContent = "Try again";
  } catch (error) {
    reactionError.textContent = error.message;
    reactionInstruction.textContent = "Activity complete, but the result could not be saved.";
  }
  activity = null;
  reactionTarget.disabled = true;
  reactionTarget.classList.remove("is-ready", "is-waiting");
  reactionTarget.textContent = "GO";
}

function beginRound() {
  if (!activity) return;
  activity.phase = "waiting";
  reactionTarget.disabled = true;
  reactionTarget.classList.remove("is-ready");
  reactionTarget.classList.add("is-waiting");
  reactionInstruction.textContent = `Wait for the target… Round ${activity.readings.length + 1} of 5`;
  const delay = 900 + Math.random() * 1900;
  waitTimer = window.setTimeout(() => {
    if (!activity) return;
    activity.phase = "ready";
    reactionTarget.disabled = false;
    reactionTarget.classList.remove("is-waiting");
    reactionTarget.classList.add("is-ready");
    reactionInstruction.textContent = "Tap or click the target!";
    activity.startedAt = performance.now();
  }, delay);
}

reactionStart.addEventListener("click", () => {
  window.clearTimeout(waitTimer);
  window.clearTimeout(nextRoundTimer);
  activity = { readings: [], phase: "waiting", startedAt: 0 };
  reactionError.textContent = "";
  reactionStatus.textContent = "Optional activity in progress.";
  reactionStart.textContent = "Restart activity";
  beginRound();
});

reactionTarget.addEventListener("click", () => {
  if (!activity) return;
  if (activity.phase === "waiting") {
    window.clearTimeout(waitTimer);
    window.clearTimeout(nextRoundTimer);
    activity = null;
    reactionTarget.disabled = true;
    reactionTarget.classList.remove("is-waiting");
    reactionInstruction.textContent = "Too soon. Start again when you are ready.";
    reactionStatus.textContent = "No result was saved.";
    reactionStart.textContent = "Start activity";
    return;
  }
  if (activity.phase !== "ready") return;
  activity.readings.push(Math.round(performance.now() - activity.startedAt));
  reactionTarget.disabled = true;
  reactionTarget.classList.remove("is-ready");
  reactionTarget.textContent = "✓";
  if (activity.readings.length === 5) {
    window.setTimeout(finishActivity, 300);
  } else {
    reactionInstruction.textContent = "Got it. Get ready for the next round.";
    nextRoundTimer = window.setTimeout(() => {
      if (activity) {
        reactionTarget.textContent = "GO";
        beginRound();
      }
    }, 500);
  }
});

document.querySelector("#export-data").addEventListener("click", () => {
  try {
    const records = readRecords();
    const blob = new Blob([JSON.stringify(records, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `crew-vitals-${localDay()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  } catch (error) {
    document.querySelector("#history-title").focus?.();
    historyNode.textContent = error.message;
  }
});

try {
  document.querySelector("#daily-prompt").textContent = prompts[Math.floor(Math.random() * prompts.length)];
  refreshPage();
  setupReminder();
} catch (error) {
  errorNode.textContent = error.message;
  showReminderNote(error.message);
}
