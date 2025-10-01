import React, { useState, useEffect, useCallback } from "react";
import { useAuth } from "../hooks/useAuth.js";
import shopService from "../services/shopService";
import RevenueChart from "../components/RevenueChart.jsx";
import CategoryPieChart from "../components/CategoryPieChart.jsx";
import CreateShopForm from "../components/CreateShopForm.jsx";
import Chat from "../components/Chat.jsx";

// Icons
const DollarSignIcon = () => (
  <path d="M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
);
const TrendingUpIcon = () => (
  <path d="M2.25 18L9 11.25l4.306 4.307a11.95 11.95 0 015.814-5.519l2.74-1.22m0 0l-3.75-.625m3.75.625l-6.25 3.75" />
);
const ChartBarIcon = () => (
  <path d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
);
const CubeIcon = () => (
  <path d="M21 7.5l-9-5.25L3 7.5m18 0l-9 5.25m9-5.25v9l-9 5.25M3 7.5l9 5.25M3 7.5v9l9 5.25m0-9v9" />
);

export default function OwnerDashboard() {
  const { user, token } = useAuth();
  const jwtToken = token || localStorage.getItem("token"); // JWT for RAG

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    if (!user?.shopId) {
      setLoading(false);
      return;
    }
    try {
      const dashboardData = await shopService.getOwnerDashboardData(
        user.shopId
      );
      setData(dashboardData);
    } catch (err) {
      setError("Failed to fetch dashboard data.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const formatCurrency = (amount) =>
    new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
    }).format(amount || 0);

  if (loading) {
    return <div className="text-center mt-10">Loading dashboard...</div>;
  }
  if (error) {
    return <div className="text-center mt-10 text-red-500">{error}</div>;
  }

  if (user && user.role === "owner" && !user.shopId) {
    return <CreateShopForm />;
  }

  if (!data) {
    return <div className="text-center mt-10">No data available.</div>;
  }

  const kpis = [
    {
      title: "Revenue (This Month)",
      value: formatCurrency(data.revenueThisMonth),
      icon: <DollarSignIcon />,
    },
    {
      title: "Profit (This Month)",
      value: formatCurrency(data.profitThisMonth),
      icon: <TrendingUpIcon />,
    },
    {
      title: "Units Sold (This Month)",
      value: data.unitsSoldThisMonth,
      icon: <ChartBarIcon />,
    },
    {
      title: "Total Product Types",
      value: data.totalProductTypes,
      icon: <CubeIcon />,
    },
  ];

  return (
    <div className="space-y-8 p-4 sm:p-6 lg:p-8">
      <h1 className="text-3xl font-bold text-gray-800">Dashboard</h1>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {kpis.map((kpi) => (
          <div
            key={kpi.title}
            className="bg-white p-6 rounded-2xl shadow-lg flex items-center space-x-4 transition hover:shadow-xl hover:-translate-y-1"
          >
            <div className="bg-indigo-100 text-indigo-600 rounded-full p-3">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
                className="w-8 h-8"
              >
                {kpi.icon}
              </svg>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">{kpi.title}</p>
              <p className="text-3xl font-bold text-gray-900">{kpi.value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Charts + Chat Sidebar */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Revenue Chart */}
        <div className="lg:col-span-3 bg-white p-4 rounded-lg shadow-md">
          {data.revenueTrend && data.revenueTrend.length > 0 ? (
            <RevenueChart data={data.revenueTrend} />
          ) : (
            <div className="text-center text-gray-500 py-10">
              No revenue data for the last 30 days.
            </div>
          )}
        </div>

        {/* Sidebar: Category Pie + Chat */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          {/* Category Pie Chart */}
          <div className="bg-white p-4 rounded-lg shadow-md flex-1">
            <CategoryPieChart data={data.salesByCategory} />
          </div>

          {/* RAG Chat */}
          <div className="rag-chat-widget bg-white p-4 rounded-lg shadow-md flex-1 flex flex-col">
            <h2 className="text-lg font-semibold mb-2">Shop AI Assistant</h2>
            <div className="flex-1 overflow-y-auto">
              <Chat jwtToken={jwtToken} />
            </div>
          </div>
        </div>
      </div>

      {/* Low Stock Alerts */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4 text-gray-700">
          Low Stock Alerts
        </h2>
        {data.lowStockItems.length > 0 ? (
          <ul className="divide-y divide-gray-200">
            {data.lowStockItems.map((item) => (
              <li
                key={item._id}
                className="py-3 flex justify-between items-center"
              >
                <span className="font-medium text-gray-800">{item.name}</span>
                <span className="text-sm text-red-600 font-bold">
                  Only {item.stock} left
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-500">No items are currently low on stock.</p>
        )}
      </div>
    </div>
  );
}
