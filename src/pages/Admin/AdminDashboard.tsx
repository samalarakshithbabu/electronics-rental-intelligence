/**
 * AI-Powered Electronics Rental and Revenue Intelligence - Admin Dashboard
 * Premium analytics and business intelligence interface
 */
import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import {
  DollarSign, Package, AlertTriangle,
  Activity, Zap, Target, ChevronRight, RefreshCw,
  ArrowUpRight, ShoppingCart
} from 'lucide-react';
import { motion } from 'framer-motion';
import { Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, AreaChart, Area } from 'recharts';

// Types
interface DashboardMetrics {
  total_revenue: number;
  total_rentals: number;
  active_rentals: number;
  available_items: number;
  overdue_rentals: number;
  revenue_growth: number;
}

interface DemandForecast {
  date: string;
  predicted_demand: number;
  confidence_lower: number;
  confidence_upper: number;
}

interface PricingRecommendation {
  product_id: string;
  product_name: string;
  current_rate: number;
  recommended_rate: number;
  price_change_percent: number;
  confidence: number;
  reason: string;
}

interface BusinessInsight {
  type: string;
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  action: string;
}

interface ProductAnalytics {
  product_id: string;
  name: string;
  total_rentals: number;
  total_rental_days: number;
  total_revenue: number;
  utilization_rate: number;
  available_quantity: number;
}

// Mock data for demonstration
const mockRevenueData = [
  { month: 'Jan', revenue: 12500, rentals: 45 },
  { month: 'Feb', revenue: 15800, rentals: 52 },
  { month: 'Mar', revenue: 18200, rentals: 61 },
  { month: 'Apr', revenue: 21500, rentals: 68 },
  { month: 'May', revenue: 24800, rentals: 75 },
  { month: 'Jun', revenue: 28900, rentals: 82 },
  { month: 'Jul', revenue: 32100, rentals: 91 },
  { month: 'Aug', revenue: 35800, rentals: 98 },
  { month: 'Sep', revenue: 39200, rentals: 105 },
  { month: 'Oct', revenue: 43500, rentals: 118 },
  { month: 'Nov', revenue: 48200, rentals: 132 },
  { month: 'Dec', revenue: 54500, rentals: 148 },
];

const mockCategoryData = [
  { name: 'Laptops', value: 35, color: '#6366f1' },
  { name: 'Cameras', value: 25, color: '#8b5cf6' },
  { name: 'Audio', value: 15, color: '#ec4899' },
  { name: 'Gaming', value: 15, color: '#f59e0b' },
  { name: 'Tablets', value: 10, color: '#10b981' },
];

const API_BASE = 'http://localhost:8000/api';

// API Service - connects to actual backend
const api = {
  async getDashboardMetrics(): Promise<DashboardMetrics> {
    const response = await fetch(`${API_BASE}/analytics/dashboard`);
    if (!response.ok) throw new Error('Failed to fetch metrics');
    return response.json();
  },

  async getRevenueAnalytics(): Promise<{ monthly_breakdown: typeof mockRevenueData }> {
    const response = await fetch(`${API_BASE}/analytics/revenue`);
    if (!response.ok) throw new Error('Failed to fetch revenue analytics');
    const data = await response.json();
    // Transform backend data to match frontend format
    return {
      monthly_breakdown: data.monthly_breakdown.map((item: any) => ({
        month: item.month.split('-')[1], // Just show month number
        revenue: item.revenue,
        rentals: item.rentals
      }))
    };
  },

  async getProductAnalytics(): Promise<{ products: ProductAnalytics[] }> {
    const response = await fetch(`${API_BASE}/analytics/products`);
    if (!response.ok) throw new Error('Failed to fetch product analytics');
    return response.json();
  },

  async getDemandForecast(days: number = 14): Promise<DemandForecast[]> {
    const response = await fetch(`${API_BASE}/forecasting/demand?days=${days}`);
    if (!response.ok) throw new Error('Failed to fetch demand forecast');
    const data = await response.json();
    return data.map((item: any) => ({
      date: item.date,
      predicted_demand: item.predicted_demand,
      confidence_lower: item.confidence_lower,
      confidence_upper: item.confidence_upper
    }));
  },

  async getPricingRecommendations(): Promise<{ recommendations: PricingRecommendation[] }> {
    const response = await fetch(`${API_BASE}/pricing/recommendations`);
    if (!response.ok) throw new Error('Failed to fetch pricing recommendations');
    return response.json();
  },

  async getBusinessInsights(): Promise<{ insights: BusinessInsight[] }> {
    const response = await fetch(`${API_BASE}/business/insights`);
    if (!response.ok) throw new Error('Failed to fetch business insights');
    const data = await response.json();
    return { insights: data.insights };
  },

  async getCategoryDistribution(): Promise<{ categories: { name: string; value: number; color: string }[] }> {
    const response = await fetch(`${API_BASE}/analytics/categories`);
    if (!response.ok) throw new Error('Failed to fetch category data');
    return response.json();
  }
};

// Main Dashboard Component
export const AdminDashboard = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [revenueData] = useState(mockRevenueData);
  const [productAnalytics, setProductAnalytics] = useState<{ products: ProductAnalytics[] }>({ products: [] });
  const [demandForecast, setDemandForecast] = useState<DemandForecast[]>([]);
  const [pricingRecs, setPricingRecs] = useState<{ recommendations: PricingRecommendation[] }>({ recommendations: [] });
  const [insights, setInsights] = useState<{ insights: BusinessInsight[] }>({ insights: [] });
  const [categoryData, setCategoryData] = useState<{ categories: { name: string; value: number; color: string }[] }>({ categories: mockCategoryData });
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [metricsData, productData, forecastData, pricingData, insightsData, categoryDist] = await Promise.all([
        api.getDashboardMetrics(),
        api.getProductAnalytics(),
        api.getDemandForecast(14),
        api.getPricingRecommendations(),
        api.getBusinessInsights(),
        api.getCategoryDistribution().catch(() => ({ categories: mockCategoryData }))
      ]);

      setMetrics(metricsData);
      setProductAnalytics(productData);
      setDemandForecast(forecastData);
      setPricingRecs(pricingData);
      setInsights(insightsData);
      setCategoryData(categoryDist);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 60000);
    return () => clearInterval(interval);
  }, [loadData]);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  if (loading && !metrics) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">AI-Powered Electronics Rental and Revenue Intelligence Dashboard</h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Smart Rental & Revenue Intelligence Platform
              </p>
            </div>
            <div className="flex items-center gap-4">
              <Link to="/" className="text-sm text-indigo-600 dark:text-indigo-400 hover:underline">
                Back to Home
              </Link>
              <button
                onClick={loadData}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition"
              >
                <RefreshCw className={`h-5 w-5 text-gray-600 dark:text-gray-400 ${loading ? 'animate-spin' : ''}`} />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        >
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-100 dark:border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-lg bg-emerald-500 bg-opacity-10">
                <DollarSign className="h-6 w-6 text-emerald-500" />
              </div>
              <div className="flex items-center text-sm font-medium text-green-500">
                <ArrowUpRight className="h-4 w-4 mr-1" />
                {metrics?.revenue_growth}%
              </div>
            </div>
            <h3 className="text-gray-500 dark:text-gray-400 text-sm font-medium">Total Revenue</h3>
            <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{formatCurrency(metrics?.total_revenue || 0)}</p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-100 dark:border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-lg bg-blue-500 bg-opacity-10">
                <ShoppingCart className="h-6 w-6 text-blue-500" />
              </div>
              <div className="flex items-center text-sm font-medium text-green-500">
                <ArrowUpRight className="h-4 w-4 mr-1" />
                8.2%
              </div>
            </div>
            <h3 className="text-gray-500 dark:text-gray-400 text-sm font-medium">Total Rentals</h3>
            <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{metrics?.total_rentals || 0}</p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-100 dark:border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-lg bg-purple-500 bg-opacity-10">
                <Activity className="h-6 w-6 text-purple-500" />
              </div>
            </div>
            <h3 className="text-gray-500 dark:text-gray-400 text-sm font-medium">Active Rentals</h3>
            <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{metrics?.active_rentals || 0}</p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-100 dark:border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-lg bg-red-500 bg-opacity-10">
                <AlertTriangle className="h-6 w-6 text-red-500" />
              </div>
            </div>
            <h3 className="text-gray-500 dark:text-gray-400 text-sm font-medium">Overdue Returns</h3>
            <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{metrics?.overdue_rentals || 0}</p>
          </div>
        </motion.div>

        {/* Revenue Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-100 dark:border-gray-700 mb-8"
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Revenue Overview</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">Monthly revenue and rental trends</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-indigo-500"></div>
                <span className="text-sm text-gray-600 dark:text-gray-400">Revenue</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
                <span className="text-sm text-gray-600 dark:text-gray-400">Rentals</span>
              </div>
            </div>
          </div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={revenueData}>
                <defs>
                  <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="month" stroke="#9ca3af" fontSize={12} />
                <YAxis yAxisId="left" stroke="#9ca3af" fontSize={12} tickFormatter={(v: number) => `$${(v/1000).toFixed(0)}k`} />
                <YAxis yAxisId="right" orientation="right" stroke="#9ca3af" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1f2937',
                    border: 'none',
                    borderRadius: '8px',
                    color: '#fff'
                  }}
                />
                <Area yAxisId="left" type="monotone" dataKey="revenue" stroke="#6366f1" strokeWidth={2} fill="url(#colorRevenue)" />
                <Line yAxisId="right" type="monotone" dataKey="rentals" stroke="#10b981" strokeWidth={2} dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Second Row - Demand Forecast & Category */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Demand Forecast */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-100 dark:border-gray-700"
          >
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Demand Forecast</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">AI-powered prediction for next 14 days</p>
              </div>
              <div className="flex items-center gap-2 text-sm text-indigo-600 dark:text-indigo-400">
                <Activity className="h-4 w-4" />
                <span>ML Model: GradientBoosting</span>
              </div>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={demandForecast.slice(0, 14)}>
                  <defs>
                    <linearGradient id="colorDemand" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="date" stroke="#9ca3af" fontSize={10} tickFormatter={(v: string) => v.slice(5)} />
                  <YAxis stroke="#9ca3af" fontSize={12} domain={[0, 'auto']} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1f2937',
                      border: 'none',
                      borderRadius: '8px',
                      color: '#fff'
                    }}
                  />
                  <Area type="monotone" dataKey="predicted_demand" stroke="#f59e0b" strokeWidth={2} fill="url(#colorDemand)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Category Distribution */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-100 dark:border-gray-700"
          >
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Category Distribution</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">Revenue by product category</p>
              </div>
              <Package className="h-5 w-5 text-gray-400" />
            </div>
            <div className="h-64 flex items-center">
              <ResponsiveContainer width="50%" height="100%">
                <PieChart>
                  <Pie
                    data={categoryData.categories}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {categoryData.categories.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1f2937',
                      border: 'none',
                      borderRadius: '8px',
                      color: '#fff'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex-1 pl-4 space-y-2">
                {categoryData.categories.map((cat) => (
                  <div key={cat.name} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: cat.color }}></div>
                      <span className="text-sm text-gray-600 dark:text-gray-400">{cat.name}</span>
                    </div>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">{cat.value}%</span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>

        {/* Insights & Pricing */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Business Insights */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-100 dark:border-gray-700"
          >
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Business Intelligence</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">AI-generated actionable insights</p>
              </div>
              <div className="flex items-center gap-2 text-sm text-emerald-600 dark:text-emerald-400">
                <Zap className="h-4 w-4" />
                <span>AI Powered</span>
              </div>
            </div>
            <div className="space-y-4">
              {insights.insights.map((insight) => (
                <div
                  key={insight.type}
                  className={`p-4 rounded-lg border-l-4 ${
                    insight.impact === 'high' ? 'border-l-red-500 bg-red-50 dark:bg-red-900/20' :
                    insight.impact === 'medium' ? 'border-l-amber-500 bg-amber-50 dark:bg-amber-900/20' :
                    'border-l-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white">{insight.title}</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{insight.description}</p>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      insight.impact === 'high' ? 'bg-red-100 text-red-700' :
                      insight.impact === 'medium' ? 'bg-amber-100 text-amber-700' :
                      'bg-blue-100 text-blue-700'
                    }`}>
                      {insight.impact}
                    </span>
                  </div>
                  <div className="mt-3 flex items-center text-sm text-indigo-600 dark:text-indigo-400">
                    <Target className="h-4 w-4 mr-1" />
                    {insight.action}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Pricing Recommendations */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-100 dark:border-gray-700"
          >
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Dynamic Pricing</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">AI-optimized pricing recommendations</p>
              </div>
              <span className="px-3 py-1 bg-indigo-100 dark:bg-indigo-900 text-indigo-600 dark:text-indigo-300 rounded-full text-sm font-medium">
                {pricingRecs.recommendations.length} recommendations
              </span>
            </div>
            <div className="space-y-4">
              {pricingRecs.recommendations.map((rec) => (
                <div
                  key={rec.product_id}
                  className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-100 dark:border-gray-600"
                >
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-900 dark:text-white">{rec.product_name}</h4>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      rec.price_change_percent > 0 ? 'bg-green-100 text-green-700' :
                      rec.price_change_percent < 0 ? 'bg-red-100 text-red-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {rec.price_change_percent > 0 ? '+' : ''}{rec.price_change_percent}%
                    </span>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                    <span>Current: <span className="font-medium text-gray-900 dark:text-white">${rec.current_rate}</span></span>
                    <span>→</span>
                    <span>Recommended: <span className="font-medium text-indigo-600 dark:text-indigo-400">${rec.recommended_rate}</span></span>
                  </div>
                  <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">{rec.reason}</p>
                  <div className="mt-2 flex items-center gap-2">
                    <div className="flex-1 h-1.5 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-indigo-500 rounded-full"
                        style={{ width: `${rec.confidence * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-500">{Math.round(rec.confidence * 100)}% confidence</span>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Product Performance Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-100 dark:border-gray-700"
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Product Performance</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">Top performing products by utilization</p>
            </div>
            <button className="flex items-center gap-2 text-sm text-indigo-600 dark:text-indigo-400 hover:text-indigo-700">
              View All <ChevronRight className="h-4 w-4" />
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-sm text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-700">
                  <th className="pb-3 font-medium">Product</th>
                  <th className="pb-3 font-medium text-right">Rentals</th>
                  <th className="pb-3 font-medium text-right">Revenue</th>
                  <th className="pb-3 font-medium text-right">Utilization</th>
                  <th className="pb-3 font-medium text-right">Status</th>
                </tr>
              </thead>
              <tbody>
                {productAnalytics.products.map((product) => (
                  <tr
                    key={product.product_id}
                    className="border-b border-gray-100 dark:border-gray-700 last:border-0"
                  >
                    <td className="py-3 font-medium text-gray-900 dark:text-white">{product.name}</td>
                    <td className="py-3 text-right text-gray-600 dark:text-gray-400">{product.total_rentals}</td>
                    <td className="py-3 text-right font-medium text-gray-900 dark:text-white">${product.total_revenue.toLocaleString()}</td>
                    <td className="py-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <div className="w-16 h-2 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              product.utilization_rate > 80 ? 'bg-green-500' :
                              product.utilization_rate > 60 ? 'bg-amber-500' :
                              'bg-red-500'
                            }`}
                            style={{ width: `${product.utilization_rate}%` }}
                          />
                        </div>
                        <span className="text-sm text-gray-600 dark:text-gray-400 w-12">{product.utilization_rate}%</span>
                      </div>
                    </td>
                    <td className="py-3 text-right">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        product.available_quantity > 3 ? 'bg-green-100 text-green-700' :
                        product.available_quantity > 0 ? 'bg-amber-100 text-amber-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                        {product.available_quantity > 3 ? 'Available' :
                         product.available_quantity > 0 ? 'Low Stock' : 'Out of Stock'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500 dark:text-gray-400">
          <p>Last updated: {lastUpdated.toLocaleTimeString()} | AI-Powered Electronics Rental and Revenue Intelligence v1.0.0</p>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;