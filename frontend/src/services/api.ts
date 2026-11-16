import {
  Station,
  Train,
  LiveStatusResponse,
  StationLiveBoardItem,
  ServiceAlert,
  User,
  AdminStats,
  ImportValidationResult,
  ImportResult,
  AuditLog
} from '../types';

const API_BASE = '/api/v1';

function getAuthHeader(): Record<string, string> {
  const token = localStorage.getItem('railtrack_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export const api = {
  // Authentication
  async register(data: any): Promise<User> {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Registration failed' }));
      throw new Error(err.detail || 'Registration failed');
    }
    return res.json();
  },

  async login(username: string, password: string):Promise<{ access_token: string; user: User }> {
    const res = await fetch(`${API_BASE}/auth/login/json`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(err.detail || 'Invalid username or password');
    }
    return res.json();
  },

  async getMe(): Promise<User> {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) throw new Error('Failed to fetch user profile');
    return res.json();
  },

  // Trains
  async searchTrains(params: {
    query?: string;
    source?: string;
    destination?: string;
    station?: string;
    train_type?: string;
    day?: string;
    page?: number;
    limit?: number;
  }): Promise<{ items: Train[]; total: number; page: number; limit: number; pages: number }> {
    const query = new URLSearchParams();
    if (params.query) query.append('query', params.query);
    if (params.source) query.append('source', params.source);
    if (params.destination) query.append('destination', params.destination);
    if (params.station) query.append('station', params.station);
    if (params.train_type) query.append('train_type', params.train_type);
    if (params.day) query.append('day', params.day);
    if (params.page) query.append('page', params.page.toString());
    if (params.limit) query.append('limit', params.limit.toString());

    const res = await fetch(`${API_BASE}/trains?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to search trains');
    return res.json();
  },

  async getTrainDetail(trainNumber: string): Promise<Train> {
    const res = await fetch(`${API_BASE}/trains/${encodeURIComponent(trainNumber)}`);
    if (!res.ok) throw new Error(`Train '${trainNumber}' not found`);
    return res.json();
  },

  // Live Tracking
  async getLiveStatus(trainNumber: string, options?: { date?: string; provider?: string }): Promise<LiveStatusResponse> {
    const query = new URLSearchParams();
    if (options?.date) query.append('date', options.date);
    if (options?.provider) query.append('provider', options.provider);

    const res = await fetch(`${API_BASE}/tracking/train/${encodeURIComponent(trainNumber)}/live?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to retrieve live running status');
    return res.json();
  },

  async getProviderInfo(provider?: string): Promise<{ active_provider: string; description: string; available_providers: string[]; is_live_available: boolean }> {
    const query = provider ? `?provider=${encodeURIComponent(provider)}` : '';
    const res = await fetch(`${API_BASE}/tracking/provider-info${query}`);
    if (!res.ok) throw new Error('Failed to fetch provider info');
    return res.json();
  },

  // Stations
  async getStations(query?: string, limit = 50): Promise<Station[]> {
    const params = new URLSearchParams();
    if (query) params.append('query', query);
    params.append('limit', limit.toString());

    const res = await fetch(`${API_BASE}/stations?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch stations');
    return res.json();
  },

  async getStationDetail(code: string): Promise<Station> {
    const res = await fetch(`${API_BASE}/stations/${encodeURIComponent(code)}`);
    if (!res.ok) throw new Error('Station not found');
    return res.json();
  },

  async getStationLiveBoard(code: string, provider?: string): Promise<{
    station: Station;
    arrivals: StationLiveBoardItem[];
    departures: StationLiveBoardItem[];
    provider: string;
    is_live_available: boolean;
  }> {
    const query = provider ? `?provider=${encodeURIComponent(provider)}` : '';
    const res = await fetch(`${API_BASE}/stations/${encodeURIComponent(code)}/live-board${query}`);
    if (!res.ok) throw new Error('Failed to load station live board');
    return res.json();
  },

  // Alerts
  async getAlerts(trainNumber?: string, stationCode?: string): Promise<ServiceAlert[]> {
    const params = new URLSearchParams();
    if (trainNumber) params.append('train_number', trainNumber);
    if (stationCode) params.append('station_code', stationCode);

    const res = await fetch(`${API_BASE}/alerts?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch service alerts');
    return res.json();
  },

  // Saved Trains
  async getSavedTrains(): Promise<Train[]> {
    const res = await fetch(`${API_BASE}/saved-trains`, {
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) return [];
    return res.json();
  },

  async saveTrain(trainNumber: string): Promise<void> {
    const res = await fetch(`${API_BASE}/saved-trains/${encodeURIComponent(trainNumber)}`, {
      method: 'POST',
      headers: { ...getAuthHeader() }
    });
    if (!res.ok && res.status !== 401) {
      throw new Error('Failed to bookmark train');
    }
  },

  async unsaveTrain(trainNumber: string): Promise<void> {
    const res = await fetch(`${API_BASE}/saved-trains/${encodeURIComponent(trainNumber)}`, {
      method: 'DELETE',
      headers: { ...getAuthHeader() }
    });
    if (!res.ok && res.status !== 401) {
      throw new Error('Failed to remove bookmark');
    }
  },

  // Admin APIs
  async getAdminStats(): Promise<AdminStats> {
    const res = await fetch(`${API_BASE}/admin/stats`, {
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) throw new Error('Unauthorized or failed to load stats');
    return res.json();
  },

  async validateImport(entityType: string, file: File): Promise<ImportValidationResult> {
    const formData = new FormData();
    formData.append('entity_type', entityType);
    formData.append('file', file);

    const res = await fetch(`${API_BASE}/admin/import/validate`, {
      method: 'POST',
      headers: { ...getAuthHeader() },
      body: formData
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Validation failed' }));
      throw new Error(err.detail || 'Validation failed');
    }
    return res.json();
  },

  async executeImport(entityType: string, file: File): Promise<ImportResult> {
    const formData = new FormData();
    formData.append('entity_type', entityType);
    formData.append('file', file);

    const res = await fetch(`${API_BASE}/admin/import/execute`, {
      method: 'POST',
      headers: { ...getAuthHeader() },
      body: formData
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Import failed' }));
      throw new Error(err.detail || 'Import failed');
    }
    return res.json();
  },

  async getAuditLogs(): Promise<AuditLog[]> {
    const res = await fetch(`${API_BASE}/admin/audit-logs`, {
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) throw new Error('Failed to fetch audit logs');
    return res.json();
  },

  async getImportTemplate(entityType: string, format: 'csv' | 'json'): Promise<string> {
    const res = await fetch(`${API_BASE}/admin/import/template/${entityType}?format=${format}`);
    if (!res.ok) throw new Error('Template not found');
    return res.text();
  }
};
