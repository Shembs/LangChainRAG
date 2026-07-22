import { create } from 'zustand';
import type { User } from '../types/auth';
import { authApi } from '../api/auth';
import { setAccessToken, setRefreshToken, clearTokens, getAccessToken } from '../api/client';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
  logout: () => void;
  fetchUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: !!getAccessToken(),
  isLoading: false,

  login: async (username: string, password: string) => {
    const tokens = await authApi.login({ username, password });
    setAccessToken(tokens.access_token);
    setRefreshToken(tokens.refresh_token);
    const user = await authApi.getMe();
    set({ user, isAuthenticated: true });
  },

  register: async (username: string, password: string) => {
    await authApi.register({ username, password });
  },

  logout: () => {
    clearTokens();
    set({ user: null, isAuthenticated: false });
  },

  fetchUser: async () => {
    if (!getAccessToken()) return;
    set({ isLoading: true });
    try {
      const user = await authApi.getMe();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch {
      clearTokens();
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },
}));
