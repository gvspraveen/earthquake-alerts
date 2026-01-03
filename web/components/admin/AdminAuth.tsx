"use client";

import { useState, useEffect, ReactNode } from "react";
import {
  getAdminKey,
  setAdminKey,
  validateAdminKey,
  hasAdminKey,
} from "@/lib/admin-api";

interface AdminAuthProps {
  children: ReactNode;
}

/**
 * Admin authentication wrapper component.
 * Prompts for API key if not authenticated.
 */
export default function AdminAuth({ children }: AdminAuthProps) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [apiKey, setApiKey] = useState("");
  const [error, setError] = useState("");

  // Check for existing authentication on mount
  useEffect(() => {
    const checkAuth = async () => {
      if (hasAdminKey()) {
        const key = getAdminKey();
        if (key) {
          const valid = await validateAdminKey(key);
          if (valid) {
            setIsAuthenticated(true);
          }
        }
      }
      setIsLoading(false);
    };
    checkAuth();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const valid = await validateAdminKey(apiKey);
      if (valid) {
        setAdminKey(apiKey);
        setIsAuthenticated(true);
      } else {
        setError("Invalid API key");
      }
    } catch (err) {
      setError("Failed to validate API key");
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900">
        <div className="text-white">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900 p-4">
        <div className="w-full max-w-md">
          <div className="bg-gray-800 rounded-lg shadow-xl p-8">
            <h1 className="text-2xl font-bold text-white mb-6 text-center">
              Admin Login
            </h1>
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label
                  htmlFor="apiKey"
                  className="block text-sm font-medium text-gray-300 mb-2"
                >
                  API Key
                </label>
                <input
                  type="password"
                  id="apiKey"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter admin API key"
                  required
                />
              </div>
              {error && (
                <div className="mb-4 p-3 bg-red-500/20 border border-red-500 rounded-lg text-red-400 text-sm">
                  {error}
                </div>
              )}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
              >
                {isLoading ? "Validating..." : "Login"}
              </button>
            </form>
          </div>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
