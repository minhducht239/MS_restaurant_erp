# BÁO CÁO: XÂY DỰNG HỆ THỐNG ERP NHÀ HÀNG SỬ DỤNG KIẾN TRÚC MICROSERVICES VÀ TRIỂN KHAI TRÊN DIGITALOCEAN

## MỤC LỤC

**CHƯƠNG 1: TỔNG QUAN VỀ KIẾN TRÚC MICROSERVICES VÀ SERVERLESS**
- 1.1. Giới thiệu về Microservices
- 1.2. Serverless Architecture 
- 1.3. So sánh các mô hình kiến trúc
- 1.4. Ưu nhược điểm của từng mô hình

**CHƯƠNG 2: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG**
- 2.1. Phân tích yêu cầu hệ thống ERP nhà hàng
- 2.2. Thiết kế kiến trúc Microservices
- 2.3. Lựa chọn công nghệ và platform triển khai
- 2.4. Thiết kế database và API

**CHƯƠNG 3: TRIỂN KHAI VÀ ĐÁNH GIÁ** (Tuần sau)
- 3.1. Triển khai trên DigitalOcean
- 3.2. Testing và monitoring
- 3.3. Đánh giá hiệu suất và chi phí

---

## CHƯƠNG 1: TỔNG QUAN VỀ KIẾN TRÚC MICROSERVICES VÀ SERVERLESS

### 1.1. Microservices Architecture

#### 1.1.1. Định nghĩa
Microservices là một phương pháp thiết kế phần mềm trong đó một ứng dụng lớn được chia thành nhiều service nhỏ, độc lập, mỗi service chịu trách nhiệm cho một chức năng nghiệp vụ cụ thể.

#### 1.1.2. Đặc điểm chính của Microservices
- **Độc lập về mặt triển khai**: Mỗi service có thể được deploy, scale và update độc lập
- **Tách biệt về dữ liệu**: Mỗi service quản lý database riêng
- **Giao tiếp qua API**: Các service tương tác thông qua RESTful API hoặc message queue
- **Công nghệ đa dạng**: Mỗi service có thể sử dụng ngôn ngữ/framework khác nhau
- **Tổ chức team**: Mỗi team chịu trách nhiệm cho một hoặc vài service

#### 1.1.3. Ví dụ trong hệ thống ERP nhà hàng
```
Hệ thống ERP Restaurant được chia thành:
├── Auth Service (Django) - Xác thực, phân quyền
├── Menu Service (Django) - Quản lý thực đơn
├── Order Service (Django) - Xử lý đặt hàng  
├── Payment Service (Django) - Thanh toán
├── Customer Service (Django) - Quản lý khách hàng
├── Staff Service (Django) - Quản lý nhân viên
├── Inventory Service (Django) - Quản lý kho
└── Frontend (React) - Giao diện người dùng
```

### 1.2. Serverless Architecture

#### 1.2.1. Định nghĩa
Serverless là mô hình điện toán đám mây cho phép nhà phát triển chạy code mà không cần quản lý server. Cloud provider tự động xử lý việc provisioning, scaling và quản lý infrastructure.

#### 1.2.2. Đặc điểm chính của Serverless
- **No server management**: Không cần quản lý server, OS, runtime
- **Auto-scaling**: Tự động scale từ 0 đến vô hạn dựa trên traffic
- **Pay-per-execution**: Chỉ trả tiền khi code chạy, không có idle cost
- **Event-driven**: Kích hoạt bởi events (HTTP request, database change, file upload...)
- **Stateless**: Mỗi function execution là độc lập

#### 1.2.3. Ví dụ Serverless Functions
```javascript
// DigitalOcean Functions - Process Payment
exports.main = async (event) => {
  const { orderId, amount, paymentMethod } = event.body;
  
  // Xử lý thanh toán
  const paymentResult = await processPayment(amount, paymentMethod);
  
  return {
    statusCode: 200,
    body: { success: true, transactionId: paymentResult.id }
  };
};
```

### 1.3. So sánh các mô hình kiến trúc

| Tiêu chí | Monolith | Microservices | Serverless |
|----------|----------|---------------|------------|
| **Complexity** | Thấp | Cao | Trung bình |
| **Scalability** | Hạn chế | Linh hoạt | Tự động |
| **Development Speed** | Nhanh (ban đầu) | Chậm (ban đầu), nhanh (lâu dài) | Nhanh |
| **Deployment** | Đơn giản | Phức tạp | Rất đơn giản |
| **Monitoring** | Dễ | Khó | Trung bình |
| **Cost** | Cố định | Tăng theo scale | Pay-per-use |
| **Team Size** | Nhỏ-Trung | Lớn | Nhỏ-Trung |

### 1.4. Ưu nhược điểm của từng mô hình

#### 1.4.1. Microservices
**Ưu điểm:**
- Scalability tốt: Scale từng service độc lập
- Technology diversity: Mỗi service dùng tech stack phù hợp
- Fault isolation: Lỗi ở một service không ảnh hưởng toàn bộ
- Team autonomy: Các team làm việc độc lập

**Nhược điểm:**
- Network complexity: Nhiều API calls giữa services
- Data consistency: Khó đảm bảo ACID transactions
- Operational overhead: Cần monitoring, logging phức tạp
- Testing complexity: Integration testing khó khăn

#### 1.4.2. Serverless
**Ưu điểm:**
- No infrastructure management
- Automatic scaling (0 to ∞)
- Cost-effective cho workload biến động
- Fast time-to-market

**Nhược điểm:**
- Vendor lock-in
- Cold start latency
- Limited execution time
- Difficult local development

---

## CHƯƠNG 2: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG

### 2.1. Phân tích yêu cầu hệ thống ERP nhà hàng

#### 2.1.1. Functional Requirements
- **Quản lý thực đơn**: CRUD menu items, categories, pricing
- **Đặt hàng**: Order processing, table management
- **Thanh toán**: Multiple payment methods, billing
- **Quản lý khách hàng**: Customer profiles, loyalty points
- **Quản lý nhân viên**: Staff scheduling, roles, permissions
- **Báo cáo**: Sales reports, inventory reports
- **Tích hợp**: Google OAuth, payment gateways

#### 2.1.2. Non-functional Requirements
- **Performance**: Response time < 500ms
- **Scalability**: Handle 1000+ concurrent users
- **Availability**: 99.9% uptime
- **Security**: OAuth 2.0, JWT authentication
- **Maintainability**: Easy to update individual services

### 2.2. Thiết kế kiến trúc Microservices

#### 2.2.1. Service Decomposition
Chia hệ thống thành 8 microservices chính:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Load Balancer │
│   (React)       │───▶│   (Nginx)       │───▶│   (DigitalOcean)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
┌───────▼────────┐    ┌───────────▼────────┐    ┌───────────▼────────┐
│  Auth Service  │    │   Menu Service     │    │  Order Service     │
│  (Port 8001)   │    │   (Port 8002)      │    │  (Port 8003)       │
└────────────────┘    └────────────────────┘    └────────────────────┘
        │                         │                         │
┌───────▼────────┐    ┌───────────▼────────┐    ┌───────────▼────────┐
│Payment Service │    │ Customer Service   │    │  Staff Service     │
│ (Port 8004)    │    │  (Port 8005)       │    │  (Port 8006)       │
└────────────────┘    └────────────────────┘    └────────────────────┘
        │                         │                         │
┌───────▼────────┐    ┌───────────▼────────┐    
│Inventory Service│   │Dashboard Service   │    
│ (Port 8007)    │    │  (Port 8008)       │    
└────────────────┘    └────────────────────┘    
```

#### 2.2.2. Database Design per Service
```sql
-- Auth Service Database
Users Table: id, email, password_hash, role, created_at
Sessions Table: session_id, user_id, expires_at

-- Menu Service Database  
Categories Table: id, name, description
MenuItems Table: id, name, price, category_id, available

-- Order Service Database
Orders Table: id, customer_id, table_id, status, total_amount
OrderItems Table: order_id, menu_item_id, quantity, price

-- Customer Service Database
Customers Table: id, name, email, phone, loyalty_points
Reservations Table: id, customer_id, table_id, datetime

-- Payment Service Database
Payments Table: id, order_id, amount, method, status
Transactions Table: id, payment_id, gateway_response

-- Staff Service Database
Staff Table: id, name, position, salary, schedule
Shifts Table: id, staff_id, start_time, end_time

-- Inventory Service Database
Ingredients Table: id, name, unit, stock_quantity
Recipes Table: id, menu_item_id, ingredient_id, quantity

-- Dashboard Service (Read-only views)
Aggregated data from other services
```

### 2.3. Lựa chọn công nghệ và platform triển khai

#### 2.3.1. Tech Stack
- **Backend**: Django REST Framework (Python)
- **Frontend**: React.js với Material-UI
- **Database**: MySQL (DigitalOcean Managed Database)
- **Authentication**: JWT + Google OAuth 2.0
- **Containerization**: Docker
- **Orchestration**: DigitalOcean App Platform / Kubernetes
- **API Gateway**: Nginx
- **Monitoring**: DigitalOcean Monitoring

#### 2.3.2. DigitalOcean Services Selection

##### Option 1: App Platform (Serverless-like)
```yaml
Chi phí ước tính:
- 8 Backend Services × $5/month = $40
- 1 Frontend Static Site = Free  
- 1 MySQL Database = $15/month
- Total: $55/month

Ưu điểm:
+ Auto-scaling
+ Zero server management  
+ Built-in CI/CD
+ SSL certificates tự động

Nhược điểm:
- Đắt hơn với nhiều services
- Ít control về infrastructure
```

##### Option 2: Droplets (VPS)
```yaml
Chi phí ước tính:
- 1 Droplet 4GB = $24/month
- 1 MySQL Database = $15/month
- Total: $39/month

Ưu điểm:
+ Rẻ hơn đáng kể
+ Full control
+ Có thể optimize performance

Nhược điểm:
- Cần quản lý server
- Manual scaling
- Phức tạp hơn về setup
```

##### Option 3: Kubernetes (DO Kubernetes)
```yaml
Chi phí ước tính:
- 2 Worker Nodes 2GB × $12 = $24/month
- 1 Load Balancer = $12/month
- 1 MySQL Database = $15/month
- Total: $51/month

Ưu điểm:
+ Auto-scaling pods
+ High availability
+ Industry standard

Nhược điểm:
- Learning curve cao
- Phức tạp setup
```

### 2.4. Thiết kế API và Communication

#### 2.4.1. API Gateway Pattern
```nginx
# Nginx configuration for API Gateway
upstream auth_service {
    server auth-service:8001;
}

upstream menu_service {
    server menu-service:8002;
}

server {
    listen 80;
    
    # Route to Auth Service
    location /api/auth/ {
        proxy_pass http://auth_service/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Route to Menu Service
    location /api/menu/ {
        proxy_pass http://menu_service/;
        # Add authentication middleware
        auth_request /auth;
    }
    
    # Authentication endpoint
    location /auth {
        internal;
        proxy_pass http://auth_service/verify;
        proxy_pass_request_body off;
    }
}
```

#### 2.4.2. Inter-service Communication
```python
# Service-to-service communication example
class OrderService:
    async def create_order(self, order_data):
        # 1. Validate menu items from Menu Service
        menu_items = await self.menu_service_client.get_items(
            order_data.item_ids
        )
        
        # 2. Check customer from Customer Service  
        customer = await self.customer_service_client.get_customer(
            order_data.customer_id
        )
        
        # 3. Create order
        order = Order.objects.create(**order_data)
        
        # 4. Process payment via Payment Service
        payment_result = await self.payment_service_client.process_payment({
            'order_id': order.id,
            'amount': order.total_amount,
            'customer_id': customer.id
        })
        
        return order, payment_result
```

#### 2.4.3. Database per Service Pattern
```python
# Each service has its own database
DATABASES = {
    'auth_db': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'auth-db.mysql.ondigitalocean.com',
        'NAME': 'auth_service'
    },
    'menu_db': {
        'ENGINE': 'django.db.backends.mysql', 
        'HOST': 'menu-db.mysql.ondigitalocean.com',
        'NAME': 'menu_service'
    }
}

# Cross-service data access via APIs only
class OrderViewSet(viewsets.ModelViewSet):
    def create(self, request):
        # Don't access Menu database directly
        # Call Menu Service API instead
        menu_response = requests.get(
            f"{MENU_SERVICE_URL}/api/items/{item_id}"
        )
```

---

## PLAN TRIỂN KHAI TUẦN TỚI

### Tuần này (Chương 1 + 2):
- [x] Nghiên cứu lý thuyết Microservices vs Serverless  
- [x] Phân tích requirements và thiết kế architecture
- [x] Lựa chọn tech stack và DigitalOcean services
- [x] Thiết kế database và API contracts
- [ ] Viết báo cáo chi tiết 2 chương đầu

### Tuần tới (Chương 3 - Implementation):
- [ ] Setup DigitalOcean infrastructure
- [ ] Deploy services lên App Platform
- [ ] Configure API Gateway và Load Balancer  
- [ ] Implement monitoring và logging
- [ ] Performance testing và optimization
- [ ] Cost analysis và recommendations
- [ ] Viết báo cáo đánh giá kết quả

### Deliverables:
1. **Báo cáo hoàn chỉnh** (20-30 trang)
2. **Source code** đầy đủ trên GitHub
3. **Live demo** trên DigitalOcean
4. **Presentation slides** để demo

---

## TÀI LIỆU THAM KHẢO
1. Martin Fowler - Microservices Architecture
2. DigitalOcean Documentation - App Platform 
3. AWS Serverless Application Lens
4. Microservices Patterns - Chris Richardson
5. Building Event-Driven Microservices - Adam Bellemare