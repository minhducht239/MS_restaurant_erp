import axios from "axios";
import { API_BASE_URL } from "./config";

const API_URL = API_BASE_URL.menu;

axios.defaults.timeout = 10000;

const getAuthHeader = () => {
  const token = localStorage.getItem("access_token");
  return { Authorization: `Bearer ${token}` };
};

const handleApiError = (error, operation = "API operation") => {
  console.error(`Error in ${operation}:`, error);

  if (error.response) {
    const { status, data } = error.response;
    console.error(`HTTP ${status}:`, data);

    switch (status) {
      case 400:
        throw new Error(`Dữ liệu không hợp lệ: ${JSON.stringify(data)}`);
      case 401:
        throw new Error("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.");
      case 403:
        throw new Error("Bạn không có quyền thực hiện hành động này.");
      case 404:
        throw new Error("Không tìm thấy dữ liệu yêu cầu.");
      case 500:
        throw new Error("Lỗi server. Vui lòng thử lại sau.");
      default:
        throw new Error(`Lỗi server (${status}): ${data?.detail || "Không xác định"}`);
    }
  } else if (error.request) {
    throw new Error("Không thể kết nối đến server. Vui lòng kiểm tra kết nối mạng.");
  } else {
    throw new Error(error.message || "Đã xảy ra lỗi không xác định.");
  }
};

// Fetch menu items with optional filters
export const getMenuItems = async (params = {}) => {
  try {
    console.log("Fetching menu items with params:", params);
    const response = await axios.get(`${API_URL}/api/menu/items/`, {
      params,
      headers: getAuthHeader(),
    });
    console.log("Menu items fetched successfully:", response.data);
    return response.data;
  } catch (error) {
    handleApiError(error, "getMenuItems");
  }
};

// Get single menu item
export const getMenuItem = async (id) => {
  try {
    console.log(`Fetching menu item with ID: ${id}`);
    const response = await axios.get(`${API_URL}/api/menu/items/${id}/`, {
      headers: getAuthHeader(),
    });
    console.log("Menu item fetched successfully:", response.data);
    return response.data;
  } catch (error) {
    handleApiError(error, `getMenuItem(${id})`);
  }
};

export const createMenuItem = async (itemData) => {
  try {
    console.log("CREATE MENU ITEM START");
    console.log("Input data type:", typeof itemData);
    console.log("Is FormData:", itemData instanceof FormData);

    let headers = { ...getAuthHeader() };

    if (itemData instanceof FormData) {
      console.log("Using FormData for file upload");

      console.log("FormData contents:");
      for (let [key, value] of itemData.entries()) {
        if (value instanceof File) {
          console.log(`${key}: File(${value.name}, ${value.size} bytes, ${value.type})`);
        } else {
          console.log(`${key}: ${value}`);
        }
      }
    } else {
      console.log("Using JSON data");
      headers["Content-Type"] = "application/json";
      console.log("JSON data:", itemData);
    }

    const response = await axios.post(`${API_URL}/api/menu/items/`, itemData, {
      headers,
    });

    console.log("Create response:", response.data);
    console.log("CREATE MENU ITEM SUCCESS");
    return response.data;
  } catch (error) {
    console.error("CREATE MENU ITEM ERROR");
    handleApiError(error, "createMenuItem");
  }
};

export const updateMenuItem = async (id, itemData) => {
  try {
    console.log(`UPDATE MENU ITEM ${id} START`);
    console.log("Input data type:", typeof itemData);
    console.log("Is FormData:", itemData instanceof FormData);

    let headers = { ...getAuthHeader() };

    if (itemData instanceof FormData) {
      console.log("Using FormData for file upload");

      console.log("FormData contents:");
      for (let [key, value] of itemData.entries()) {
        if (value instanceof File) {
          console.log(`${key}: File(${value.name}, ${value.size} bytes, ${value.type})`);
        } else {
          console.log(`${key}: ${value}`);
        }
      }
    } else {
      console.log("Using JSON data");
      headers["Content-Type"] = "application/json";
      console.log("JSON data:", itemData);
    }

    const response = await axios.put(`${API_URL}/api/menu/items/${id}/`, itemData, {
      headers,
    });

    console.log("Update response:", response.data);
    console.log(`UPDATE MENU ITEM ${id} SUCCESS`);
    return response.data;
  } catch (error) {
    console.error(`UPDATE MENU ITEM ${id} ERROR`);
    handleApiError(error, `updateMenuItem(${id})`);
  }
};

export const deleteMenuItem = async (id) => {
  try {
    console.log(`Deleting menu item with ID: ${id}`);
    await axios.delete(`${API_URL}/api/menu/items/${id}/`, {
      headers: getAuthHeader(),
    });
    console.log(`Menu item ${id} deleted successfully`);
    return true;
  } catch (error) {
    handleApiError(error, `deleteMenuItem(${id})`);
  }
};

export const uploadMenuImage = async (id, imageFile) => {
  try {
    console.log(`Uploading image for menu item ${id}:`, imageFile.name);

    const formData = new FormData();
    formData.append("image", imageFile);

    const response = await axios.patch(`${API_URL}/api/menu/items/${id}/`, formData, {
      headers: {
        ...getAuthHeader(),
        "Content-Type": "multipart/form-data",
      },
    });

    console.log("Image uploaded successfully:", response.data);
    return response.data;
  } catch (error) {
    handleApiError(error, `uploadMenuImage(${id})`);
  }
};

export const toggleMenuItemAvailability = async (id, isAvailable) => {
  try {
    console.log(`Toggling availability for item ${id} to: ${isAvailable}`);

    const response = await axios.patch(
      `${API_URL}/api/menu/items/${id}/`,
      { is_available: Boolean(isAvailable) },
      {
        headers: {
          ...getAuthHeader(),
          "Content-Type": "application/json",
        },
        params: { is_available: Boolean(isAvailable) },
      }
    );

    console.log("Availability toggled successfully:", response.data);
    return response.data;
  } catch (error) {
    handleApiError(error, `toggleMenuItemAvailability(${id})`);
  }
};

export const checkApiHealth = async () => {
  try {
    const response = await axios.get(`${API_URL}/health/`, {
      timeout: 5000,
    });
    return response.status === 200;
  } catch (error) {
    console.warn("API health check failed:", error.message);
    return false;
  }
};
