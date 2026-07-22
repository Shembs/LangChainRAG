export interface User {
  id: string;
  username: string;
  role: 'admin' | 'user';
  is_active: boolean;
  last_login_at: string | null;
  created_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface ChangePasswordRequest {
  old_password: string;
  new_password: string;
}
