# ENVIRONMENT CONFIGURATION FOR DEPLOYMENT

## 🎯 TRẢ LỜI: **CÓ CẦN THAY ĐỔI PORT KHI DEPLOY**

### ✅ **Frontend đã sẵn sàng** - KHÔNG cần thay đổi code!
Frontend của bạn đã được config rất tốt với **environment variables**:

```javascript
// File: config.js
export const API_BASE_URL = {
  auth: process.env.REACT_APP_AUTH_API_URL || "http://localhost:8001",
  menu: process.env.REACT_APP_MENU_API_URL || "http://localhost:8002",
  billing: process.env.REACT_APP_BILLING_API_URL || "http://localhost:8003",
  // ... các service khác
};
```

### ⚙️ **Backend** - KHÔNG cần thay đổi Dockerfile
Tất cả services đều expose port 8000 bên trong container (chuẩn):
```dockerfile
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", ...]
```

---

## 🚀 **CẤU HÌNH CHO DEPLOYMENT**

### **1. DigitalOcean App Platform**
Mỗi service sẽ có URL riêng, frontend cần environment variables:

```bash
# Environment variables cho Frontend trên App Platform:
REACT_APP_AUTH_API_URL=https://auth-service-xxxxx.ondigitalocean.app
REACT_APP_MENU_API_URL=https://menu-service-xxxxx.ondigitalocean.app
REACT_APP_BILLING_API_URL=https://billing-service-xxxxx.ondigitalocean.app
REACT_APP_CUSTOMER_API_URL=https://customer-service-xxxxx.ondigitalocean.app
REACT_APP_TABLES_API_URL=https://table-service-xxxxx.ondigitalocean.app
REACT_APP_STAFF_API_URL=https://staff-service-xxxxx.ondigitalocean.app
REACT_APP_RESERVATION_API_URL=https://reservation-service-xxxxx.ondigitalocean.app
REACT_APP_DASHBOARD_API_URL=https://dashboard-service-xxxxx.ondigitalocean.app
```

### **2. Droplet Deployment**
Với Nginx reverse proxy, tất cả sẽ qua 1 domain:

```bash
# Environment variables cho Frontend trên Droplet:
REACT_APP_AUTH_API_URL=https://yourdomain.com/api/auth
REACT_APP_MENU_API_URL=https://yourdomain.com/api/menu
REACT_APP_BILLING_API_URL=https://yourdomain.com/api/billing
REACT_APP_CUSTOMER_API_URL=https://yourdomain.com/api/customers
REACT_APP_TABLES_API_URL=https://yourdomain.com/api/tables
REACT_APP_STAFF_API_URL=https://yourdomain.com/api/staff
REACT_APP_RESERVATION_API_URL=https://yourdomain.com/api/reservations
REACT_APP_DASHBOARD_API_URL=https://yourdomain.com/api/dashboard
```

---

## 📁 **TẠO CÁC FILE CẤU HÌNH DEPLOYMENT**

Tôi sẽ tạo sẵn các file environment cho bạn...