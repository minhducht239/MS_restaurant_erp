import axios from "axios";
// 👇 THÊM DÒNG NÀY: Import cấu hình từ file config bạn vừa sửa
import { AUTH_API_URL } from "./config";
//const AUTH_API_URL = process.env.REACT_APP_AUTH_API_URL || "http://localhost:8001";

const authClient = axios.create({
  baseURL: AUTH_API_URL,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add token to requests
authClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle token refresh
authClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem("refresh_token");
        if (!refreshToken) throw new Error("No refresh token");

        const response = await axios.post(`${AUTH_API_URL}/api/auth/token/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        localStorage.setItem("access_token", access);

        originalRequest.headers.Authorization = `Bearer ${access}`;
        return authClient(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/authentication/sign-in";
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// ============= USER MANAGEMENT =============

export const getUsers = async (params = {}) => {
  try {
    const response = await authClient.get("/api/auth/users/", { params });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getUser = async (userId) => {
  try {
    const response = await authClient.get(`/api/auth/users/${userId}/`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const createUser = async (userData) => {
  try {
    const payload = { ...userData };
    // Backend requires password_confirm matching password
    if (payload.password) {
      payload.password_confirm = payload.password;
    }
    const response = await authClient.post("/api/auth/users/", payload);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const updateUser = async (userId, userData) => {
  try {
    const payload = { ...userData };
    // Remove password field if empty (backend doesn't support password update via PATCH)
    if (!payload.password || payload.password === "") {
      delete payload.password;
    }
    // Remove password_confirm as it's not needed for update
    delete payload.password_confirm;
    const response = await authClient.patch(`/api/auth/users/${userId}/`, payload);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const deleteUser = async (userId) => {
  try {
    const response = await authClient.delete(`/api/auth/users/${userId}/`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const activateUser = async (userId) => {
  try {
    const response = await authClient.post(`/api/auth/users/${userId}/activate/`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const deactivateUser = async (userId) => {
  try {
    const response = await authClient.post(`/api/auth/users/${userId}/deactivate/`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const resetUserPassword = async (userId, newPassword) => {
  try {
    const response = await authClient.post(`/api/auth/users/${userId}/reset_password/`, {
      new_password: newPassword,
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const unlockUser = async (userId) => {
  try {
    const response = await authClient.post(`/api/auth/users/${userId}/unlock/`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const changeUserRole = async (userId, role, customRoleId = null) => {
  try {
    const response = await authClient.post(`/api/auth/users/${userId}/change_role/`, {
      role,
      custom_role_id: customRoleId,
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

// ============= ROLES & PERMISSIONS =============

export const getRoles = async () => {
  try {
    const response = await authClient.get("/api/auth/roles/");
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getRole = async (roleId) => {
  try {
    const response = await authClient.get(`/api/auth/roles/${roleId}/`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const createRole = async (roleData) => {
  try {
    const response = await authClient.post("/api/auth/roles/", roleData);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const updateRole = async (roleId, roleData) => {
  try {
    const response = await authClient.patch(`/api/auth/roles/${roleId}/`, roleData);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const deleteRole = async (roleId) => {
  try {
    const response = await authClient.delete(`/api/auth/roles/${roleId}/`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getPermissions = async (params = {}) => {
  try {
    const response = await authClient.get("/api/auth/permissions/", { params });
    return response.data;
  } catch (error) {
    throw error;
  }
};

// ============= ACTIVITY LOGS =============

export const getActivityLogs = async (params = {}) => {
  try {
    const response = await authClient.get("/api/auth/activity-logs/", { params });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getLoginHistory = async (params = {}) => {
  try {
    const response = await authClient.get("/api/auth/login-history/", { params });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getMyActivityLogs = async () => {
  try {
    const response = await authClient.get("/api/auth/my-activity/");
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getMyLoginHistory = async () => {
  try {
    const response = await authClient.get("/api/auth/my-login-history/");
    return response.data;
  } catch (error) {
    throw error;
  }
};

export default {
  getUsers,
  getUser,
  createUser,
  updateUser,
  deleteUser,
  activateUser,
  deactivateUser,
  resetUserPassword,
  unlockUser,
  changeUserRole,
  getRoles,
  getRole,
  createRole,
  updateRole,
  deleteRole,
  getPermissions,
  getActivityLogs,
  getLoginHistory,
  getMyActivityLogs,
  getMyLoginHistory,
};
