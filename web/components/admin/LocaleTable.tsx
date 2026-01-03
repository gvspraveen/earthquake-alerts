"use client";

import Link from "next/link";
import { AdminLocale } from "@/lib/admin-api";

interface LocaleTableProps {
  locales: AdminLocale[];
  onDelete: (slug: string) => void;
  onRestore: (slug: string) => void;
  isLoading?: boolean;
}

/**
 * Table displaying all locales with actions.
 */
export default function LocaleTable({
  locales,
  onDelete,
  onRestore,
  isLoading = false,
}: LocaleTableProps) {
  if (locales.length === 0) {
    return (
      <div className="text-center py-12 text-gray-400">
        No locales found. Create your first locale to get started.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-gray-700">
            <th className="px-4 py-3 text-left text-sm font-medium text-gray-400">
              Slug
            </th>
            <th className="px-4 py-3 text-left text-sm font-medium text-gray-400">
              Display Name
            </th>
            <th className="px-4 py-3 text-left text-sm font-medium text-gray-400">
              Bounds
            </th>
            <th className="px-4 py-3 text-left text-sm font-medium text-gray-400">
              Status
            </th>
            <th className="px-4 py-3 text-left text-sm font-medium text-gray-400">
              Order
            </th>
            <th className="px-4 py-3 text-right text-sm font-medium text-gray-400">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-700">
          {locales.map((locale) => (
            <tr
              key={locale.slug}
              className={`hover:bg-gray-800/50 ${
                !locale.is_active ? "opacity-50" : ""
              }`}
            >
              <td className="px-4 py-3">
                <span className="font-mono text-sm text-blue-400">
                  {locale.slug}
                </span>
              </td>
              <td className="px-4 py-3 text-white">{locale.display_name}</td>
              <td className="px-4 py-3 text-sm text-gray-400">
                <span className="font-mono">
                  {locale.bounds?.min_latitude?.toFixed(1)},{" "}
                  {locale.bounds?.min_longitude?.toFixed(1)} →{" "}
                  {locale.bounds?.max_latitude?.toFixed(1)},{" "}
                  {locale.bounds?.max_longitude?.toFixed(1)}
                </span>
              </td>
              <td className="px-4 py-3">
                <div className="flex gap-2">
                  {locale.is_active ? (
                    <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-500/20 text-green-400">
                      Active
                    </span>
                  ) : (
                    <span className="px-2 py-1 text-xs font-medium rounded-full bg-red-500/20 text-red-400">
                      Inactive
                    </span>
                  )}
                  {locale.is_featured && (
                    <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-500/20 text-blue-400">
                      Featured
                    </span>
                  )}
                </div>
              </td>
              <td className="px-4 py-3 text-gray-400">{locale.sort_order}</td>
              <td className="px-4 py-3 text-right">
                <div className="flex justify-end gap-2">
                  <Link
                    href={`/admin/locales/${locale.slug}`}
                    className="px-3 py-1 text-sm bg-gray-700 hover:bg-gray-600 text-white rounded transition-colors"
                  >
                    Edit
                  </Link>
                  {locale.is_active ? (
                    <button
                      onClick={() => onDelete(locale.slug)}
                      disabled={isLoading}
                      className="px-3 py-1 text-sm bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded transition-colors disabled:opacity-50"
                    >
                      Deactivate
                    </button>
                  ) : (
                    <button
                      onClick={() => onRestore(locale.slug)}
                      disabled={isLoading}
                      className="px-3 py-1 text-sm bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded transition-colors disabled:opacity-50"
                    >
                      Restore
                    </button>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
