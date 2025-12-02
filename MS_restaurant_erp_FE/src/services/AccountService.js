import axios from "axios";

// Tách riêng 2 API URLs
const AUTH_API_URL = process.env.REACT_APP_AUTH_API_URL || "http://localhost:8001";
const USER_API_URL = process.env.REACT_APP_USER_API_URL || "http://localhost:8002";

// Auth API Client (cho authentication)
const authClient = axios.create({
  baseURL: AUTH_API_URL,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

// User API Client (cho user profile)
const userClient = axios.create({
  baseURL: USER_API_URL,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add token to user requests
userClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle token refresh for user client
userClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem("refresh_token");
        if (!refreshToken) throw new Error("No refresh token");

        // Gọi AUTH SERVICE để refresh token
        const response = await authClient.post("/auth/token/refresh", {
          refresh: refreshToken,
        });

        const { access } = response.data;
        localStorage.setItem("access_token", access);

        // Retry original request
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return userClient(originalRequest);
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

// ============= USER SERVICE APIs =============

export const getCurrentUser = async () => {
  try {
    console.log("=== GET CURRENT USER ===");
    const response = await userClient.get("/users/me");
    console.log("Current user response:", response.data);
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
      dataToSend.phone = profileData.phone.trim();
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

    // Gọi USER SERVICE
    const response = await userClient.patch("/users/me", dataToSend);

    console.log("Update response:", response.data);
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
      formData.append("file", file); // Backend mới dùng "file" thay vì "avatar"
    }

    // Gọi USER SERVICE
    const response = await userClient.post("/users/upload-avatar", formData, {
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
    // Gọi USER SERVICE
    const response = await userClient.delete("/users/avatar");
    console.log("Delete avatar response:", response.data);
    return response.data;
  } catch (error) {
    handleApiError(error, "deleteAvatar");
  }
};

export const getAvatarUrl = (avatarPath) => {
  if (!avatarPath) return null;

  // If already full URL, return as is
  if (avatarPath.startsWith("http")) {
    return avatarPath;
  }

  // If relative path, prepend USER API base URL
  const baseUrl = USER_API_URL.replace("/api", "");
  return `${baseUrl}${avatarPath}`;
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

    // Get current user để lấy username
    const currentUser = await getCurrentUser();

    const dataToSend = {
      current_password: passwordData.currentPassword,
      new_password: passwordData.newPassword,
      username: currentUser.username,
    };

    console.log("Sending password change request...");

    // Gọi AUTH SERVICE
    const response = await authClient.put("/auth/change-password", dataToSend);

    console.log("Password change response:", response.data);
    return response.data;
  } catch (error) {
    handleApiError(error, "changeUserPassword");
  }
};

export default { authClient, userClient };