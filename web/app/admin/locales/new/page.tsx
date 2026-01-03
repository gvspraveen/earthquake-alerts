"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import LocaleForm from "@/components/admin/LocaleForm";
import { createLocale, LocaleCreateInput, LocaleUpdateInput } from "@/lib/admin-api";

export default function NewLocalePage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (data: LocaleCreateInput | LocaleUpdateInput) => {
    try {
      setIsLoading(true);
      setError("");
      await createLocale(data as LocaleCreateInput);
      router.push("/admin/locales");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create locale");
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    router.push("/admin/locales");
  };

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/admin/locales"
            className="text-gray-400 hover:text-white text-sm mb-2 inline-block"
          >
            ← Back to Locales
          </Link>
          <h1 className="text-3xl font-bold text-white">Create New Locale</h1>
          <p className="text-gray-400 mt-1">
            Add a new earthquake monitoring region
          </p>
        </div>

        {/* Error message */}
        {error && (
          <div className="mb-6 p-4 bg-red-500/20 border border-red-500 rounded-lg text-red-400">
            {error}
          </div>
        )}

        {/* Form */}
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
          <LocaleForm
            onSubmit={handleSubmit}
            onCancel={handleCancel}
            isLoading={isLoading}
          />
        </div>
      </div>
    </div>
  );
}
