export interface Station {
  code: string;
  name: string;
  state?: string;
  district?: string;
  division?: string;
  zone?: string;
  latitude: number;
  longitude: number;
  category?: 'Terminal' | 'Junction' | 'Suburban' | 'Regular' | 'Halt' | string;
  platforms_count?: number;
  facilities?: string[] | null;
  operational_status?: string;
  total_trains_count?: number;
  created_at?: string;
}

export interface Stop {
  id: number;
  station_code: string;
  stop_sequence: number;
  arrival_time?: string | null;
  departure_time?: string | null;
  halt_minutes: number;
  distance_km: number;
  distance_from_prev?: number;
  day_number: number;
  platform?: string | null;
  station?: Station;
}

export interface Train {
  id: number;
  train_number: string;
  train_name: string;
  short_name?: string | null;
  train_type: string;
  train_category?: string;
  source_station_code: string;
  destination_station_code: string;
  running_days: string;
  total_distance_km: number;
  duration_minutes: number;
  classes?: string[];
  pantry_car: boolean;
  return_train_number?: string | null;
  validity_start?: string | null;
  validity_end?: string | null;
  is_special?: boolean;
  is_active?: boolean;
  source_of_data?: string;
  last_verified_date?: string | null;
  aliases?: string[] | null;
  tags?: string[] | null;
  source_station?: Station;
  destination_station?: Station;
  stops?: Stop[];
}

export interface LiveStatusStop {
  station_code: string;
  station_name: string;
  stop_sequence: number;
  scheduled_arrival?: string | null;
  scheduled_departure?: string | null;
  actual_arrival?: string | null;
  actual_departure?: string | null;
  delay_arrival_minutes: number;
  delay_departure_minutes: number;
  halt_minutes: number;
  distance_km: number;
  day_number: number;
  platform?: string | null;
  platform_source: 'scheduled' | 'verified_feed' | 'estimated';
  status: 'PASSED' | 'CURRENT' | 'UPCOMING' | 'CANCELLED';
  latitude: number;
  longitude: number;
}

export interface LiveStatusResponse {
  train_number: string;
  train_name: string;
  train_type: string;
  journey_date: string;
  source_station: Station;
  destination_station: Station;
  is_live_available: boolean;
  provider_name: string;
  data_provenance: 'demo_simulation' | 'verified_live_feed' | 'scheduled_timetable_only' | 'unavailable';
  status_summary: string;
  current_status_description: string;
  delay_minutes: number;
  speed_kmh?: number | null;
  last_reported_station?: string | null;
  last_reported_time?: string | null;
  next_station?: string | null;
  eta_next_station?: string | null;
  current_latitude?: number | null;
  current_longitude?: number | null;
  progress_percentage: number;
  last_updated_timestamp: string;
  stops: LiveStatusStop[];
}

export interface StationLiveBoardItem {
  train_number: string;
  train_name: string;
  train_type: string;
  train_category?: string;
  source_station_code: string;
  destination_station_code: string;
  scheduled_arrival?: string | null;
  scheduled_departure?: string | null;
  expected_arrival?: string | null;
  expected_departure?: string | null;
  delay_arrival_minutes: number;
  delay_departure_minutes: number;
  platform?: string | null;
  platform_source: string;
  status: string;
  direction: string;
  data_provenance: string;
}

export interface ServiceAlert {
  id: number;
  title: string;
  alert_type: string;
  severity: 'info' | 'warning' | 'critical';
  description: string;
  affected_train_numbers?: string[];
  affected_station_codes?: string[];
  active_from?: string;
  active_to?: string | null;
  is_active: boolean;
  created_at: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  role: 'admin' | 'passenger';
  is_active: boolean;
  created_at: string;
}

export interface AuditLog {
  id: number;
  user_id?: number | null;
  username?: string | null;
  action: string;
  entity_type: string;
  entity_id?: string | null;
  details?: Record<string, any>;
  ip_address?: string | null;
  created_at: string;
}

export interface AdminStats {
  stations_count: number;
  trains_count: number;
  stops_count: number;
  alerts_count: number;
  users_count: number;
  audit_logs_count: number;
  memu_count?: number;
  demu_count?: number;
  emu_count?: number;
  local_count?: number;
  express_count?: number;
  superfast_count?: number;
  passenger_count?: number;
  mail_count?: number;
  weekly_count?: number;
  special_count?: number;
  rajdhani_count?: number;
  shatabdi_count?: number;
  vande_bharat_count?: number;
  duronto_count?: number;
  garib_rath_count?: number;
  tejas_count?: number;
  humsafar_count?: number;
  total_route_records?: number;
  total_route_stops?: number;
  trains_by_category?: Record<string, number>;
  stations_by_zone?: Record<string, number>;
  stations_by_division?: Record<string, number>;
  missing_route_trains_count?: number;
  duplicate_records_checked?: boolean;
  records_requiring_verification?: number;
}

export interface ImportValidationResult {
  is_valid: boolean;
  total_rows: number;
  valid_rows_count: number;
  error_rows_count: number;
  entity_type: string;
  errors: {
    row_index: number;
    field: string;
    message: string;
    raw_data?: Record<string, any>;
  }[];
  preview: Record<string, any>[];
}

export interface ImportResult {
  success: boolean;
  imported_count: number;
  updated_count: number;
  errors_count: number;
  message: string;
}
