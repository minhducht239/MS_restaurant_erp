# Restaurant ERP Microservices

Hệ thống quản lý nhà hàng sử dụng kiến trúc Microservices với Docker.

## 🏗️ Kiến trúc

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway (Nginx)                       │
│                         Port: 8000                               │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │           │           │           │           │
        ▼           ▼           ▼           ▼           ▼
┌─────────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│Auth Service │ │  Menu   │ │ Billing │ │Customer │ │  Table  │
│   :8001     │ │ :8002   │ │ :8003   │ │ :8004   │ │ :8005   │
└─────────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘
        │           │           │           │           │
        ▼           ▼           ▼           ▼           ▼
┌─────────────────────────────────────────────────────────────────┐
│                         MySQL Database                           │
│                         Port: 3307                               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Redis Cache                              │
│                         Port: 6379                               │
└─────────────────────────────────────────────────────────────────┘
```

## 📦 Services

| Service | Port | Mô tả |
|---------|------|-------|
| **gateway** | 8000 | API Gateway (Nginx) - Route requests |
| **auth-service** | 8001 | Đăng nhập, đăng ký, JWT tokens |
| **menu-service** | 8002 | Quản lý món ăn |
| **billing-service** | 8003 | Quản lý hóa đơn |
| **customer-service** | 8004 | Quản lý khách hàng, loyalty |
| **table-service** | 8005 | Quản lý bàn, đơn hàng bàn |
| **staff-service** | 8006 | Quản lý nhân viên |
| **reservation-service** | 8007 | Quản lý đặt bàn |
| **dashboard-service** | 8008 | Thống kê, báo cáo |

## 🚀 Khởi chạy

### Prerequisites
- Docker & Docker Compose
- Git

### Quick Start

```bash
# 1. Clone và di chuyển vào thư mục
cd restaurant-microservices

# 2. Tạo file .env từ template
cp .env.example .env

# 3. Build và chạy tất cả services
docker-compose up --build -d

# 4. Xem logs
docker-compose logs -f

# 5. Chạy migrations (lần đầu)
docker-compose exec auth-service python manage.py migrate
docker-compose exec menu-service python manage.py migrate
docker-compose exec billing-service python manage.py migrate
docker-compose exec customer-service python manage.py migrate
docker-compose exec table-service python manage.py migrate
docker-compose exec staff-service python manage.py migrate
docker-compose exec reservation-service python manage.py migrate
```

### Dừng services

```bash
docker-compose down

# Xóa cả volumes (data)
docker-compose down -v
```

## 📡 API Endpoints

Base URL: `http://localhost:8000`

### Authentication
```
POST /api/auth/login/           # Đăng nhập
POST /api/auth/register/        # Đăng ký
POST /api/auth/token/refresh/   # Refresh token
GET  /api/auth/profile/         # Lấy profile
```

### Menu
```
GET    /api/menu/items/          # Danh sách món
POST   /api/menu/items/          # Thêm món
GET    /api/menu/items/{id}/     # Chi tiết món
PUT    /api/menu/items/{id}/     # Cập nhật món
DELETE /api/menu/items/{id}/     # Xóa món
GET    /api/menu/categories/     # Danh mục
```

### Billing
```
GET    /api/billing/             # Danh sách hóa đơn
POST   /api/billing/             # Tạo hóa đơn
GET    /api/billing/{id}/        # Chi tiết hóa đơn
GET    /api/billing/statistics/  # Thống kê
```

### Customers
```
GET    /api/customers/           # Danh sách khách hàng
POST   /api/customers/           # Thêm khách hàng
GET    /api/customers/{id}/      # Chi tiết
GET    /api/customers/top_customers/ # Top khách hàng
```

### Tables
```
GET    /api/tables/              # Danh sách bàn
POST   /api/tables/{id}/create_order/  # Tạo order cho bàn
POST   /api/tables/{id}/add_item/      # Thêm món vào bàn
POST   /api/tables/{id}/complete_order/ # Hoàn thành order
```

### Staff
```
GET    /api/staff/               # Danh sách nhân viên
POST   /api/staff/               # Thêm nhân viên
GET    /api/staff/statistics/    # Thống kê nhân viên
```

### Reservations
```
GET    /api/reservations/        # Danh sách đặt bàn
POST   /api/reservations/        # Tạo đặt bàn
POST   /api/reservations/{id}/confirm/  # Xác nhận
POST   /api/reservations/{id}/cancel/   # Hủy
GET    /api/reservations/today/  # Đặt bàn hôm nay
```

### Dashboard
```
GET    /api/dashboard/statistics/     # Thống kê tổng hợp
GET    /api/dashboard/weekly-revenue/ # Doanh thu tuần
GET    /api/dashboard/monthly-revenue/ # Doanh thu tháng
GET    /api/dashboard/top-items/      # Món bán chạy
```

## 🔧 Development

### Rebuild một service cụ thể
```bash
docker-compose up --build -d auth-service
```

### Xem logs của một service
```bash
docker-compose logs -f menu-service
```

### Chạy Django shell
```bash
docker-compose exec auth-service python manage.py shell
```

### Tạo superuser
```bash
docker-compose exec auth-service python manage.py createsuperuser
```

## 📁 Cấu trúc thư mục

```
restaurant-microservices/
├── docker-compose.yml          # Orchestration config
├── .env.example                # Environment template
├── README.md
├── gateway/                    # Nginx API Gateway
│   ├── Dockerfile
│   ├── nginx.conf
│   └── conf.d/
│       └── default.conf
├── shared/                     # Shared utilities
│   ├── __init__.py
│   ├── jwt_auth.py            # JWT authentication
│   ├── service_client.py      # Inter-service communication
│   ├── exceptions.py          # Custom exceptions
│   └── requirements-base.txt
├── init-db/                   # Database initialization
│   └── 01-init.sql
└── services/
    ├── auth-service/
    ├── menu-service/
    ├── billing-service/
    ├── customer-service/
    ├── table-service/
    ├── staff-service/
    ├── reservation-service/
    └── dashboard-service/
```

## 🔐 Environment Variables

| Variable | Default | Mô tả |
|----------|---------|-------|
| `MYSQL_ROOT_PASSWORD` | MinhDucA123@ | MySQL root password |
| `SECRET_KEY` | - | Django secret key |
| `DEBUG` | False | Debug mode |
| `DB_HOST` | mysql | Database host |
| `DB_PORT` | 3306 | Database port |
| `DB_NAME` | restaurant_erp | Database name |

## 🐛 Troubleshooting

### Service không kết nối được database
```bash
# Kiểm tra MySQL đã ready chưa
docker-compose logs mysql

# Restart service
docker-compose restart auth-service
```

### Port đã bị sử dụng
```bash
# Thay đổi port mapping trong docker-compose.yml
# Ví dụ: "8001:8000" -> "9001:8000"
```

### Xóa và rebuild hoàn toàn
```bash
docker-compose down -v
docker system prune -a
docker-compose up --build -d
```

## 📄 License

MIT License
