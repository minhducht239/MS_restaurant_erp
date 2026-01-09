import axios from "axios";
import { AUTH_API_URL } from "./config";

// Auth API Client
const authClient = axios.create({
  baseURL: AUTH_API_URL,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add token to auth requests
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

        // Refresh token
        const response = await axios.post(`${AUTH_API_URL}/api/auth/token/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        localStorage.setItem("access_token", access);

        // Retry original request
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return authClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/authentication/sign-in";
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

const handleApiError = (error, context = "") => {
  console.error(`API Error in ${context}:`, error);

  if (error.response) {
    const status = error.response.status;
    const data = error.response.data;

    console.error("Response data:", data);
    console.error("Response status:", status);

    if (data?.errors) {
      const errorMessages = Object.values(data.errors).flat();
      throw new Error(errorMessages.join(", "));
    } else if (data?.detail) {
      throw new Error(data.detail);
    } else if (data?.message) {
      throw new Error(data.message);
    } else {
      throw new Error(`Server error: ${status}`);
    }
  } else if (error.request) {
    console.error("Request made but no response received");
    throw new Error("Không thể kết nối đến server. Vui lòng kiểm tra kết nối mạng.");
  } else {
    console.error("Error setting up request:", error.message);
    throw new Error(error.message || "Có lỗi không xác định xảy ra");
  }
};

// ============= USER PROFILE APIs (via Auth Service) =============

export const getCurrentUser = async () => {
  try {
    console.log("=== GET CURRENT USER ===");
    const response = await authClient.get("/api/auth/profile/");
    console.log("Current user response:", response.data);

    // Backend trả về {success: true, user: {...}}
    if (response.data.success && response.data.user) {
      return response.data.user;
    }

    return response.data;
  } catch (error) {
    handleApiError(error, "getCurrentUser");
  }
};

export const updateUserProfile = async (profileData) => {
  try {
    console.log("=== UPDATE USER PROFILE ===");
    console.log("Profile data:", profileData);

    if (!profileData || typeof profileData !== "object") {
      throw new Error("Invalid profile data");
    }

    const dataToSend = {};

    // Xử lý name
    if (profileData.name && profileData.name.trim()) {
      const nameParts = profileData.name.trim().split(/\s+/);
      dataToSend.first_name = nameParts[0] || "";
      dataToSend.last_name = nameParts.slice(1).join(" ") || "";
    }

    // Xử lý email
    if (profileData.email && profileData.email.trim()) {
      dataToSend.email = profileData.email.trim();
    }

    // Xử lý phone
    if (profileData.phone && profileData.phone.trim()) {
      dataToSend.phone_number = profileData.phone.trim();
    }

    if (profileData.address !== undefined) {
      dataToSend.address = profileData.address;
    }

    if (profileData.date_of_birth !== undefined) {
      dataToSend.date_of_birth = profileData.date_of_birth;
    }

    console.log("Sending data:", dataToSend);

    if (Object.keys(dataToSend).length === 0) {
      throw new Error("No data to update");
    }

    // Gọi AUTH SERVICE
    const response = await authClient.patch("/api/auth/profile/", dataToSend);

    console.log("Update response:", response.data);

    // Backend trả về {success: true, user: {...}}
    if (response.data.success && response.data.user) {
      return response.data.user;
    }

    return response.data;
  } catch (error) {
    handleApiError(error, "updateUserProfile");
  }
};

export const uploadAvatar = async (file) => {
  try {
    console.log("=== UPLOAD AVATAR ===");

    if (!file) {
      throw new Error("No file provided");
    }

    let formData;
    if (file instanceof FormData) {
      formData = file;
    } else {
      formData = new FormData();
      formData.append("avatar", file);
    }

    // Gọi AUTH SERVICE
    const response = await authClient.post("/api/auth/profile/avatar/", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    console.log("Avatar upload response:", response.data);
    return response.data;
  } catch (error) {
    handleApiError(error, "uploadAvatar");
  }
};

export const deleteAvatar = async () => {
  try {
    console.log("=== DELETE AVATAR ===");
    // Gọi AUTH SERVICE
    const response = await authClient.delete("/api/auth/profile/avatar/");
    console.log("Delete avatar response:", response.data);
    return response.data;
  } catch (error) {
    handleApiError(error, "deleteAvatar");
  }
};

export const getAvatarUrl = (avatarPath) => {
  if (!avatarPath) return null;

  // If already full URL, normalize to https for the gateway domain to avoid mixed-content
  if (typeof avatarPath === "string" && avatarPath.startsWith("http")) {
    if (avatarPath.startsWith("http://lionfish-app-jfnln.ondigitalocean.app")) {
      return avatarPath.replace("http://", "https://");
    }
    return avatarPath;
  }

  // If relative path, prepend AUTH API base URL
  if (typeof avatarPath === "string") {
    return `${AUTH_API_URL}${avatarPath}`;
  }

  return null;
};

// ============= AUTH SERVICE APIs =============

export const changeUserPassword = async (passwordData) => {
  try {
    console.log("=== CHANGE USER PASSWORD ===");

    if (!passwordData || typeof passwordData !== "object") {
      throw new Error("Invalid password data");
    }

    // Validate input
    if (!passwordData.currentPassword) {
      throw new Error("Current password is required");
    }

    if (!passwordData.newPassword) {
      throw new Error("New password is required");
    }

    if (passwordData.newPassword.length < 6) {
      throw new Error("New password must be at least 6 characters");
    }

    const dataToSend = {
      old_password: passwordData.currentPassword,
      new_password: passwordData.newPassword,
    };

    console.log("Sending password change request...");

    // Gọi AUTH SERVICE
    const response = await authClient.post("/api/auth/profile/change-password/", dataToSend);

    console.log("Password change response:", response.data);

    // Backend có thể trả về {success: true, ...}
    if (response.data.success !== undefined) {
      return response.data;
    }

    return response.data;
  } catch (error) {
    handleApiError(error, "changeUserPassword");
  }
};

export default { authClient };
