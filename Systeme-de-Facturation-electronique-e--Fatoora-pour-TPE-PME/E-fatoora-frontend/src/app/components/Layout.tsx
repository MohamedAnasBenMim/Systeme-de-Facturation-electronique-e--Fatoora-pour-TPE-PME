import { Outlet } from "react-router";
import { Sidebar } from "./Sidebar";
import { Navbar } from "./Navbar";

export function Layout() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      <div className="ml-64">
        <Navbar />
        <main className="p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
