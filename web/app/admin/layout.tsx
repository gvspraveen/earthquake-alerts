import { Metadata } from "next";
import AdminAuth from "@/components/admin/AdminAuth";

export const metadata: Metadata = {
  title: "Admin - earthquake.city",
  description: "Admin dashboard for earthquake.city",
  robots: "noindex, nofollow",
};

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <AdminAuth>{children}</AdminAuth>;
}
