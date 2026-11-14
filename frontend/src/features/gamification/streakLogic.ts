// Streak calculation (Member 5): consecutive local calendar days with at least one saved check-in.
// If today has no check-in yet, the streak counts back from yesterday, so it is not broken mid-day.
import { localDay } from "../checkin/checkinSchema";

export function calculateStreak(days: Iterable<string>, today: Date = new Date()): number {
  const set = new Set(days);
  const cursor = new Date(today);
  if (!set.has(localDay(cursor))) cursor.setDate(cursor.getDate() - 1);
  let count = 0;
  while (set.has(localDay(cursor))) {
    count += 1;
    cursor.setDate(cursor.getDate() - 1);
  }
  return count;
}
