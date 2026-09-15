import axios from "axios";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_URL,

  headers: {
    "Content-Type": "application/json",
  },

  // Normal API requests should fail fast enough to give the user
  // useful feedback. Long-running backtests override this timeout
  // at the individual request level.
  timeout: 120000,
});

// ============================================================
// USER-FRIENDLY API ERROR MESSAGE
// ============================================================

export function getApiErrorMessage(
  error: unknown,
  fallback = "Something went wrong. Please try again."
): string {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status;
    const data = error.response?.data;

    // MarketIQ production error format.
    if (typeof data?.error?.message === "string") {
      return data.error.message;
    }

    // Existing FastAPI responses.
    if (typeof data?.message === "string") {
      return data.message;
    }

    if (typeof data?.detail === "string") {
      return data.detail;
    }

    if (Array.isArray(data?.detail)) {
      const messages = data.detail
        .map((item: any) => {
          if (typeof item === "string") return item;
          return item?.msg || "Invalid request.";
        })
        .filter(Boolean);

      if (messages.length > 0) {
        return messages.join(", ");
      }
    }

    if (status === 400) {
      return "The request could not be completed. Please check your input.";
    }

    if (status === 404) {
      return "The requested MarketIQ resource was not found.";
    }

    if (status === 422) {
      return "Please check the entered values and try again.";
    }

    if (status === 429) {
      return "Too many requests. Please wait a moment and try again.";
    }

    if (status && status >= 500) {
      return "MarketIQ is temporarily unavailable. Please try again shortly.";
    }

    if (error.code === "ECONNABORTED" || error.code === "ETIMEDOUT") {
      return "The request took too long. Please try again.";
    }

    if (!error.response) {
      return "Unable to connect to the MarketIQ server. Please check your connection.";
    }
  }

  if (error instanceof Error && error.message) {
    return error.message;
  }

  return fallback;
}

// ============================================================
// REQUEST INTERCEPTOR
// ============================================================

api.interceptors.request.use(
  (config) => {
    if (typeof window !== "undefined") {
      const token =
        localStorage.getItem("access_token");

      if (token) {
        config.headers =
          config.headers || {};

        config.headers.Authorization =
          `Bearer ${token}`;
      }
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// ============================================================
// RESPONSE INTERCEPTOR
// ============================================================

api.interceptors.response.use(
  (response) => {
    return response;
  },

  (error) => {
    if (
      typeof window !== "undefined" &&
      error?.response?.status === 401
    ) {
      console.warn(
        "Authentication token is invalid or expired."
      );

      localStorage.removeItem(
        "access_token"
      );

      localStorage.removeItem(
        "user"
      );

      if (
        window.location.pathname !==
        "/login"
      ) {
        window.location.href =
          "/login";
      }
    }

    return Promise.reject(error);
  }
);

export default api;
