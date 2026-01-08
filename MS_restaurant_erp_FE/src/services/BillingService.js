import axios from "axios";
import { API_BASE_URL } from "./config";

// Thay thế
const API_URL = API_BASE_URL.billing;

// Hàm lấy header xác thực
const getAuthHeader = () => {
  const token = localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// Lấy danh sách hóa đơn
export const getBills = async (params = {}) => {
  try {
    let url = `${API_URL}/bills/`;

    // Log chi tiết các tham số ngày
    if (params.from_date || params.to_date) {
      console.log("Date params:", {
        from_date: params.from_date,
        to_date: params.to_date,
      });
    }

    const queryParams = new URLSearchParams();
    Object.keys(params).forEach((key) => {
      if (params[key] !== undefined && params[key] !== null && params[key] !== "") {
        queryParams.append(key, params[key]);
        console.log(`Added param: ${key}=${params[key]}`);
      }
    });

    const queryString = queryParams.toString();
    if (queryString) {
      url += `?${queryString}`;
    }

    console.log("Final request URL:", url);

    const response = await axios.get(url, {
      headers: getAuthHeader(),
    });

    return response.data;
  } catch (error) {
    console.error("Error fetching bills:", error);
    throw error;
  }
};

// Lấy chi tiết hóa đơn
export const getBillDetail = async (id) => {
  try {
    const response = await axios.get(`${API_URL}/bills/${id}/`, {
      headers: getAuthHeader(),
    });

    const data = response.data;
    console.log("Raw API response:", data);
    if (!data.items) data.items = [];
    return data;
  } catch (error) {
    console.error("Error fetching bill detail:", error);
    throw error;
  }
};

// Tạo hóa đơn mới
export const createBill = async (billData) => {
  console.log("Creating bill with data:", billData);

  try {
    // Kiểm tra nếu có table_id - tạo bill từ bàn
    if (billData.table_id) {
      console.log("Creating bill from table:", billData.table_id);

      // Tạo bill từ table với customer info và loyalty points
      const tableBillResponse = await axios.post(
        `${API_BASE_URL.tables}/${billData.table_id}/create_bill/`,
        {
          date: billData.date || new Date().toISOString().split("T")[0],
          customer: billData.customer?.trim() || "",
          phone: billData.phone?.trim() || "",
          // Loyalty points info
          customer_id: billData.customer_id || null,
          points_used: billData.points_used || 0,
          points_discount: billData.points_discount || 0,
        },
        {
          headers: {
            ...getAuthHeader(),
            "Content-Type": "application/json",
          },
        }
      );

      console.log("Table bill created:", tableBillResponse.data);

      // Return bill data directly (customer info already included)
      return {
        ...tableBillResponse.data,
        customer: tableBillResponse.data.bill?.customer || billData.customer,
        phone: tableBillResponse.data.bill?.phone || billData.phone,
      };
    } else {
      // Tạo hóa đơn thường
      console.log("Creating regular bill");

      const response = await axios.post(`${API_URL}/bills/`, billData, {
        headers: {
          ...getAuthHeader(),
          "Content-Type": "application/json",
        },
      });

      console.log("Regular bill created:", response.data);
      return response.data;
    }
  } catch (error) {
    console.error("Error in createBill:", error);

    if (error.response) {
      const errorMessage =
        error.response.data?.detail ||
        error.response.data?.message ||
        `HTTP ${error.response.status}: ${error.response.statusText}`;
      throw new Error(errorMessage);
    } else if (error.request) {
      throw new Error("Không thể kết nối đến server. Vui lòng kiểm tra kết nối mạng.");
    } else {
      throw new Error(`Lỗi request: ${error.message}`);
    }
  }
};

// Xóa hóa đơn
export const deleteBill = async (id) => {
  try {
    await axios.delete(`${API_URL}/bills/${id}/`, {
      headers: getAuthHeader(),
    });
  } catch (error) {
    console.error(`Error deleting bill ${id}:`, error);
    throw error;
  }
};

// Lấy dữ liệu doanh thu theo tháng
export const getMonthlyRevenue = async (year = new Date().getFullYear()) => {
  try {
    const response = await axios.get(`${API_URL}/bills/monthly_revenue/?year=${year}`, {
      headers: getAuthHeader(),
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching monthly revenue:", error);
    throw error;
  }
};
