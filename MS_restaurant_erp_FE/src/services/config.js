// Địa chỉ Gateway trên DigitalOcean
const GATEWAY_URL = "https://lionfish-app-jfnln.ondigitalocean.app";

export const API_BASE_URL = {
  // Service Auth: Trỏ về gốc (Vì trong UserService.js code đã tự thêm "/api/auth/...")
  auth: process.env.REACT_APP_AUTH_API_URL || GATEWAY_URL,
  menu: process.env.REACT_APP_MENU_API_URL || `${GATEWAY_URL}/api/menu`,
  billing: process.env.REACT_APP_BILLING_API_URL || `${GATEWAY_URL}/api/billing`,
  customer: process.env.REACT_APP_CUSTOMER_API_URL || `${GATEWAY_URL}/api/customer`,
  tables: process.env.REACT_APP_TABLES_API_URL || `${GATEWAY_URL}/api/table`,
  staff: process.env.REACT_APP_STAFF_API_URL || `${GATEWAY_URL}/api/staff`,
  reservation: process.env.REACT_APP_RESERVATION_API_URL || `${GATEWAY_URL}/api/reservation`,
  dashboard: process.env.REACT_APP_DASHBOARD_API_URL || `${GATEWAY_URL}/api/dashboard`,
};

// Export riêng cho các service cần dùng
export const AUTH_API_URL = API_BASE_URL.auth;
export const MENU_API_URL = API_BASE_URL.menu;
export const BILLING_API_URL = API_BASE_URL.billing;
export const CUSTOMER_API_URL = API_BASE_URL.customer;
export const TABLES_API_URL = API_BASE_URL.tables;
export const STAFF_API_URL = API_BASE_URL.staff;
export const RESERVATION_API_URL = API_BASE_URL.reservation;
export const DASHBOARD_API_URL = API_BASE_URL.dashboard;

export const logApiUrls = () => {
  console.log("=== API Configuration (Production) ===");
  Object.entries(API_BASE_URL).forEach(([service, url]) => {
    console.log(`${service.toUpperCase()}: ${url}`);
  });
  console.log("========================");
};
