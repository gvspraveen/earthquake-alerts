"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, useRef, useEffect } from "react";

interface LocaleNav {
  slug: string;
  name: string;
}

interface HeaderProps {
  currentLocale: string;
  locales?: LocaleNav[];
}

// Fallback for initial render before API data loads
const DEFAULT_LOCALES: LocaleNav[] = [
  { slug: "sanramon", name: "San Ramon" },
  { slug: "bayarea", name: "Bay Area" },
  { slug: "la", name: "Los Angeles" },
];

export default function Header({ currentLocale, locales = DEFAULT_LOCALES }: HeaderProps) {
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const currentLocaleName = locales.find((l) => l.slug === currentLocale)?.name ?? currentLocale;

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelect = (slug: string) => {
    setIsOpen(false);
    if (slug !== currentLocale) {
      router.push(`/${slug}`);
    }
  };

  return (
    <header className="w-full py-4 px-4 md:px-6">
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        <Link
          href="/"
          className="flex items-center gap-2 text-white hover:text-primary-400 transition-colors"
          aria-label="earthquake.city home"
        >
          <svg
            className="w-6 h-6 md:w-8 md:h-8"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            aria-hidden="true"
          >
            <circle cx="12" cy="12" r="10" strokeWidth="1.5" />
            <path
              d="M2 12h20M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"
              strokeWidth="1.5"
            />
          </svg>
          <span className="text-lg md:text-xl font-semibold">
            earthquake<span className="text-primary-400">.city</span>
          </span>
        </Link>

        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setIsOpen(!isOpen)}
            aria-haspopup="listbox"
            aria-expanded={isOpen}
            aria-label="Select location"
            className="flex items-center gap-2 bg-slate-800/50 border border-slate-700 text-white text-sm
                       rounded-lg px-3 py-2 cursor-pointer
                       hover:bg-slate-700/50 hover:border-slate-600
                       focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
                       transition-colors"
          >
            <span>{currentLocaleName}</span>
            <svg
              className={`w-4 h-4 text-slate-400 transition-transform ${isOpen ? "rotate-180" : ""}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {isOpen && (
            <ul
              role="listbox"
              className="absolute right-0 mt-2 w-44 bg-slate-800 border border-slate-700 rounded-lg
                         shadow-lg shadow-black/20 overflow-hidden z-50"
            >
              {locales.map((locale) => (
                <li key={locale.slug}>
                  <button
                    role="option"
                    aria-selected={locale.slug === currentLocale}
                    onClick={() => handleSelect(locale.slug)}
                    className={`w-full text-left px-4 py-2.5 text-sm transition-colors
                      ${locale.slug === currentLocale
                        ? "bg-primary-600 text-white"
                        : "text-slate-300 hover:bg-slate-700 hover:text-white"
                      }`}
                  >
                    {locale.name}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </header>
  );
}
