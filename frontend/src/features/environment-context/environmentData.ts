// Committed 300-point sample built by backend/app/environment/osdr_eda.py from the NASA OSDR EDA RR-1
// telemetry export. Bundled so the card works offline and on the static deploy.
import sample from "./fixtures/environment.sample.json";
import type { EnvironmentSeries } from "./types";

export const ENVIRONMENT_SERIES: EnvironmentSeries = sample as unknown as EnvironmentSeries;
