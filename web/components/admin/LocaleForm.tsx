"use client";

import { useState } from "react";
import { AdminLocale, LocaleCreateInput, LocaleUpdateInput } from "@/lib/admin-api";

interface LocaleFormProps {
  locale?: AdminLocale;
  onSubmit: (data: LocaleCreateInput | LocaleUpdateInput) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
}

/**
 * Form for creating or editing a locale.
 */
export default function LocaleForm({
  locale,
  onSubmit,
  onCancel,
  isLoading = false,
}: LocaleFormProps) {
  const isEditing = !!locale;

  const [formData, setFormData] = useState({
    slug: locale?.slug || "",
    name: locale?.name || "",
    display_name: locale?.display_name || "",
    min_latitude: locale?.bounds?.min_latitude?.toString() || "",
    max_latitude: locale?.bounds?.max_latitude?.toString() || "",
    min_longitude: locale?.bounds?.min_longitude?.toString() || "",
    max_longitude: locale?.bounds?.max_longitude?.toString() || "",
    center_lat: locale?.center?.lat?.toString() || "",
    center_lng: locale?.center?.lng?.toString() || "",
    min_magnitude: locale?.min_magnitude?.toString() || "2.5",
    is_active: locale?.is_active ?? true,
    is_featured: locale?.is_featured ?? true,
    sort_order: locale?.sort_order?.toString() || "0",
  });

  const [error, setError] = useState("");

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;

    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      const bounds = {
        min_latitude: parseFloat(formData.min_latitude),
        max_latitude: parseFloat(formData.max_latitude),
        min_longitude: parseFloat(formData.min_longitude),
        max_longitude: parseFloat(formData.max_longitude),
      };

      const center = {
        lat: parseFloat(formData.center_lat),
        lng: parseFloat(formData.center_lng),
      };

      // Basic validation
      if (bounds.min_latitude >= bounds.max_latitude) {
        throw new Error("Min latitude must be less than max latitude");
      }
      if (bounds.min_longitude >= bounds.max_longitude) {
        throw new Error("Min longitude must be less than max longitude");
      }
      if (
        center.lat < bounds.min_latitude ||
        center.lat > bounds.max_latitude ||
        center.lng < bounds.min_longitude ||
        center.lng > bounds.max_longitude
      ) {
        throw new Error("Center must be within bounds");
      }

      if (isEditing) {
        const updates: LocaleUpdateInput = {
          name: formData.name,
          display_name: formData.display_name,
          bounds,
          center,
          min_magnitude: parseFloat(formData.min_magnitude),
          is_active: formData.is_active,
          is_featured: formData.is_featured,
          sort_order: parseInt(formData.sort_order),
        };
        await onSubmit(updates);
      } else {
        const newLocale: LocaleCreateInput = {
          slug: formData.slug.toLowerCase().replace(/[^a-z0-9-]/g, ""),
          name: formData.name,
          display_name: formData.display_name,
          bounds,
          center,
          min_magnitude: parseFloat(formData.min_magnitude),
          is_active: formData.is_active,
          is_featured: formData.is_featured,
          sort_order: parseInt(formData.sort_order),
        };
        await onSubmit(newLocale);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="p-3 bg-red-500/20 border border-red-500 rounded-lg text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Basic Info */}
      <div className="space-y-4">
        <h3 className="text-lg font-medium text-white">Basic Information</h3>

        {!isEditing && (
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Slug (URL-friendly ID)
            </label>
            <input
              type="text"
              name="slug"
              value={formData.slug}
              onChange={handleChange}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., san-diego"
              required
              pattern="[a-z0-9-]+"
              title="Lowercase letters, numbers, and hyphens only"
            />
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Name
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., San Diego"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Display Name
            </label>
            <input
              type="text"
              name="display_name"
              value={formData.display_name}
              onChange={handleChange}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., San Diego, CA"
              required
            />
          </div>
        </div>
      </div>

      {/* Bounds */}
      <div className="space-y-4">
        <h3 className="text-lg font-medium text-white">Geographic Bounds</h3>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Min Latitude (South)
            </label>
            <input
              type="number"
              name="min_latitude"
              value={formData.min_latitude}
              onChange={handleChange}
              step="0.0001"
              min="-90"
              max="90"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Max Latitude (North)
            </label>
            <input
              type="number"
              name="max_latitude"
              value={formData.max_latitude}
              onChange={handleChange}
              step="0.0001"
              min="-90"
              max="90"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Min Longitude (West)
            </label>
            <input
              type="number"
              name="min_longitude"
              value={formData.min_longitude}
              onChange={handleChange}
              step="0.0001"
              min="-180"
              max="180"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Max Longitude (East)
            </label>
            <input
              type="number"
              name="max_longitude"
              value={formData.max_longitude}
              onChange={handleChange}
              step="0.0001"
              min="-180"
              max="180"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
        </div>
      </div>

      {/* Center */}
      <div className="space-y-4">
        <h3 className="text-lg font-medium text-white">Map Center</h3>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Center Latitude
            </label>
            <input
              type="number"
              name="center_lat"
              value={formData.center_lat}
              onChange={handleChange}
              step="0.0001"
              min="-90"
              max="90"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Center Longitude
            </label>
            <input
              type="number"
              name="center_lng"
              value={formData.center_lng}
              onChange={handleChange}
              step="0.0001"
              min="-180"
              max="180"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
        </div>
      </div>

      {/* Settings */}
      <div className="space-y-4">
        <h3 className="text-lg font-medium text-white">Settings</h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Min Magnitude
            </label>
            <input
              type="number"
              name="min_magnitude"
              value={formData.min_magnitude}
              onChange={handleChange}
              step="0.1"
              min="0"
              max="10"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Sort Order
            </label>
            <input
              type="number"
              name="sort_order"
              value={formData.sort_order}
              onChange={handleChange}
              min="0"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
        </div>

        <div className="flex gap-6">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              name="is_active"
              checked={formData.is_active}
              onChange={handleChange}
              className="w-4 h-4 rounded bg-gray-700 border-gray-600 text-blue-500 focus:ring-blue-500"
            />
            <span className="text-gray-300">Active</span>
          </label>

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              name="is_featured"
              checked={formData.is_featured}
              onChange={handleChange}
              className="w-4 h-4 rounded bg-gray-700 border-gray-600 text-blue-500 focus:ring-blue-500"
            />
            <span className="text-gray-300">Featured (show in navigation)</span>
          </label>
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-4 pt-4">
        <button
          type="submit"
          disabled={isLoading}
          className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
        >
          {isLoading ? "Saving..." : isEditing ? "Update Locale" : "Create Locale"}
        </button>
        <button
          type="button"
          onClick={onCancel}
          disabled={isLoading}
          className="px-6 py-2 bg-gray-600 hover:bg-gray-700 disabled:bg-gray-800 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}
