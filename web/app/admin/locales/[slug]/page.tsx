"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import LocaleForm from "@/components/admin/LocaleForm";
import {
  getLocale,
  updateLocale,
  AdminLocale,
  LocaleCreateInput,
  LocaleUpdateInput,
} from "@/lib/admin-api";

export default function EditLocalePage() {
  const router = useRouter();
  const params = useParams();
  const slug = params.slug as string;

  const [locale, setLocale] = useState<AdminLocale | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchLocale = async () => {
      try {
        setIsLoading(true);
        const data = await getLocale(slug);
        setLocale(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch locale");
      } finally {
        setIsLoading(false);
      }
    };

    if (slug) {
      fetchLocale();
    }
  }, [slug]);

  const handleSubmit = async (data: LocaleCreateInput | LocaleUpdateInput) => {
    try {
      setIsSaving(true);
      setError("");
      await updateLocale(slug, data as LocaleUpdateInput);
      router.push("/admin/locales");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update locale");
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    router.push("/admin/locales");
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 p-6 flex items-center justify-center">
        <div className="text-gray-400">Loading locale...</div>
      </div>
    );
  }

  if (!locale && !isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 p-6">
        <div className="max-w-3xl mx-auto">
          <div className="bg-red-500/20 border border-red-500 rounded-lg p-6 text-center">
            <p className="text-red-400 mb-4">
              {error || `Locale "${slug}" not found`}
            </p>
            <Link
              href="/admin/locales"
              className="text-blue-400 hover:text-blue-300"
            >
              ← Back to Locales
            </Link>
          </div>
        </div>
      </div>
    );
  }

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
          <h1 className="text-3xl font-bold text-white">
            Edit Locale: {locale?.display_name}
          </h1>
          <p className="text-gray-400 mt-1">
            Slug: <span className="font-mono text-blue-400">{slug}</span>
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
          {locale && (
            <LocaleForm
              locale={locale}
              onSubmit={handleSubmit}
              onCancel={handleCancel}
              isLoading={isSaving}
            />
          )}
        </div>
      </div>
    </div>
  );
}
