/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_DATA_MODE?: "fixtures" | "api";
  readonly VITE_SUBJECT_ID?: string;
}
