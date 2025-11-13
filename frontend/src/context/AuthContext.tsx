import React, {
  createContext,
  useContext,
  useMemo,
  useEffect,
  useState,
} from "react";
import type { UserType } from "../types/User.types";
import { login as apiLogin, logout as apiLogout } from "../api/auth";
import api from "../api/axios";
import {
  getAccessToken,
  getRefreshToken,
  setAccessToken,
  setRefreshToken,
  clearTokens,
} from "../utils/tokenStorage";
import { useQuery, useQueryClient } from "@tanstack/react-query";

type AuthContextType = {
  user: UserType | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  isLoading: boolean;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const queryClient = useQueryClient();
  const [isLoggingIn, setIsLoggingIn] = useState(false);

  const {
    data: user,
    isLoading: isUserLoading,
    error,
    refetch,
  } = useQuery<UserType | null, Error>({
    queryKey: ["userProfile"],
    queryFn: async () => {
      const response = await api.get<{ user: UserType }>("user/me/");
      return response.data.user;
    },
    enabled: Boolean(getAccessToken() && getRefreshToken()),
    staleTime: 60 * 1000,
    retry: false,
  });

  useEffect(() => {
    if (error) {
      clearTokens();
      queryClient.removeQueries({ queryKey: ["userProfile"] });
    }
  }, [error, queryClient]);

  const login = async (email: string, password: string) => {
    setIsLoggingIn(true);
    try {
      const response = await apiLogin({ email, password });
      const tokens = response.data;
      setAccessToken(tokens.access);
      setRefreshToken(tokens.refresh);
      api.defaults.headers.common["Authorization"] = `Bearer ${tokens.access}`;

      await refetch();
    } finally {
      setIsLoggingIn(false);
    }
  };

  const logout = async () => {
    try {
      const refresh = getRefreshToken();
      if (refresh) {
        await apiLogout(refresh);
      }
    } catch (error) {
      console.warn("Logout API call failed", error);
    } finally {
      clearTokens();
      delete api.defaults.headers.common["Authorization"];
      queryClient.removeQueries({ queryKey: ["userProfile"] });
      window.location.href = "/login";
    }
  };

  const isLoading = isUserLoading || isLoggingIn;

  const contextValue = useMemo<AuthContextType>(
    () => ({
      user: user ?? null,
      login,
      logout,
      isLoading,
    }),
    [user, login, logout, isLoading]
  );

  return (
    <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>
  );
};
