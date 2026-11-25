/**
 * AI-Powered Electronics Rental and Revenue Intelligence API Service
 * Centralized API client for backend communication
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Types for API responses
export interface DashboardMetrics {
  total_revenue: number;
  total_rentals: number;
  active_rentals: number;
  available_items: number;
  overdue_rentals: number;
  revenue_growth: number;
}

export interface RevenueData {
  month: string;
  revenue: number;
  rentals: number;
}

export interface RevenueAnalytics {
  period: string;
  total_revenue: number;
  monthly_breakdown: RevenueData[];
  avg_monthly_revenue: number;
}

export interface ProductAnalytics {
  product_id: string;
  name: string;
  total_rentals: number;
  total_rental_days: number;
  total_revenue: number;
  utilization_rate: number;
  available_quantity: number;
  category_id?: string;
}

export interface ProductAnalyticsResponse {
  products: ProductAnalytics[];
  avg_utilization: number;
}

export interface CustomerAnalytics {
  total_customers: number;
  active_customers: number;
  segment_distribution: {
    new: number;
    regular: number;
    premium: number;
    vip: number;
  };
  retention_rate: number;
  avg_lifetime_value: number;
  avg_rental_duration: number;
}

export interface DemandForecast {
  date: string;
  predicted_demand: number;
  confidence_lower: number;
  confidence_upper: number;
  category_id?: string;
  forecast_day?: number;
  confidence_interval?: {
    lower: number;
    upper: number;
    std: number;
  };
}

export interface CategoryForecast {
  category_id: string;
  forecasts: Array<{
    date: string;
    predicted_demand: number;
    confidence: number;
    trend: string;
  }>;
  avg_demand: number;
  peak_day: string;
}

export interface PricingRecommendation {
  product_id: string;
  product_name: string;
  current_rate: number;
  recommended_rate: number;
  price_change_percent: number;
  confidence: number;
  reason: string;
}

export interface PricingResponse {
  recommendations: PricingRecommendation[];
  total_products: number;
  avg_price_change: number;
}

export interface ProductPricing {
  product_id: string;
  name: string;
  current_rate: number;
  recommended_rate: number;
  price_change_percent: number;
  factors: {
    demand_factor: number;
    availability_factor: number;
    seasonality_factor: number;
  };
  confidence: number;
  min_acceptable: number;
  max_recommended: number;
}

export interface BusinessInsight {
  type: string;
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  action: string;
}

export interface BusinessInsightsResponse {
  summary: {
    total_revenue: number;
    total_rentals: number;
    avg_rental_value: number;
    growth_rate: number;
  };
  insights: BusinessInsight[];
}

export interface RevenueOpportunity {
  product_id: string;
  name: string;
  current_revenue: number;
  potential_increase: number;
  strategy: string;
  priority: string;
}

export interface OpportunitiesResponse {
  opportunities: RevenueOpportunity[];
  total_potential: number;
  top_priority: RevenueOpportunity | null;
}

// API Error class
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public details?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// API Client
class ApiClient {
  private baseUrl: string;
  private defaultHeaders: HeadersInit;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const config: RequestInit = {
      ...options,
      headers: {
        ...this.defaultHeaders,
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const errorText = await response.text();
        let errorDetails;
        
        try {
          errorDetails = JSON.parse(errorText);
        } catch {
          errorDetails = errorText;
        }

        throw new ApiError(
          `API Error: ${response.status} ${response.statusText}`,
          response.status,
          errorDetails
        );
      }

      // Handle empty responses
      const text = await response.text();
      if (!text) {
        return {} as T;
      }

      return JSON.parse(text);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      
      // Network errors
      throw new ApiError(
        `Network Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        0
      );
    }
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return this.request('/api/health');
  }

  // Analytics Endpoints
  async getDashboardMetrics(): Promise<DashboardMetrics> {
    return this.request('/api/analytics/dashboard');
  }

  async getRevenueAnalytics(period: string = 'monthly'): Promise<RevenueAnalytics> {
    return this.request(`/api/analytics/revenue?period=${period}`);
  }

  async getProductAnalytics(): Promise<ProductAnalyticsResponse> {
    return this.request('/api/analytics/products');
  }

  async getCustomerAnalytics(): Promise<CustomerAnalytics> {
    return this.request('/api/analytics/customers');
  }

  // Demand Forecasting Endpoints
  async getDemandForecast(days: number = 14): Promise<DemandForecast[]> {
    return this.request(`/api/forecasting/demand?days=${days}`);
  }

  async getCategoryForecast(categoryId: string, days: number = 7): Promise<CategoryForecast> {
    return this.request(`/api/forecasting/category/${categoryId}?days=${days}`);
  }

  // Pricing Endpoints
  async getPricingRecommendations(): Promise<PricingResponse> {
    return this.request('/api/pricing/recommendations');
  }

  async getProductPricing(productId: string): Promise<ProductPricing> {
    return this.request(`/api/pricing/product/${productId}`);
  }

  // Business Intelligence Endpoints
  async getBusinessInsights(): Promise<BusinessInsightsResponse> {
    return this.request('/api/business/insights');
  }

  async getRevenueOpportunities(): Promise<OpportunitiesResponse> {
    return this.request('/api/business/opportunities');
  }

  // ML Endpoints
  async getCustomerSegment(customerId: string): Promise<{
    customer_id: string;
    segment: string;
    description: string;
    benefits: string[];
    recommended_actions: string[];
  }> {
    return this.request(`/api/ml/segmentation/${customerId}`);
  }

  async getProductRecommendations(
    customerId?: string,
    productId?: string,
    categoryId?: string,
    n: number = 5
  ): Promise<Array<{
    product_id: string;
    combined_score: number;
    content_score: number;
    collaborative_score: number;
    daily_rate: number;
    category_id: string | null;
  }>> {
    let endpoint = `/api/ml/recommendations?n=${n}`;
    if (customerId) endpoint += `&customer_id=${customerId}`;
    if (productId) endpoint += `&product_id=${productId}`;
    if (categoryId) endpoint += `&category_id=${categoryId}`;
    return this.request(endpoint);
  }

  async getMLStatus(): Promise<{
    models: Record<string, {
      name: string;
      status: string;
      last_trained: string | null;
      metrics: Record<string, unknown>;
    }>;
    scheduler: {
      running: boolean;
      jobs: number;
    };
    training_history: Array<{
      job_name: string;
      timestamp: string;
      results: Record<string, unknown>;
      status: string;
    }>;
  }> {
    return this.request('/api/ml/status');
  }

  async trainMLModels(): Promise<Record<string, {
    status: string;
    metrics?: Record<string, unknown>;
    error?: string;
  }>> {
    return this.request('/api/ml/train', {
      method: 'POST',
    });
  }
}

// Export singleton instance
export const api = new ApiClient();

// Export class for custom instances
export { ApiClient };

// Helper functions for common operations
export const analyticsApi = {
  async getFullDashboard() {
    const [metrics, revenue, products, customers] = await Promise.all([
      api.getDashboardMetrics(),
      api.getRevenueAnalytics(),
      api.getProductAnalytics(),
      api.getCustomerAnalytics(),
    ]);
    return { metrics, revenue, products, customers };
  },

  async getAllForecasts(days: number = 14) {
    const [demand, pricing, insights, opportunities] = await Promise.all([
      api.getDemandForecast(days),
      api.getPricingRecommendations(),
      api.getBusinessInsights(),
      api.getRevenueOpportunities(),
    ]);
    return { demand, pricing, insights, opportunities };
  },
};

export const mlApi = {
  async getStatus() {
    return api.getMLStatus();
  },

  async trainModels() {
    return api.trainMLModels();
  },

  async getRecommendations(
    customerId?: string,
    productId?: string,
    categoryId?: string,
    n: number = 5
  ) {
    return api.getProductRecommendations(customerId, productId, categoryId, n);
  },

  async getCustomerSegment(customerId: string) {
    return api.getCustomerSegment(customerId);
  },
};