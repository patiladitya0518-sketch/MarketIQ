import axios from "axios";

const api = axios.create({
  baseURL:
    process.env.NEXT_PUBLIC_API_URL ||
    "http://127.0.0.1:8000",

  headers: {
    "Content-Type": "application/json",
  },
});

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

      // Remove invalid token
      localStorage.removeItem(
        "access_token"
      );

      // Optional user information
      localStorage.removeItem("user");

      /*
       * Redirect to login page.
       *
       * Change "/login" if your actual
       * login route has a different name.
       */
      if (
        window.location.pathname !==
        "/login"
      ) {
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
);

export default api;