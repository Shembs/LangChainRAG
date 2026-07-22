import client from './client';
import type { LoginRequest, RegisterRequest, TokenResponse, User, ChangePasswordRequest } from '../types/auth';

export const authApi = {
  login: (data: LoginRequest) =>
    client.post<TokenResponse>('/auth/login', data).then((r) => r.data),

  register: (data: RegisterRequest) =>
    client.post<User>('/auth/register', data).then((r) => r.data),

  getMe: () =>
    client.get<User>('/auth/me').then((r) => r.data),

  changePassword: (data: ChangePasswordRequest) =>
    client.post<{ message: string }>('/auth/change-password', data).then((r) => r.data),
};
