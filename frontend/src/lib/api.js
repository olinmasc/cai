const BASE = "http://127.0.0.1:8000";

function getToken() {
  return localStorage.getItem("cai_token") || "";
}

async function request(method, path, body = null) {
  const token = getToken();
  const isFormData = body instanceof FormData;

  const headers = {
    ...(token && { Authorization: `Bearer ${token}` }),
    ...(!isFormData && body && { "Content-Type": "application/json" }),
  };

  try {
    const res = await fetch(`${BASE}${path}`, {
      method,
      headers,
      body: isFormData ? body : body ? JSON.stringify(body) : undefined,
    });

    let data = null;
    const contentType = res.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      data = await res.json().catch(() => null);
    }

    if (!res.ok) {
      return { data: null, error: data?.detail || `Error ${res.status}` };
    }

    return { data, error: null };
  } catch {
    return { data: null, error: "Network error — is the backend running?" };
  }
}

async function download(path) {
  const token = getToken();
  try {
    const res = await fetch(`${BASE}${path}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) {
      const err = await res.json().catch(() => null);
      return { blob: null, error: err?.detail || "Download failed" };
    }
    const blob = await res.blob();
    return { blob, error: null };
  } catch {
    return { blob: null, error: "Network error during download" };
  }
}

export const api = {
  get:      (path)         => request("GET",    path),
  post:     (path, body)   => request("POST",   path, body),
  put:      (path, body)   => request("PUT",    path, body),
  delete:   (path)         => request("DELETE", path),
  upload:   (path, form)   => request("POST",   path, form),
  download,
};
