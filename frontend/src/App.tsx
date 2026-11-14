import { useEffect, useState } from "react";
import { AppShell } from "./components/layout/AppShell";
import { CheckInPage } from "./features/checkin/CheckInPage";
import { DashboardPage } from "./features/dashboard/DashboardPage";

// Hash routes work on any static host and offline: #/ (dashboard), #/checkin
type Route = "dashboard" | "checkin";
const routeFromHash = (): Route => (window.location.hash.startsWith("#/checkin") ? "checkin" : "dashboard");

export default function App() {
  const [route, setRoute] = useState<Route>(routeFromHash);

  useEffect(() => {
    const onHash = () => {
      setRoute(routeFromHash());
      document.getElementById("main")?.focus();
    };
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  const nav = (
    <nav className="app-nav" aria-label="Sections">
      <a href="#/" aria-current={route === "dashboard" ? "page" : undefined}>Crew dashboard</a>
      <a href="#/checkin" aria-current={route === "checkin" ? "page" : undefined}>Daily check-in</a>
    </nav>
  );

  return <AppShell nav={nav}>{route === "checkin" ? <CheckInPage /> : <DashboardPage />}</AppShell>;
}
