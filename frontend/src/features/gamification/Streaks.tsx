import { calculateStreak } from "./streakLogic";

/** Check-in streak (Member 5 stretch goal). Encourages routine; it says nothing about health. */
export function StreakCard({ days }: { days: string[] }) {
  const count = calculateStreak(days);
  return (
    <div className="ci-streak" aria-live="polite" data-testid="streak">
      <svg width="36" height="36" viewBox="0 0 36 36" aria-hidden="true">
        <circle cx="18" cy="18" r="16" fill="#ffffff" stroke="var(--launch-orange)" strokeWidth="2" />
        <path d="M18 7l3 7.5 8 .5-6.2 5 2 7.8L18 23.5 11.2 27.8l2-7.8L7 15l8-.5z" fill="var(--launch-orange)" />
      </svg>
      <div>
        <strong>{count} {count === 1 ? "day" : "days"} streak</strong>
        <span>{count ? "Nice work showing up for your routine." : "A check-in a day keeps your routine going."}</span>
      </div>
    </div>
  );
}
