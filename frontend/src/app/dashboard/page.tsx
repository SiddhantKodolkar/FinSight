"use client";

import { useEffect, useState } from "react";
import { useUser } from "../components/UserContext";
import { useRouter } from "next/navigation";

type Account = {
  account_id: number;
  account_name: string;
  account_type: string;
  account_balance: number;
};

export default function Dashboard() {
  const { user, logout } = useUser();
  const router = useRouter();
  const [accounts, setAccounts] = useState<Account[]>([]);

  useEffect(() => {
    if (!user) {
      router.push("/");
    } else {
      fetchAccounts();
    }
  }, [user]);

  const fetchAccounts = async () => {
    try {
      const res = await fetch(
        `http://localhost:8000/users/${user?.user_id}/accounts`
      );
      if (!res.ok) throw new Error("Failed to fetch accounts");

      const data = await res.json();
      if (Array.isArray(data)) {
        setAccounts(data);
      } else {
        console.error("Expected array but got:", data);
      }
    } catch (err) {
      console.error("Error fetching accounts:", err);
    }
  };

  const handleLogout = () => {
    logout();
    router.push("/");
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold">
        Welcome, {user?.user_name || user?.user_email}!
      </h1>

      {/* 💳 Account Boxes */}
      <div className="grid grid-cols-2 gap-4 mt-6">
        {accounts.map((account) => (
          <div key={account.account_id} className="border p-4 rounded shadow">
            <h2 className="text-lg font-semibold">
              {account.account_type.toUpperCase()}
            </h2>
            <p className="text-sm text-gray-600">{account.account_name}</p>
            <p className="text-xl font-bold mt-2">
              ${account.account_balance.toFixed(2)}
            </p>
          </div>
        ))}
      </div>

      <button
        onClick={handleLogout}
        className="bg-red-500 text-white px-4 py-2 rounded mt-6"
      >
        Logout
      </button>
    </div>
  );
}
