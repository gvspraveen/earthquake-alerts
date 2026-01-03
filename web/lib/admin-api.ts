/**
 * Admin API client for locale management.
 *
 * All requests include the admin API key in the X-Admin-Key header.
 * The API key is stored in session storage after the user enters it.
 */

import { API_BASE_URL } from "./api";

const ADMIN_KEY_STORAGE_KEY = "earthquake-admin-key";

export interface LocaleBounds {
  min_latitude: number;
  max_latitude: number;
  min_longitude: number;
  max_longitude: number;
}

export interface LocaleCenter {
  lat: number;
  lng: number;
}

export interface AdminLocale {
  slug: string;
  name: string;
  display_name: string;
  bounds: LocaleBounds;
  center: LocaleCenter;
  min_magnitude: number;
  is_active: boolean;
  is_featured: boolean;
  sort_order: number;
  created_at: string | null;
  updated_at: string | null;
}

export interface LocaleCreateInput {
  slug: string;
  name: string;
  display_name: string;
  bounds: LocaleBounds;
  center: LocaleCenter;
  min_magnitude?: number;
  is_active?: boolean;
  is_featured?: boolean;
  sort_order?: number;
}

export interface LocaleUpdateInput {
  name?: string;
  display_name?: string;
  bounds?: LocaleBounds;
  center?: LocaleCenter;
  min_magnitude?: number;
  is_active?: boolean;
  is_featured?: boolean;
  sort_order?: number;
}

/**
 * Get the admin API key from session storage.
 */
export function getAdminKey(): string | null {
  if (typeof window === "undefined") return null;
  return sessionStorage.getItem(ADMIN_KEY_STORAGE_KEY);
}

/**
 * Set the admin API key in session storage.
 */
export function setAdminKey(key: string): void {
  if (typeof window === "undefined") return;
  sessionStorage.setItem(ADMIN_KEY_STORAGE_KEY, key);
}

/**
 * Clear the admin API key from session storage.
 */
export function clearAdminKey(): void {
  if (typeof window === "undefined") return;
  sessionStorage.removeItem(ADMIN_KEY_STORAGE_KEY);
}

/**
 * Check if the user has an admin key stored.
 */
export function hasAdminKey(): boolean {
  return getAdminKey() !== null;
}

/**
 * Make an authenticated admin API request.
 */
async function adminFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const adminKey = getAdminKey();

  if (!adminKey) {
    throw new Error("Admin key not set. Please authenticate first.");
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-Admin-Key": adminKey,
      ...options.headers,
    },
  });

  if (response.status === 401) {
    clearAdminKey();
    throw new Error("Invalid admin key. Please re-authenticate.");
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || `Request failed: ${response.status}`);
  }

  return response.json();
}

/**
 * Validate admin key by making a test request.
 */
export async function validateAdminKey(key: string): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/api-admin/locales`, {
      headers: {
        "X-Admin-Key": key,
      },
    });
    return response.ok;
  } catch {
    return false;
  }
}

/**
 * List all locales (including inactive) for admin.
 */
export async function listLocales(): Promise<AdminLocale[]> {
  const data = await adminFetch<{ locales: AdminLocale[] }>("/api-admin/locales");
  return data.locales;
}

/**
 * Get a single locale by slug.
 */
export async function getLocale(slug: string): Promise<AdminLocale> {
  return adminFetch<AdminLocale>(`/api-admin/locales/${slug}`);
}

/**
 * Create a new locale.
 */
export async function createLocale(
  locale: LocaleCreateInput
): Promise<{ message: string; slug: string }> {
  return adminFetch<{ message: string; slug: string }>("/api-admin/locales", {
    method: "POST",
    body: JSON.stringify(locale),
  });
}

/**
 * Update an existing locale.
 */
export async function updateLocale(
  slug: string,
  updates: LocaleUpdateInput
): Promise<{ message: string; slug: string }> {
  return adminFetch<{ message: string; slug: string }>(
    `/api-admin/locales/${slug}`,
    {
      method: "PUT",
      body: JSON.stringify(updates),
    }
  );
}

/**
 * Delete a locale (soft delete by default).
 */
export async function deleteLocale(
  slug: string,
  hard: boolean = false
): Promise<{ message: string; slug: string }> {
  const query = hard ? "?hard=true" : "";
  return adminFetch<{ message: string; slug: string }>(
    `/api-admin/locales/${slug}${query}`,
    {
      method: "DELETE",
    }
  );
}

/**
 * Restore a soft-deleted locale.
 */
export async function restoreLocale(
  slug: string
): Promise<{ message: string; slug: string }> {
  return adminFetch<{ message: string; slug: string }>(
    `/api-admin/locales/${slug}/restore`,
    {
      method: "POST",
    }
  );
}
