"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import LocaleTable from "@/components/admin/LocaleTable";
import {
  AdminLocale,
  listLocales,
  deleteLocale,
  restoreLocale,
  clearAdminKey,
} from "@/lib/admin-api";

export default function AdminLocalesPage() {
  const [locales, setLocales] = useState<AdminLocale[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionLoading, setActionLoading] = useState(false);

  const fetchLocales = async () => {
    try {
      setIsLoading(true);
      setError("");
      const data = await listLocales();
      setLocales(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch locales");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchLocales();
  }, []);

  const handleDelete = async (slug: string) => {
    if (!confirm(`Are you sure you want to deactivate "${slug}"?`)) {
      return;
    }

    try {
      setActionLoading(true);
      await deleteLocale(slug);
      await fetchLocales();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete locale");
    } finally {
      setActionLoading(false);
    }
  };

  const handleRestore = async (slug: string) => {
    try {
      setActionLoading(true);
      await restoreLocale(slug);
      await fetchLocales();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to restore locale");
    } finally {
      setActionLoading(false);
    }
  };

  const handleLogout = () => {
    clearAdminKey();
    window.location.reload();
  };

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white">Locale Management</h1>
            <p className="text-gray-400 mt-1">
              Manage earthquake monitoring regions
            </p>
          </div>
          <div className="flex gap-4">
            <Link
              href="/admin/locales/new"
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
            >
              + New Locale
            </Link>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white font-medium rounded-lg transition-colors"
            >
              Logout
            </button>
          </div>
        </div>

        {/* Error message */}
        {error && (
          <div className="mb-6 p-4 bg-red-500/20 border border-red-500 rounded-lg text-red-400">
            {error}
            <button
              onClick={() => setError("")}
              className="ml-4 text-red-300 hover:text-white"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Content */}
        <div className="bg-gray-800 rounded-lg shadow-xl">
          {isLoading ? (
            <div className="p-12 text-center text-gray-400">
              Loading locales...
            </div>
          ) : (
            <LocaleTable
              locales={locales}
              onDelete={handleDelete}
              onRestore={handleRestore}
              isLoading={actionLoading}
            />
          )}
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-gray-500 text-sm">
          <Link href="/" className="hover:text-gray-300">
            ← Back to earthquake.city
          </Link>
        </div>
      </div>
    </div>
  );
}
