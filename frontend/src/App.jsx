import { useState } from "react";
import { ToastProvider } from "./hooks/useToast.jsx";
import Sidebar from "./components/layout/Sidebar.jsx";
import PipelineModal from "./components/PipelineModal.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import ClientsPage from "./pages/ClientsPage.jsx";
import FilingsPage from "./pages/FilingsPage.jsx";
import ExceptionsPage from "./pages/ExceptionsPage.jsx";
import AgentStatusPage from "./pages/AgentStatusPage.jsx";

function AppShell() {
  const [token, setToken] = useState(() => localStorage.getItem("cai_token") || "");
  const [user, setUser]   = useState(() => {
    try { return JSON.parse(localStorage.getItem("cai_user") || "null"); }
    catch { return null; }
  });
  const [view, setView]               = useState("dashboard");
  const [pipelineClient, setPipelineClient] = useState(null);
  const [refreshKey, setRefreshKey]   = useState(0);

  function handleLogin(newToken, userObj) {
    setToken(newToken);
    setUser(userObj);
  }

  function handleLogout() {
    setToken("");
    setUser(null);
    localStorage.removeItem("cai_token");
    localStorage.removeItem("cai_user");
  }

  function handlePipelineDone() {
    setRefreshKey((k) => k + 1);
  }

  if (!token) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "var(--bg)",
        display: "flex",
      }}
    >
      <Sidebar
        view={view}
        setView={setView}
        user={user}
        onLogout={handleLogout}
      />

      <main style={{ flex: 1, overflowY: "auto", minHeight: "100vh" }}>
        {view === "dashboard"  && (
          <DashboardPage
            key={refreshKey}
            user={user}
            onRunPipeline={setPipelineClient}
          />
        )}
        {view === "clients"    && (
          <ClientsPage
            user={user}
            onRunPipeline={setPipelineClient}
          />
        )}
        {view === "filings"    && <FilingsPage user={user} />}
        {view === "exceptions" && <ExceptionsPage user={user} />}
        {view === "agents"     && <AgentStatusPage />}
      </main>

      {pipelineClient && (
        <PipelineModal
          client={pipelineClient}
          isAdmin={user?.role === "Admin"}
          onClose={() => setPipelineClient(null)}
          onDone={handlePipelineDone}
        />
      )}
    </div>
  );
}

export default function App() {
  return (
    <ToastProvider>
      <AppShell />
    </ToastProvider>
  );
}
