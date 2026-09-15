"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import api from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setLoading(true);
    setError("");

    try {
      const response = await api.post("/auth/login", {
        email: email.trim(),
        password,
      });

      const token = response?.data?.access_token;

      if (!token) {
        throw new Error(
          "Login succeeded but no access token was returned."
        );
      }

      // Save authentication token
      localStorage.setItem("access_token", token);

      // Clear old user information
      localStorage.removeItem("user");

      // Go to dashboard
      router.push("/dashboard");
    } catch (error: any) {
      console.error(
        "Login failed:",
        error?.response?.data || error
      );

      const backendMessage =
        error?.response?.data?.detail ||
        error?.response?.data?.message;

      setError(
        typeof backendMessage === "string"
          ? backendMessage
          : error?.message ||
              "Login failed. Please check your email and password."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 px-4">
      <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-8 shadow-xl">

        {/* ========================================================
            HEADER
        ======================================================== */}

        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-white">
            Welcome to MarketIQ
          </h1>

          <p className="mt-2 text-slate-400">
            Sign in to your account
          </p>
        </div>

        {/* ========================================================
            LOGIN FORM
        ======================================================== */}

        <form
          onSubmit={handleLogin}
          className="space-y-5"
        >
          {/* ======================================================
              EMAIL
          ====================================================== */}

          <div>
            <label className="mb-2 block text-sm font-medium text-slate-300">
              Email
            </label>

            <input
              type="email"
              value={email}
              onChange={(event) =>
                setEmail(event.target.value)
              }
              placeholder="you@example.com"
              autoComplete="email"
              required
              className="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-white outline-none transition focus:border-blue-500"
            />
          </div>

          {/* ======================================================
              PASSWORD
          ====================================================== */}

          <div>
            <label className="mb-2 block text-sm font-medium text-slate-300">
              Password
            </label>

            <input
              type="password"
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
              placeholder="Enter your password"
              autoComplete="current-password"
              required
              className="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-white outline-none transition focus:border-blue-500"
            />
          </div>

          {/* ======================================================
              ERROR
          ====================================================== */}

          {error && (
            <div className="rounded-xl border border-red-800 bg-red-950/40 px-4 py-3 text-sm text-red-400">
              {error}
            </div>
          )}

          {/* ======================================================
              SUBMIT
          ====================================================== */}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-blue-600 px-4 py-3 font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        {/* ========================================================
            REGISTER LINK
        ======================================================== */}

        <div className="mt-6 text-center text-sm text-slate-400">
          Don't have an account?{" "}

          <Link
            href="/register"
            className="font-semibold text-blue-400 transition hover:text-blue-300"
          >
            Create Account
          </Link>
        </div>
      </div>
    </main>
  );
}