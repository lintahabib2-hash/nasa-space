import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { restoreBeforeRender, startDurability } from "./services/storage";
import { registerServiceWorker } from "./sw/register";
// Fonts are bundled locally (latin subsets) so the app still renders correctly offline.
import "@fontsource/chakra-petch/latin-600.css";
import "@fontsource/chakra-petch/latin-700.css";
import "@fontsource/atkinson-hyperlegible/latin-400.css";
import "@fontsource/atkinson-hyperlegible/latin-700.css";
import "@fontsource/ibm-plex-mono/latin-400.css";
import "@fontsource/ibm-plex-mono/latin-500.css";
import "./styles/global.css";

// Member 6: put back check-ins from the IndexedDB mirror if localStorage was cleared (bounded wait, never throws),
// then render, then enable offline caching and mirroring. All are safe no-ops where unsupported.
void restoreBeforeRender().then(() => {
  createRoot(document.getElementById("root")!).render(
    <StrictMode>
      <App />
    </StrictMode>,
  );
  void registerServiceWorker();
  startDurability();
});
