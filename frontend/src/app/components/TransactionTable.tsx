'use client';
import { useState, useMemo } from "react";

type Transaction = {
  transaction_id: number;
  account_id: number;
  transaction_name: string;
  transaction_amount: number;
  transaction_category: string;
  transaction_date: string;
};

type Props = {
  accountId: number;
  allTransactions: Transaction[];
};

export default function TransactionTable({ accountId, allTransactions }: Props) {
  const [categoryFilter, setCategoryFilter] = useState("");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [amountRange, setAmountRange] = useState("");

  const categories = Array.from(
    new Set(allTransactions.map((t) => t.transaction_category))
  );

  const filtered = useMemo(() => {
    let txns = allTransactions.filter((t) => t.account_id === accountId);

    if (categoryFilter) {
      txns = txns.filter((t) => t.transaction_category === categoryFilter);
    }

    if (amountRange) {
      const [min, max] = amountRange.split("-").map(Number);
      txns = txns.filter((t) => t.transaction_amount >= min && t.transaction_amount < max);
    }

    txns.sort((a, b) =>
      sortOrder === "asc"
        ? new Date(a.transaction_date).getTime() - new Date(b.transaction_date).getTime()
        : new Date(b.transaction_date).getTime() - new Date(a.transaction_date).getTime()
    );

    return txns;
  }, [accountId, allTransactions, categoryFilter, sortOrder, amountRange]);

  const resetFilters = () => {
    setCategoryFilter("");
    setSortOrder("desc");
    setAmountRange("");
  };

  return (
    <div className="mt-4">
      {/* 🔍 Filter Controls */}
      <div className="flex flex-wrap gap-3 items-center mb-4">
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="border p-1"
        >
          <option value="">All Categories</option>
          {categories.map((cat) => (
            <option key={cat}>{cat}</option>
          ))}
        </select>

        <select
          value={sortOrder}
          onChange={(e) => setSortOrder(e.target.value as "asc" | "desc")}
          className="border p-1"
        >
          <option value="desc">Latest First</option>
          <option value="asc">Earliest First</option>
        </select>

        <select
          value={amountRange}
          onChange={(e) => setAmountRange(e.target.value)}
          className="border p-1"
        >
          <option value="">All Amounts</option>
          <option value="0-100">$0 - $100</option>
          <option value="100-200">$100 - $200</option>
          <option value="200-300">$200 - $300</option>
          <option value="300-400">$300 - $400</option>
          <option value="400-500">$400 - $500</option>
        </select>

        <button
          onClick={resetFilters}
          className="text-sm px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
        >
          Reset Filters
        </button>
      </div>

      {/* 📄 Transactions Table */}
      <table className="w-full text-sm text-left border">
        <thead className="bg-gray-100 text-gray-700">
          <tr>
            <th className="p-2 border">Name</th>
            <th className="p-2 border">Amount</th>
            <th className="p-2 border">Category</th>
            <th className="p-2 border">Date</th>
          </tr>
        </thead>
        <tbody>
          {filtered.map((txn) => (
            <tr key={txn.transaction_id} className="hover:bg-gray-50">
              <td className="p-2 border">{txn.transaction_name}</td>
              <td className="p-2 border">${txn.transaction_amount.toFixed(2)}</td>
              <td className="p-2 border">{txn.transaction_category}</td>
              <td className="p-2 border">{new Date(txn.transaction_date).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {filtered.length === 0 && (
        <p className="text-gray-500 text-sm mt-2">No transactions found.</p>
      )}
    </div>
  );
}
