# 🚀 DEPLOY VỚI DIGITALOCEAN MANAGED DATABASE SẴN CÓ

## ✅ **CHUẨN BỊ HOÀN TẤT:**
- ✅ Database: `restaurant-erp-do-user-28536171-0.e.db.ondigitalocean.com:25060`
- ✅ App Spec: `do-app-spec-production.yaml` 
- ✅ All services optimized và ready to deploy

---

## 🎯 **DEPLOY APP PLATFORM (KHUYẾN NGHỊ)**

### **Bước 1: Deploy bằng App Spec**
1. Vào [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. **Create App** → **From Spec**
3. Upload file: `do-app-spec-production.yaml`
4. **QUAN TRỌNG**: Replace placeholder password:
   ```yaml
   # Tìm dòng này và thay thế:
   value: "YOUR_ACTUAL_DB_PASSWORD_HERE"
   # Thành password thực từ DigitalOcean Database dashboard
   value: "your-actual-database-password"
   ```
5. Click **Create Resources**

### **Bước 2: Đợi Deploy hoàn thành** (~10-15 phút)
- 8 Backend services sẽ được tạo
- 1 Frontend static site
- Tất cả sẽ connect tới database có sẵn

### **Bước 3: Get Service URLs**
Sau khi deploy xong, copy URLs của từng service:
```
Auth: https://auth-service-xxxxx.ondigitalocean.app
Menu: https://menu-service-xxxxx.ondigitalocean.app  
Billing: https://billing-service-xxxxx.ondigitalocean.app
Customer: https://customer-service-xxxxx.ondigitalocean.app
Tables: https://table-service-xxxxx.ondigitalocean.app
Staff: https://staff-service-xxxxx.ondigitalocean.app
Reservations: https://reservation-service-xxxxx.ondigitalocean.app
Dashboard: https://dashboard-service-xxxxx.ondigitalocean.app
Frontend: https://restaurant-frontend-xxxxx.ondigitalocean.app
```

### **Bước 4: Update Frontend Environment**
1. Vào **restaurant-frontend** app settings
2. **Environment Variables** → Edit:
   ```
   REACT_APP_AUTH_API_URL=https://auth-service-xxxxx.ondigitalocean.app
   REACT_APP_MENU_API_URL=https://menu-service-xxxxx.ondigitalocean.app
   REACT_APP_BILLING_API_URL=https://billing-service-xxxxx.ondigitalocean.app
   REACT_APP_CUSTOMER_API_URL=https://customer-service-xxxxx.ondigitalocean.app
   REACT_APP_TABLES_API_URL=https://table-service-xxxxx.ondigitalocean.app
   REACT_APP_STAFF_API_URL=https://staff-service-xxxxx.ondigitalocean.app
   REACT_APP_RESERVATION_API_URL=https://reservation-service-xxxxx.ondigitalocean.app
   REACT_APP_DASHBOARD_API_URL=https://dashboard-service-xxxxx.ondigitalocean.app
   ```
3. **Deploy** để rebuild frontend

---

## 🔧 **DATABASE MIGRATION**

### **Setup Initial Database:**
1. Vào bất kỳ backend service nào (ví dụ: auth-service)
2. **Console** → Run commands:
   ```bash
   # Create all tables
   python manage.py migrate
   
   # Create superuser
   python manage.py createsuperuser
   
   # Load initial data (optional)
   python manage.py loaddata initial_data.json
   ```

---

## 🧪 **TESTING & VERIFICATION**

### **Test Backend APIs:**
```bash
# Test auth service
curl https://auth-service-xxxxx.ondigitalocean.app/health/

# Test menu service  
curl https://menu-service-xxxxx.ondigitalocean.app/health/

# Test complete flow
curl -X POST https://auth-service-xxxxx.ondigitalocean.app/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123","first_name":"Test","last_name":"User"}'
```

### **Test Frontend:**
1. Vào frontend URL
2. ✅ Test đăng ký/đăng nhập
3. ✅ Test các chức năng chính
4. ✅ Test Google OAuth (cần update redirect URI)

---

## ⚙️ **GOOGLE OAUTH CONFIGURATION**

### **Update Google Console:**
1. Vào [Google Cloud Console](https://console.cloud.google.com/)
2. **APIs & Services** → **Credentials**
3. Edit OAuth 2.0 Client
4. **Authorized redirect URIs** → Add:
   ```
   https://restaurant-frontend-xxxxx.ondigitalocean.app/auth/google/callback
   ```
5. Save

### **Update Backend Environment:**
Vào từng backend service → **Settings** → **Environment Variables**:
```
GOOGLE_OAUTH2_REDIRECT_URI=https://restaurant-frontend-xxxxx.ondigitalocean.app/auth/google/callback
FRONTEND_URL=https://restaurant-frontend-xxxxx.ondigitalocean.app
CORS_ALLOWED_ORIGINS=https://restaurant-frontend-xxxxx.ondigitalocean.app
```

---

## 💰 **CHI PHÍ CUỐI CÙNG**

```
✅ Database (có sẵn): $15/month
✅ 8 Backend Services: $40/month  
✅ 1 Frontend Site: FREE
—————————————————————————————————
💰 Total: $55/month

🎉 Với $200 Student Pack: chạy được 3.6 tháng!
```

---

## 🔍 **MONITORING & MAINTENANCE**

### **Built-in Monitoring:**
- DigitalOcean App Platform có dashboard monitor sẵn
- Real-time metrics cho CPU, Memory, Request count
- Automatic health checks và restart

### **View Logs:**
```bash
# Trong DigitalOcean dashboard:
App → Service → Runtime Logs
App → Service → Build Logs
```

### **Update Deployment:**
```bash
# Auto-deploy khi push to GitHub
git add .
git commit -m "Update feature"
git push origin master
# DigitalOcean sẽ tự động rebuild và deploy
```

---

## 🎯 **TROUBLESHOOTING**

### **Nếu service không start:**
1. Check **Build Logs** → Tìm errors
2. Check **Environment Variables** → Đảm bảo database config đúng
3. Check **Runtime Logs** → Django errors

### **Database connection issues:**
```python
# Test DB connection trong console:
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT 1")
print("DB connected successfully!")
```

### **Frontend không call được API:**
1. Check CORS settings trong backend
2. Verify API URLs trong frontend environment
3. Check network connectivity

---

## ✅ **READY TO GO!**

**Bạn giờ có thể:**
1. 🚀 Deploy tất cả với 1 click (App Spec)
2. 🔧 Connect tới database có sẵn  
3. 🌐 Access ứng dụng qua internet
4. 📊 Monitor performance real-time
5. 🔄 Auto-deploy từ GitHub

**Total setup time: ~20 phút!** 🎉