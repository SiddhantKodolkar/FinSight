'use client';

import { useEffect } from "react";
import { useUser } from "../components/UserContext";
import { useRouter } from "next/navigation";

export default function Dashboard() {
  const { user, logout } = useUser();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push("/"); // Redirect to login
  };

  useEffect(() => {
    if (!user) {
      router.push("/");
    }
  }, [user]);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold">Welcome, {user?.name || user?.email}!</h1>
      <button
        onClick={handleLogout}
        className="bg-red-500 text-white px-4 py-2 rounded mt-4"
      >
        Logout
      </button>
    </div>
  );
}
