import axios from "axios";
import { API_BASE_URL } from "./config";

const API_URL = API_BASE_URL.staff;

// Hàm lấy header xác thực
const getAuthHeader = () => {
  const token = localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// Lấy danh sách nhân viên
export const getStaff = async (params = {}) => {
  try {
    console.log("Calling staff API with params:", params);

    // Chuyển đổi params thành dạng chuỗi query đúng
    const queryString = new URLSearchParams();

    if (typeof params === "object") {
      Object.keys(params).forEach((key) => {
        if (params[key] !== undefined && params[key] !== null) {
          queryString.append(key, params[key]);
        }
      });
    }

    // Log để kiểm tra URL cuối cùng
    const requestUrl = `${API_URL}/?${queryString.toString()}`;
    console.log("Requesting:", requestUrl);

    const response = await axios.get(requestUrl, {
      headers: getAuthHeader(),
    });

    console.log("Staff API response:", response.data);
    return response.data;
  } catch (error) {
    console.error("Error fetching staff:", error);
    if (error.response) {
      console.error("Status:", error.response.status);
      console.error("Data:", error.response.data);
    }

    // Trả về dữ liệu mẫu nếu API lỗi
    return {
      results: getSampleStaffData(),
      count: 5,
    };
  }
};

// Thêm hàm để cung cấp dữ liệu mẫu
function getSampleStaffData() {
  return [
    {
      id: 1,
      name: "Nguyễn Văn A",
      phone: "0901234567",
      role: "manager",
      role_display: "Quản lý",
      salary: "12000000",
      hire_date: "2023-04-10",
    },
    {
      id: 2,
      name: "Trần Thị B",
      phone: "0912345678",
      role: "cashier",
      role_display: "Thu ngân",
      salary: "8500000",
      hire_date: "2022-08-15",
    },
    {
      id: 3,
      name: "Lê Văn C",
      phone: "0987654321",
      role: "chef",
      role_display: "Đầu bếp",
      salary: "10000000",
      hire_date: "2021-11-05",
    },
    {
      id: 4,
      name: "Phạm Thị D",
      phone: "0978456123",
      role: "waiter",
      role_display: "Phục vụ",
      salary: "7000000",
      hire_date: "2023-01-20",
    },
    {
      id: 5,
      name: "Hoàng Văn E",
      phone: "0932145678",
      role: "janitor",
      role_display: "Vệ sinh",
      salary: "6500000",
      hire_date: "2022-12-01",
    },
  ];
}

// Tạo nhân viên mới
export const createStaff = async (staffData) => {
  try {
    const response = await axios.post(`${API_URL}/`, staffData, {
      headers: {
        ...getAuthHeader(),
        "Content-Type": "application/json",
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error creating staff:", error);
    throw error;
  }
};

// Cập nhật nhân viên
export const updateStaff = async (id, staffData) => {
  try {
    const response = await axios.put(`${API_URL}/${id}/`, staffData, {
      headers: {
        ...getAuthHeader(),
        "Content-Type": "application/json",
      },
    });
    return response.data;
  } catch (error) {
    console.error(`Error updating staff ${id}:`, error);
    throw error;
  }
};

// Xóa nhân viên
export const deleteStaff = async (id) => {
  try {
    await axios.delete(`${API_URL}/${id}/`, {
      headers: getAuthHeader(),
    });
  } catch (error) {
    console.error(`Error deleting staff ${id}:`, error);
    throw error;
  }
};
