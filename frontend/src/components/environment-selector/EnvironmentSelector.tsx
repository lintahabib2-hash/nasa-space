import type { EnvironmentCard } from "../../features/dashboard/types";

interface Props {
  environments: Record<string, EnvironmentCard>;
  value: string;
  onChange: (id: string) => void;
}

/** Mission environment (station / spacecraft / lunar / Mars). Native radios keep it keyboard-accessible. */
export function EnvironmentSelector({ environments, value, onChange }: Props) {
  return (
    <fieldset className="control-group">
      <legend>Mission environment</legend>
      <div className="segmented">
        {Object.entries(environments).map(([id, env]) => (
          <label key={id}>
            <input
              type="radio"
              name="environment"
              value={id}
              checked={value === id}
              onChange={() => onChange(id)}
            />
            <span>{env.label}</span>
          </label>
        ))}
      </div>
    </fieldset>
  );
}
