"use client";

import { useEffect, useState } from "react";
import { useUser } from "../components/UserContext";
import { useRouter } from "next/navigation";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
const COLORS = ["#8884d8", "#82ca9d", "#ffc658", "#ff8042", "#d0ed57"];

type Insight = {
  weekly_spending: {
    range: string;
    total: number;
    change?: number | null;
  }[];
  top_categories: { category: string; total: number }[];
  top_merchants: { merchant: string; total: number }[];
  average_transaction: number;
  expensive_transactions: {
    name: string;
    amount: number;
    category: string;
    date: string;
  }[];
};

export default function PremiumInsights() {
  const { user } = useUser();
  const router = useRouter();
  const [insights, setInsights] = useState<Insight | null>(null);

  useEffect(() => {
    if (!user) {
      router.push("/");
    } else if (!user.user_is_premium) {
      router.push("/dashboard");
    } else {
      fetchInsights();
    }
  }, [user]);

  const fetchInsights = async () => {
    try {
      const res = await fetch(
        `http://localhost:8000/users/${user?.user_id}/insights`
      );
      const data = await res.json();
      setInsights(data);
    } catch (err) {
      console.error("Error fetching insights:", err);
    }
  };

  if (!insights) {
    return (
      <div className="p-8 text-center">
        <h1 className="text-xl font-semibold">Loading premium insights...</h1>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">💡 Premium Insights</h1>

      {/* Weekly Spending Chart */}
      <section className="mb-8">
        <h2 className="text-lg font-semibold mb-2">Weekly Spending Overview</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={insights.weekly_spending}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="range" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="total" fill="#8884d8" />
          </BarChart>
        </ResponsiveContainer>
        <ul className="mt-4 list-disc pl-6 text-sm text-gray-700">
          {insights.weekly_spending.map((week, i) => (
            <li key={i}>
              {week.range}: ${week.total.toFixed(2)}{" "}
              {week.change !== undefined && week.change !== null && (
                <span
                  className={
                    week.change > 0 ? "text-red-600" : "text-green-600"
                  }
                >
                  ({week.change > 0 ? "↑" : "↓"} {Math.abs(week.change)}%)
                </span>
              )}
            </li>
          ))}
        </ul>
      </section>

      {/* Top Categories */}
      {/* Top Categories */}
      <section className="mb-8">
        <h2 className="text-lg font-semibold mb-2">Top Categories</h2>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={insights.top_categories}
              dataKey="total"
              nameKey="category"
              outerRadius={100}
              label
            >
              {insights.top_categories.map((_, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[index % COLORS.length]}
                />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </section>

      {/* Top Merchants */}
      {/* Top Merchants */}
      <section className="mb-8">
        <h2 className="text-lg font-semibold mb-2">Top Merchants</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={insights.top_merchants}>
            <XAxis dataKey="merchant" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="total" fill="#8884d8" />
          </BarChart>
        </ResponsiveContainer>
      </section>

      {/* Average Transaction */}
      <section className="mb-6">
        <h2 className="text-lg font-semibold mb-2">
          Average Transaction Value
        </h2>
        <p className="text-gray-700">
          ${insights.average_transaction.toFixed(2)}
        </p>
      </section>

      {/* Expensive Transactions */}
      <section className="mb-6">
        <h2 className="text-lg font-semibold mb-2">
          Flagged Expensive Transactions
        </h2>
        <ul className="list-disc pl-6">
          {insights.expensive_transactions.map((tx, i) => (
            <li key={i}>
              {tx.name} — ${tx.amount.toFixed(2)} on{" "}
              {new Date(tx.date).toLocaleDateString()} ({tx.category})
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
