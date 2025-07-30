import api from "./axios";

type LoginData = { email: string; password: string };
type RegisterData = {
  email: string;
  first_name: string;
  last_name: string;
  password: string;
};

export const login = (data: LoginData) => api.post("auth/token/", data);

export const refreshToken = (refresh: string) =>
  api.post("auth/token/refresh/", { refresh });

export const signup = (data: RegisterData) => api.post("auth/register/", data);

export const logout = (refresh: string) =>
  api.post("auth/token/logout/", { refresh });
