# Hướng dẫn Deploy lên DigitalOcean App Platform

## Chi phí ước tính với Student Pack ($200)

| Service | Gói | Chi phí/tháng |
|---------|-----|---------------|
| auth-service | Basic XXS | $5 |
| billing-service | Basic XXS | $5 |
| customer-service | Basic XXS | $5 |
| menu-service | Basic XXS | $5 |
| reservation-service | Basic XXS | $5 |
| staff-service | Basic XXS | $5 |
| table-service | Basic XXS | $5 |
| dashboard-service | Basic XXS | $5 |
| frontend (static) | Free | $0 |
| MySQL Database | db-s-1vcpu-1gb | $15 |
| **Tổng cộng** | | **$55/tháng** |

Với $200 Student Pack, bạn có thể chạy khoảng **3.6 tháng**.

---

## Cách 1: Deploy bằng App Spec (Khuyến nghị)

### Bước 1: Push code lên GitHub
```bash
git add .
git commit -m "Add DigitalOcean App Spec"
git push origin master
```

### Bước 2: Tạo App trên DigitalOcean
1. Vào [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Click **Create App**
3. Chọn **From Spec** (bên phải)
4. Upload file `do-app-spec.yaml` hoặc paste nội dung vào
5. Review và chỉnh sửa các biến môi trường (SECRET_KEY, Google OAuth, etc.)
6. Click **Create Resources**

### Bước 3: Cấu hình biến môi trường
Sau khi tạo app, vào từng service và cập nhật các biến:
- `SECRET_KEY`: Tạo key ngẫu nhiên
- `GOOGLE_CLIENT_ID`: Client ID từ Google Console
- `GOOGLE_CLIENT_SECRET`: Client Secret từ Google Console

---

## Cách 2: Deploy từng service thủ công

### Bước 1: Tạo Database trước
1. Vào DigitalOcean → Databases → Create Database
2. Chọn MySQL 8
3. Gói: $15/month (db-s-1vcpu-1gb)
4. Region: Singapore (hoặc gần bạn nhất)
5. Lưu lại connection string

### Bước 2: Deploy từng service

#### Auth Service
1. Create App → GitHub → `minhducht239/MS_restaurant_erp`
2. Branch: `master`
3. Source Directory: `restaurant-microservices/services/auth-service`
4. Tự động detect Dockerfile
5. Chọn gói: Basic ($5/month)
6. HTTP Port: 8000
7. Thêm Environment Variables:
   ```
   DEBUG=False
   SECRET_KEY=your-secret-key
   DB_HOST=your-db-host
   DB_PORT=25060
   DB_NAME=defaultdb
   DB_USER=doadmin
   DB_PASSWORD=your-db-password
   ALLOWED_HOSTS=*
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   ```
8. Click Create

#### Lặp lại cho các service khác:
- **billing-service**: `restaurant-microservices/services/billing-service`
- **customer-service**: `restaurant-microservices/services/customer-service`
- **menu-service**: `restaurant-microservices/services/menu-service`
- **reservation-service**: `restaurant-microservices/services/reservation-service`
- **staff-service**: `restaurant-microservices/services/staff-service`
- **table-service**: `restaurant-microservices/services/table-service`
- **dashboard-service**: `restaurant-microservices/services/dashboard-service`

#### Frontend (React)
1. Create App → GitHub → `minhducht239/MS_restaurant_erp`
2. Source Directory: `MS_restaurant_erp_FE`
3. Chọn **Static Site** (Free)
4. Build Command: `npm run build`
5. Output Directory: `build`
6. Thêm Environment Variables:
   ```
   REACT_APP_API_URL=https://your-app-url.ondigitalocean.app
   ```

---

## Cách 3: Tối ưu chi phí - Dùng 1 Droplet

Nếu muốn tiết kiệm hơn, bạn có thể thuê 1 Droplet và chạy Docker Compose:

### Chi phí: ~$12-24/tháng
- Droplet 2GB RAM: $12/month
- Droplet 4GB RAM: $24/month (khuyến nghị)

### Các bước:
1. Tạo Droplet với Docker image
2. SSH vào server
3. Clone repo
4. Chạy `docker-compose up -d`
5. Cấu hình domain/SSL với Nginx

---

## Lưu ý quan trọng

### 1. Database Connection
DigitalOcean Managed Database yêu cầu SSL. Thêm vào settings.py:
```python
DATABASES = {
    'default': {
        ...
        'OPTIONS': {
            'ssl': {'ca': '/etc/ssl/certs/ca-certificates.crt'}
        }
    }
}
```

### 2. CORS cho Frontend
Cập nhật `CORS_ALLOWED_ORIGINS` trong mỗi service để cho phép domain frontend.

### 3. Service Communication
Các service cần gọi nhau qua URL public của App Platform, không phải localhost.
Cập nhật biến môi trường:
```
AUTH_SERVICE_URL=https://auth-service-xxxxx.ondigitalocean.app
BILLING_SERVICE_URL=https://billing-service-xxxxx.ondigitalocean.app
...
```

### 4. Health Check
Đảm bảo mỗi service có endpoint `/health/` trả về HTTP 200.

---

## Tóm tắt chi phí

| Phương án | Chi phí/tháng | Thời gian với $200 |
|-----------|---------------|-------------------|
| App Platform (8 services + DB) | $55 | 3.6 tháng |
| App Platform (4 services + DB) | $35 | 5.7 tháng |
| Droplet 4GB + MySQL | $24 | 8.3 tháng |
| Droplet 2GB + MySQL | $12 | 16.6 tháng |

**Khuyến nghị**: Nếu chỉ để demo/học tập, dùng Droplet sẽ tiết kiệm hơn nhiều.
