'use client';

import { useEffect, useState } from "react";
import { useUser } from "../components/UserContext";
import { useRouter } from "next/navigation";
import TransactionTable from "../components/TransactionTable";

type Account = {
  account_id: number;
  account_name: string;
  account_type: string;
  account_balance: number;
};

type Transaction = {
  transaction_id: number;
  account_id: number;
  transaction_name: string;
  transaction_amount: number;
  transaction_category: string;
  transaction_date: string;
};

export default function Dashboard() {
  const { user, logout, refreshUser } = useUser();
  const router = useRouter();
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [showTable, setShowTable] = useState<Record<number, boolean>>({});

  useEffect(() => {
    if (!user) {
      router.push("/");
    } else {
        fetchAccounts();
        fetchTransactions();    }
  }, [user]);

  const fetchAccounts = async () => {
    try {
      const res = await fetch(`http://localhost:8000/users/${user?.user_id}/accounts`);
      const data = await res.json();
      setAccounts(data);
    } catch (err) {
      console.error("Error fetching accounts:", err);
    }
  };

  const fetchTransactions = async () => {
    try {
      const res = await fetch(`http://localhost:8000/users/${user?.user_id}/transactions`);
      const data = await res.json();
      setTransactions(data);
    } catch (err) {
      console.error("Error fetching transactions:", err);
    }
  };

  const handleUpgrade = async () => {
    if (!user?.user_email) {
      alert("User email not found");
      return;
    }

    const res = await fetch("http://localhost:8000/create-checkout-session", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: user.user_email }),
    });

    const data = await res.json();
    if (res.ok) {
      window.location.href = data.checkout_url;
    } else {
      alert(data.detail || "Checkout failed");
    }
  };

  const handleLogout = () => {
    logout();
    router.push("/");
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">
        Welcome, {user?.user_name || user?.user_email}!
      </h1>

      <div className="grid grid-cols-2 gap-4">
        {accounts.map((acc) => (
          <div key={acc.account_id} className="border p-4 rounded shadow">
            <h2 className="text-lg font-semibold">{acc.account_type.toUpperCase()}</h2>
            <p className="text-sm text-gray-600">{acc.account_name}</p>
            <p className="text-xl font-bold mt-2">${acc.account_balance.toFixed(2)}</p>

            <button
              onClick={() =>
                setShowTable((prev) => ({
                  ...prev,
                  [acc.account_id]: !prev[acc.account_id],
                }))
              }
              className="bg-blue-500 text-white px-3 py-1 rounded mt-3"
            >
              {showTable[acc.account_id] ? "Hide Transactions" : "Show Transactions"}
            </button>

            {showTable[acc.account_id] && (
              <TransactionTable accountId={acc.account_id} allTransactions={transactions} />
            )}
          </div>
        ))}
      </div>

      <button
        onClick={handleLogout}
        className="bg-red-500 text-white px-4 py-2 rounded mt-6"
      >
        Logout
      </button>

      {user?.user_is_premium ? (
        <button
          onClick={() => router.push("/premium-insights")}
          className="bg-purple-600 text-white px-4 py-2 rounded mt-4"
        >
          See Premium Insights
        </button>
      ) : (
        <button
          onClick={handleUpgrade}
          className="bg-yellow-500 text-black px-4 py-2 rounded mt-4"
        >
          Upgrade to Premium
        </button>
      )}
    </div>
  );
}
