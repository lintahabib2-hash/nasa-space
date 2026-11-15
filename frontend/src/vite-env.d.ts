/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_DATA_MODE?: "fixtures" | "api";
  readonly VITE_SUBJECT_ID?: string;
  /** Member 6: live API origin, e.g. http://127.0.0.1:8000. Unset = use the offline snapshot only. */
  readonly VITE_API_BASE?: string;
}
