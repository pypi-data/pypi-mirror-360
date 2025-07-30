# coding: utf-8

"""
    The API

    This is the YellowSapphire Backend. Carefully read the rest of this document.   **Rate Limits**: 100 requests/minute (public), 1000 requests/minute (authenticated)  ## Authentication & Authorization  **Token-Based Authentication**: All endpoints require JWT bearer tokens obtained via login endpoints.  **Access Control**: Role-based permissions with four distinct access levels:  ``` Admin      - System-wide access: User management, system configuration, all operations Customer   - Account-scoped: Product browsing, order placement, account management   Fulfillment - Order-scoped: Inventory management, order processing, product configuration Logistics  - Delivery-scoped: Shipping coordination, delivery tracking, route management ```  **Get a Token**: 1. Authenticate via `/admin/login` or `/customer/login` endpoints 2. Copy pasta the token from a 200 auth response 3. Include in requests: `Authorization: Bearer <token>` 4. Use \"Authorize\" button above for interactive testing  ## Implementation Notes  - JSON responses with standardized error handling - Real-time with fcm/ws/mongochangestreams   - correlation IDs for request tracing - JWT auth with rbac - fulfillment workflow with qa - Global Error Handler middleware    ## Logging & Monitoring **Structured Logging System**  Centralized logging with correlation ID tracking across API requests, database operations, performance metrics, and security events. JSON format optimized for log aggregation systems.  ### Status Indicators - **●** Request initiated / Processing started - **◐** Validation / Intermediate processing step - **✓** Operation completed successfully - **▲** Warning condition detected - **✗** Error or failure state - **⚡** Performance critical operation - **🔒** Security-related event  ### Request Tracing & Correlation IDs  **End-to-End Request Tracking:** Each API request receives a unique correlation ID that propagates through all system layers for distributed tracing and debugging.  **Correlation ID Format**: `req-{32-character-hex}` (e.g., `req-309edd90d27d3ab635d57e98697bc47d`) - Generated at request entry point and returned in `X-Correlation-ID` header - Enables complete request tracing across all system layers  **Timestamp Format**: ISO 8601 with millisecond precision (`2025-07-02T21:24:32.847Z`)  ### Log Format Structured JSON log format compatible with log aggregation systems (ELK Stack, Splunk, Datadog).  **Standard Log Structure:** ```json {   \"@timestamp\": \"2025-07-02T21:24:32.847Z\",   \"@level\": \"info\",   \"service\": {     \"name\": \"yellowsapphire-backend\",     \"version\": \"2.2.0\",     \"environment\": \"production\"   },   \"location\": {     \"source\": \"controller\",     \"module\": \"CustomerController\",     \"method\": \"CustomerLogin\"   },   \"message\": \"✓ [CUSTOMER.LOGIN.3] Customer authentication successful\",   \"data\": {     \"correlationId\": \"req-309edd90d27d3ab635d57e98697bc47d\",     \"ip\": \"197.242.156.23\",     \"userAgent\": \"Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)\",     \"engineering\": {       \"functionName\": \"CustomerLogin()\",       \"operationResult\": \"authentication_successful\",       \"authenticationDuration\": \"89ms\",       \"databaseQueryDuration\": \"12ms\",       \"totalOperationDuration\": \"156ms\",       \"performanceCategory\": \"acceptable\",       \"securityEvent\": \"customer_login_success\",       \"customerId\": \"60f7b8c...\",       \"responseStatus\": 200,       \"jwtTokenGenerated\": true,       \"loginAttemptNumber\": 1     }   },   \"metadata\": {     \"processId\": 1954,     \"hostname\": \"api-server-prod-01\",     \"memoryUsageMB\": 375,     \"uptime\": \"4h 18m 32s\",     \"requestMethod\": \"POST\",     \"endpoint\": \"/api/customer/login\",     \"statusCode\": 200   } } ```    ### Log Categories & Workflow Steps  Each business operation is broken down into numbered steps that trace the complete workflow. This allows precise debugging and performance monitoring at each stage.  **Feedback Mechanisms & Quality Assurance:** - **[CUSTOMER.RATING]**: Product and service rating submission with quality metrics - **[FEEDBACK.COLLECTION.1-4]**: Customer satisfaction surveys and feedback processing - **[QUALITY.REVIEW.1-3]**: Internal quality assurance workflows and improvement tracking - **[SUPPORT.TICKET.1-5]**: Customer support ticket lifecycle management - **[PERFORMANCE.FEEDBACK]**: System performance feedback loops and optimization triggers  **MongoDB Change Streams & Real-time Events:**  | Change Stream | Collection | Event Types | Socket.IO Event | Purpose | |---------------|------------|-------------|-----------------|---------| | **Product Stream** | `products` | insert, update, delete | `inventory:product_update` | New product creation, price changes, description updates | | **Inventory Stream** | `products` | update (stock field) | `inventory:stock_change` | Stock level modifications, low stock alerts | | **Order Stream** | `orders` | insert, update | `orders:status_change` | Order creation, status transitions, delivery updates | | **Stock Reservation Stream** | `stockreservations` | insert, update, delete | `inventory:reservation_update` | Stock holds, reservation expiry, release events | | **Inventory Transaction Stream** | `inventorytransactions` | insert | `inventory:transaction` | Stock movements, audit trail, transaction analytics | | **Customer Stream** | `customers` | insert, update | `customer:profile_update` | Registration, profile changes, verification status | | **Admin Stream** | `admins` | insert, update, delete | `admin:user_management` | Admin user lifecycle, permission changes | | **Category Stream** | `categories` | insert, update, delete | `catalog:category_update` | Category structure changes, navigation updates | | **Banner Stream** | `adbanners` | insert, update, delete | `content:banner_update` | Marketing content changes, campaign updates |  **Change Stream Processing Workflow:** ``` 1. MongoDB Change Event → 2. Change Stream Processor → 3. Event Transformation → 4. Socket.IO Broadcast → 5. Client Handlers ```  **Real-time Notification Triggers:** - **Low Stock Alert**: Triggered when product quantity ≤ reorder level - **Order Status Change**: Immediate notification on status transitions - **New Product Alert**: Admin notification for product additions - **Critical Stock**: Emergency alerts for zero inventory  ### MongoDB Transaction System & ACID Compliance  **Transaction-Safe Order Processing:**  Critical business operations (order creation, inventory updates, payment processing) are wrapped in MongoDB transactions to ensure data consistency and ACID compliance.  **Transaction Service Features:** - **Automatic Retry Logic**: Exponential backoff for transient failures (network issues, write conflicts) - **Rollback Guarantee**: Automatic transaction rollback on any operation failure - **Correlation ID Tracking**: Complete transaction tracing through distributed systems - **Performance Monitoring**: Transaction duration and retry metrics - **Business-Friendly Logging**: Non-technical log messages for operations teams  **Transaction Log Categories:** - **[DATABASE.TRANSACTION.1-N]**: Individual transaction attempt tracking - **[DATABASE.SEQUENCE.1-N]**: Sequential operation execution within transactions - **[DATABASE.TRANSACTION.FAILED]**: Terminal transaction failures after all retries  **Supported Operations:** ``` • Order Creation (Customer + Order + Inventory Update) • Stock Reservations (Reserve + Timeout + Release) • Payment Processing (Payment + Order Status + Notification) • Inventory Adjustments (Stock + Transaction Log + Audit Trail) ```  **Transaction Configuration:** - **Read Concern**: majority (consistent reads) - **Write Concern**: majority with journal acknowledgment - **Max Retries**: 3 attempts with exponential backoff - **Timeout**: 30 seconds per transaction - **Retry Delays**: 100ms, 200ms, 400ms  **Error Handling:** ``` Retryable Errors: TransientTransactionError, UnknownTransactionCommitResult, WriteConflict Non-Retryable: ValidationError, AuthenticationError, BusinessLogicError ``` - **Payment Confirmation**: Real-time order payment updates   #### **Order Management Workflows**  **Order Placement Flow:** ```mermaid graph LR A[Customer Request] --> B[ORDER.1 Validate] B --> C[ORDER.2 Check Stock] C --> D[ORDER.3 Process Payment] D --> E[ORDER.4 Reserve Stock] E --> F[ORDER.5 Create Order] F --> G[ORDER.6 Notify Customer] ```  **Admin Order Management:** ```mermaid graph TD A[Admin Login] --> B[ADMIN.ORDERS.1 Auth Check] B --> C[ADMIN.ORDERS.2 Query Orders] C --> D[ADMIN.ORDERS.3 Format Response] ```  - **[CUSTOMER.ORDER.1-6]**: Complete order placement process - **[ADMIN.ORDERS.1-3]**: Order management operations - **[ADMIN.ORDER_GET.2]**: Order details retrieval by admin - **[ADMIN.ORDER_STATUS.2]**: Order status updates - **[ORDERS.GET]**: General order queries  #### **Product & Inventory Management**  **Product Creation Flow:** ``` [Admin Request] --> [PRODUCT.1 Validate]  --> [PRODUCT.2 Barcode Lookup] --> [PRODUCT.3 Process Data] --> [PRODUCT.4 Save & Initialize] ```  **Inventory Update Flow:** ``` [Stock Request] --> B[INVENTORY.1 Validate]   --> [INVENTORY.2 Lock Transaction]  --> [INVENTORY.3 Calculate] --> [INVENTORY.4 Update DB] --> INVENTORY.5 Notify] ```  - **[ADMIN.PRODUCT.1-4]**: Product management workflow - **[INVENTORY.1-5]**: Stock operation tracking - **[ADMIN.PRODUCTS.1-2]**: Product catalog management - **[ADMIN.PRODUCT_GET.2]**: Individual product administration - **[ADMIN.BARCODE_LOOKUP]**: Product lookup via barcode scanning - **[ADMIN.CREATE_FROM_BARCODE.2]**: Product creation from barcode data - **[ADMIN.BULK_PRODUCTS]**: Bulk product operations - **[ADMIN.STOCK]**: Inventory level management - **[ADMIN.CATEGORY_CREATE.1]**: Product category creation  #### **Shopping & E-commerce Workflows**  **Customer Shopping Journey:** ```mermaid graph TD A[Browse Categories] --> B[Search Products] B --> C[View Product Details] C --> D[Check Availability] D --> E[Add to Cart] E --> F[Checkout]  A -.-> G[SHOP.CATEGORIES] B -.-> H[SHOP.SEARCH] C -.-> I[SHOP.DETAIL.1-3] D -.-> J[SHOP.AVAILABILITY.2] E -.-> K[CART.ADD] F -.-> L[ORDER.1-6] ```  **Offers & Promotions Flow:** ```mermaid graph LR A[Request Offers] --> B[OFFERS.1 Validate PostCode] B --> C[OFFERS.2 Query Active] C --> D[OFFERS.3 Check Expiry] D --> E[OFFERS.4-6 Return Results] ```  - **[SHOP.SEARCH]**: Product search and filtering - **[SHOP.PRODUCT_DETAIL.1-3]**: Product detail retrieval with availability check - **[SHOP.CATEGORIES]**: Category browsing and navigation - **[SHOP.FEATURED.1-2]**: Featured products display - **[SHOP.OFFERS.1-6]**: Special offers and promotions workflow - **[SHOP.QUICK_DELIVERY.1-2]**: Express delivery options - **[SHOP.TOP_STORES.1-2]**: Popular store listings - **[SHOP.STORE_BY_ID.1-2]**: Individual store information - **[SHOP.PRODUCT_AVAILABILITY.2]**: Real-time stock checking  #### **Cart Management Workflows** - **[CART.GET]**: Cart contents retrieval - **[CART.DELETE_ITEM.1-5]**: Individual item removal from cart - **[CART.CLEAR.2-6]**: Complete cart clearance  #### **Customer Management Workflows**  **Customer Registration Flow:** ```mermaid graph TD A[Registration Request] --> B[SIGNUP.1 Validate] B --> C[SIGNUP.2 Hash Password] C --> D[SIGNUP.3 Check Email] D --> E[SIGNUP.4 Create Account] E --> F[SIGNUP.5 Generate JWT] F --> G[SIGNUP.6 Notify Admins] G --> H[SIGNUP.7 Send Welcome] H --> I[SIGNUP.8 Return Response] I --> J[SIGNUP.9 Log Complete] ```  **Authentication & Verification:** ```mermaid graph LR A[Login Request] --> B[LOGIN.1-3 Process] A --> C[Google OAuth] C --> D[GOOGLE_LOGIN] B --> E[OTP Request] E --> F[OTP.1-6 Generate] F --> G[VERIFY.1-6 Validate] ```  - **[CUSTOMER.SIGNUP.1-9]**: Complete customer registration process   - **[CUSTOMER.SIGNUP.1]**: Initial request processing - correlation ID generation and metadata capture   - **[CUSTOMER.SIGNUP.1.1]**: DTO validation using class-validator - email, phone, password, firstName, lastName format checks   - **[CUSTOMER.SIGNUP.1.2]**: Field-level validation - email normalization, phone format (10 digits), password strength (6-20 chars)   - **[CUSTOMER.SIGNUP.2]**: Cryptographic operations - bcrypt salt generation and password hashing with performance tracking   - **[CUSTOMER.SIGNUP.3]**: Email uniqueness validation - database query Customer.findOne({email}) to prevent duplicates   - **[CUSTOMER.SIGNUP.4]**: Customer account creation - MongoDB document with default values (verified: false, receivemarketing: true)   - **[CUSTOMER.SIGNUP.5]**: JWT token generation - 1-day expiration with customer ID, email, and verification status claims   - **[CUSTOMER.SIGNUP.6]**: FCM notification to admins - Firebase topic 'admin' with new signup alert (non-blocking)   - **[CUSTOMER.SIGNUP.7]**: Welcome email dispatch - Brevo SMTP with Handlebars template to customer email (asynchronous)   - **[CUSTOMER.SIGNUP.8]**: Response preparation - 201 status with token, verified: false, email, and success message   - **[CUSTOMER.SIGNUP.9]**: Completion logging - total duration tracking and correlation ID logging - **[CUSTOMER.LOGIN.1-3]**: Customer authentication with OAuth support - **[CUSTOMER.GOOGLE_LOGIN]**: Google OAuth integration - **[CUSTOMER.OTP_REQUEST.1-6]**: OTP generation and delivery (SMS currently disabled) - **[CUSTOMER.VERIFY.1-6]**: Account verification process with OTP validation - **[CUSTOMER.PROFILE_GET.2]**: Customer profile retrieval - **[CUSTOMER.PROFILE_EDIT.1-4]**: Profile update operations - **[CUSTOMER.FIREBASE_TOKEN.1-4]**: Firebase token management for notifications - **[CUSTOMER.ORDER_GET.1]**: Customer order history - **[CUSTOMER.RATING]**: Product and service rating submission  #### **Admin Management Workflows** - **[ADMIN.CREATE]**: New admin account creation - **[ADMIN.UPDATE.1-4]**: Admin profile updates - **[ADMIN.DELETE]**: Admin account deletion - **[ADMIN.GET_BY_ID.1-2]**: Individual admin retrieval - **[ADMIN.LIST.1-2]**: Admin user listing - **[ADMIN.PASSWORD_RESET.1-5]**: Admin password reset process - **[ADMIN.CUSTOMER_LIST.1-3]**: Customer management operations - **[ADMIN.CUSTOMER_UPDATE.1-3]**: Customer profile administration - **[ADMIN.CUSTOMER_DELETE.2]**: Customer account removal - **[ADMIN.CUSTOMER_GET.2]**: Customer profile retrieval by admin   #### **Content Management Workflows** - **[ADMIN.BANNER_CREATE.1-3]**: Advertisement banner creation - **[ADMIN.BANNER_UPDATE.1-5]**: Banner content updates - **[ADMIN.BANNER_LIST.1-3]**: Banner management and listing  #### **Payment Processing Workflows** - **[PAYMENT.GATEWAY]**: Payment gateway integration - **[PAYMENT.GATEWAY.BANK]**: Bank transfer processing - **[PAYMENT.GATEWAY.GPAY]**: Google Pay integration - **[PAYMENT.GATEWAY.PO]**: Purchase order processing  #### **Communication & Notifications** - **[EMAIL.1-5]**: Email delivery workflow - **[FCM.1-2]**: Push notification delivery  #### **System Operations** - **[DB.1-3]**: Database operation monitoring  - **[RATE_LIMIT]**: Security event tracking - **[VALIDATION.OBJECTID]**: Input validation for database operations - **[CORRELATION.CLEANUP]**: Request context management  ### Performance Metrics & Monitoring  **Execution Time Tracking:** Every operation includes precise timing data for performance analysis and optimization.  ```json \"engineering\": {   \"authenticationDuration\": \"89ms\",   \"databaseQueryDuration\": \"12ms\",   \"totalOperationDuration\": \"156ms\",   \"performanceCategory\": \"acceptable\" } ```  **Performance Classifications:** - **⚡ Optimal** (<100ms): Lightning fast, minimal resource usage   - *Target*: Authentication, simple queries, cache hits   - *Example*: `[CUSTOMER.PROFILE.2] Profile data retrieved (43ms) - optimal`  - **✓ Acceptable** (100-500ms): Good performance within normal range   - *Target*: Complex queries, order processing, payment validation   - *Example*: `[ORDER.CREATE.3] Payment processing completed (287ms) - acceptable`  - **▲ Slow** (500ms-2s): Requires attention, may impact user experience   - *Action*: Investigate query optimization, caching opportunities   - *Example*: `[INVENTORY.2] Stock calculation completed (743ms) - slow`  - **✗ Critical** (>2s): Unacceptable performance, immediate optimization required   - *Action*: Emergency investigation, potential timeout issues   - *Example*: `[EMAIL.4] SMTP delivery attempt (2.1s) - critical`  **System Resource Monitoring:** - **Memory Usage**: V8 heap utilization and garbage collection patterns - **Database Performance**: Connection pool status, query execution times - **External APIs**: Response times for barcode lookups, payment processors - **Security Operations**: Cryptographic operation timing (bcrypt, JWT) - **Network Operations**: SMTP delivery, FCM push notifications  ### Security & Privacy Protection  **Data Sanitization Standards:** All sensitive data is automatically sanitized before logging to prevent accidental exposure.  ``` Passwords      → password: [HIDDEN]      (Authentication tracking without credentials) JWT Tokens     → authorization: [HIDDEN] (Security without token exposure) API Keys       → apikey: [HIDDEN]        (Access tracking without key exposure) Email Addresses → email: [HIDDEN]        (User identification with privacy protection) Phone Numbers  → phone: [HIDDEN]         (Contact tracking without number exposure) ```  **Security Event Tracking:** - **Authentication Events**: Login attempts, failures, security violations - **Authorization Events**: Permission checks, role validations, access denials - **Rate Limiting**: Request frequency monitoring and abuse detection - **Input Validation**: Malicious input detection and sanitization - **Session Management**: Token lifecycle, expiration, and invalidation  **Compliance & Auditing:** - **GDPR Compliance**: No personal data in logs, sanitized identifiers only - **Security Auditing**: All authentication and authorization events tracked - **Incident Response**: Correlation IDs enable complete request tracing - **Performance Auditing**: System performance tracking for SLA compliance  ### Error Handling & Recovery  **Environment-Specific Error Reporting:** - **Development**: Detailed stack traces, variable states, debugging context - **Production**: Sanitized error messages with correlation IDs for internal tracking  **Error Categories & Response Strategies:**  | Error Type | Log Pattern | Recovery Action | User Impact | |------------|-------------|-----------------|-------------| | Validation Errors | `[VALIDATION.ERROR]` | Return 400 with specific field errors | Immediate feedback for correction | | Authentication Failures | `[AUTH.ERROR]` | Return 401, log security event | Redirect to login, rate limit protection | | Authorization Violations | `[AUTHZ.ERROR]` | Return 403, audit trail | Access denied with support contact | | Database Errors | `[DB.ERROR]` | Retry logic, fallback queries | Temporary service degradation notice | | External API Failures | `[API.ERROR]` | Circuit breaker, cached responses | Graceful degradation or retry prompts | | Business Logic Errors | `[BUSINESS.ERROR]` | Transaction rollback, state recovery | Clear error message with resolution steps |  **Error Context Preservation:** ```json {   \"error\": {     \"message\": \"Validation failed for customer profile\",     \"code\": \"VALIDATION_ERROR\",     \"details\": {       \"field\": \"email\",       \"reason\": \"Invalid email format\",       \"providedValue\": \"user...@invalid\"     }   } } ```  ### Security Headers - **X-Content-Type-Options**: Prevents MIME type sniffing - **X-Frame-Options**: Protects against clickjacking attacks   - **X-XSS-Protection**: Enables browser XSS filtering - **Content-Security-Policy**: Restricts resource loading   ### Company Information **Website**: [yellowsapphire.co.za](https://yellowsapphire.co.za)   **Business**: Computer Equipment   **Location**: Fourways, Johannesburg  ## Timezone  - **Format**: ISO 8601 with timezone offset (e.g., `2025-06-22T16:30:45.123+02:00`)  ## Error Handling & Response Format **Structured Error Response System**  All API errors follow a consistent, structured format for predictable error handling and debugging.  ### Standard Error Response Format ```json {   \"error\": \"VALIDATION_FAILED\",   \"message\": \"Human-readable error description\",   \"correlationId\": \"req-b54f0f5afc234b1239cc5ff6bc8f1bdc\",   \"timestamp\": \"2025-07-03T02:32:17.941Z\",   \"details\": [     {       \"field\": \"email\",       \"constraint\": \"required\",       \"value\": \"\",       \"message\": \"Email is required\"     }   ] } ```  ### Error Types & HTTP Status Codes  | Error Type | HTTP Status | Description | Use Case | |------------|-------------|-------------|----------| | `VALIDATION_FAILED` | 400 | Invalid input data or missing required fields | Form validation, parameter validation | | `AUTHENTICATION_FAILED` | 401 | Invalid or missing authentication credentials | Login failures, expired tokens | | `AUTHORIZATION_FAILED` | 403 | Insufficient permissions for requested resource | Role-based access control violations | | `RESOURCE_NOT_FOUND` | 404 | Requested resource does not exist | Invalid IDs, deleted resources | | `CONFLICT` | 409 | Resource conflict or duplicate data | Duplicate email registration, concurrent modifications | | `BUSINESS_ERROR` | 422 | Business rule violation | Insufficient stock, order cancellation rules | | `INTERNAL_SERVER_ERROR` | 500 | Unexpected server error | Database failures, external service errors |   ### Business Logic Errors (422) Include business rule context and error codes: ```json {   \"error\": \"BUSINESS_ERROR\",   \"message\": \"Order cannot be cancelled. Current status: shipped\",   \"code\": \"ORDER_NOT_CANCELLABLE\",   \"correlationId\": \"req-def456...\",   \"timestamp\": \"2025-07-03T02:32:17.941Z\" } ```  ### Error Response Headers All error responses include these headers: - `X-Correlation-ID`: Request correlation ID for tracing - `Content-Type`: `application/json` - `X-RateLimit-*`: Rate limiting information (when applicable)  ### Client Error Handling Best Practices 1. **Always check the `error` field** for programmatic error handling 2. **Use `correlationId`** when reporting issues to support 3. **Parse `details` array** for field-specific validation errors 4. **Display `message`** to users for human-readable feedback 5. **Implement retry logic** for 5xx errors with exponential backoff  ## Real-time Events (Socket.IO) Real-time event streaming via Socket.IO WebSocket connections for inventory and order updates.  ### Connection Endpoint ```javascript // Connect to Socket.IO server const socket = io('https://yellowsapphire-backend-826925162454.africa-south1.run.app');  // Authenticate connection socket.emit('authenticate', 'your_jwt_token'); ```  ### Real-time Event Categories  #### Inventory Events 1. **inventory:product_update** - New product creation 2. **inventory:stock_change** - Stock level and reservation changes   3. **inventory:transaction** - Inventory transaction analytics 4. **inventory:reservation_update** - Stock reservation lifecycle  #### Order Events   1. **orders:status_change** - Order status transitions  #### FCM Push Notifications 1. **admin_notifications** - New order alerts 2. **inventory_alerts** - Low/critical stock alerts  ### Event Payload Structure All events include: - **timestamp**: ISO 8601 event time - **correlationId**: Request correlation tracking - **type**: Specific event type (e.g., 'product_created', 'stock_change') - **data**: Event-specific payload  ### Authentication Socket.IO connections require JWT authentication via the 'authenticate' event. Failed authentication triggers 'authentication_error' event.  ## API Versioning & Compatibility  **Current Version**: 2.2.0  **Version Strategy**: Semantic versioning (MAJOR.MINOR.PATCH) - **MAJOR**: Breaking changes requiring client updates - **MINOR**: New features with backward compatibility   - **PATCH**: Bug fixes and security updates  **Deprecation Policy**:  - 6-month notice for breaking changes - Legacy endpoint support for 2 major versions - Migration guides provided for deprecated features  ## Data Models & Relationships  **Core Entities:**  | Entity | Primary Key | Relationships | Change Stream | |--------|-------------|---------------|---------------| | **Customer** | `_id` | → Orders, Ratings | `customer:profile_update` | | **Admin** | `_id` | → Created Products, Orders | `admin:user_management` | | **Product** | `_id` | ← Categories, → Inventory | `inventory:product_update` | | **Order** | `_id` | ← Customer, → OrderItems | `orders:status_change` | | **Category** | `_id` | → Products | `catalog:category_update` | | **StockReservation** | `_id` | ← Product, ← Order | `inventory:reservation_update` | | **InventoryTransaction** | `_id` | ← Product, ← Admin | `inventory:transaction` | | **AdBanner** | `_id` | ← Admin Created | `content:banner_update` |  **Data Consistency Rules:** - Stock reservations auto-expire after 15 minutes - Order cancellation allowed only in 'pending' or 'confirmed' status - Inventory transactions maintain audit trail integrity - Customer verification required for high-value orders  ## Business Rules & Constraints  **Order Management Rules:** ```yaml Order Lifecycle:   - pending → confirmed → processing → shipped → delivered   - Cancellation: Only 'pending' and 'confirmed' statuses   - Refunds: Within 30 days of delivery   - Stock: Reserved during 'pending', committed on 'confirmed'  Inventory Rules:   - Minimum stock alerts at reorder level   - Negative stock prevention with real-time validation   - Automatic stock reservation for 15-minute checkout window   - Bulk operations require admin approval  Customer Rules:   - Email verification required for orders > R5000   - Phone verification for new accounts   - Rate limiting: 5 login attempts per 15 minutes   - Password complexity: 8+ characters, mixed case ```  **Business Validation Constraints:** - Product prices must be positive decimals - Order quantities limited to available stock + buffer - Customer profiles require validated South African phone numbers - Admin permissions hierarchical (read → write → admin → super)  ## Performance Optimization  **Caching Strategy:** - **Product Catalog**: Redis cache with 1-hour TTL - **Category Navigation**: In-memory cache with change stream invalidation - **Featured Products**: Database view with scheduled refresh - **User Sessions**: JWT stateless authentication  **Database Optimization:** - Compound indexes on frequent query patterns - Aggregation pipeline optimization for analytics - Connection pooling with 10 concurrent connections - Read replicas for reporting and analytics queries  **Response Time Targets:**  | Endpoint Category | Target Response Time | Monitoring Alert | |-------------------|---------------------|------------------| | Authentication | < 200ms | > 500ms | | Product Catalog | < 300ms | > 800ms | | Order Creation | < 1000ms | > 2000ms | | Admin Reports | < 2000ms | > 5000ms | | Real-time Events | < 50ms | > 200ms |  ## Security Implementation  **Authentication & Authorization Matrix:**  | Role | Product Management | Order Management | User Management | System Config | |------|-------------------|------------------|-----------------|---------------| | **Customer** | Read Only | Own Orders Only | Own Profile | None | | **Fulfillment** | Read/Update Stock | All Orders | None | None | | **Logistics** | Read Only | Update Shipping | None | None | | **Admin** | Full Access | Full Access | Customer Management | Limited | | **Super Admin** | Full Access | Full Access | Full Access | Full Access |  **Security Headers & Policies:** ```http Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' X-Content-Type-Options: nosniff X-Frame-Options: DENY   X-XSS-Protection: 1; mode=block Referrer-Policy: strict-origin-when-cross-origin ```  **Rate Limiting Configuration:** - **Authentication endpoints**: 5 requests/15 minutes per IP - **Password reset**: 3 requests/hour per account - **Product search**: 100 requests/minute per user - **Order creation**: 10 requests/minute per customer - **Admin operations**: 1000 requests/minute per admin  ## Integration Ecosystem  **External API Integrations:**  | Service | Purpose | Endpoint Pattern | Timeout | Retry Policy | |---------|---------|------------------|---------|--------------| | **Brevo SMTP** | Email delivery | `/v3/smtp/email` | 30s | 3 attempts | | **Firebase FCM** | Push notifications | `/fcm/send` | 10s | 2 attempts | | **Cloudinary** | Image processing | `/v1_1/{cloud}/upload` | 60s | 1 attempt | | **Barcode Lookup** | Product data | `/barcode/{ean}` | 15s | 2 attempts | | **Payment Gateway** | Transaction processing | `/payment/process` | 45s | 3 attempts |  **Integration Monitoring:** - Circuit breaker pattern for external failures - Fallback responses for non-critical integrations - Health checks for dependency monitoring - SLA tracking and alerting thresholds  ## Deployment Architecture  **Environment Configuration:**  | Environment | Server | Database | Monitoring | CDN | |-------------|--------|----------|------------|-----| | **Development** | Local Node.js | MongoDB Atlas | Console logs | Local static | | **Staging** | Google Cloud Run | MongoDB Atlas | Cloud Logging | Cloud CDN | | **Production** | Google Cloud Run | MongoDB Atlas | Cloud Operations | Cloud CDN |  **Infrastructure Components:** ```yaml Load Balancer:   - Health check: /health endpoint   - SSL termination with automatic renewal   - Geographic routing for performance  Application Layer:   - Horizontal auto-scaling (2-10 instances)   - Zero-downtime deployments   - Blue-green deployment strategy  Data Layer:   - MongoDB Atlas M10+ clusters   - Automated backups every 6 hours   - Point-in-time recovery capability   - Read replicas for analytics  Monitoring Stack:   - Google Cloud Operations Suite   - Custom dashboards for business metrics   - Alert policies for SLA violations   - Log aggregation and analysis ```  ## DevOps & CI/CD Pipeline  **Continuous Integration:** ```mermaid graph LR A[Git Push] --> B[GitHub Actions] B --> C[Lint & Test] C --> D[Build Docker Image] D --> E[Security Scan] E --> F[Deploy to Staging] F --> G[Integration Tests] G --> H[Deploy to Production] ```  **Deployment Checklist:** - ✅ All tests passing (unit, integration, e2e) - ✅ Security vulnerability scan complete - ✅ Database migration scripts validated - ✅ Environment variables updated - ✅ Monitoring alerts configured - ✅ Rollback plan documented  **Health Check Endpoints:** - `/health` - Basic server health - `/health/detailed` - Component status - `/health/dependencies` - External service status - `/metrics` - Prometheus-compatible metrics  ## Analytics & Business Intelligence  **Key Performance Indicators (KPIs):**  | Metric Category | KPI | Target | Alert Threshold | |-----------------|-----|--------|-----------------| | **Performance** | API Response Time | < 500ms | > 1000ms | | **Availability** | Uptime | 99.9% | < 99.5% | | **Business** | Order Conversion | > 15% | < 10% | | **Customer** | Registration Rate | > 5/day | < 2/day | | **Inventory** | Stock Turnover | > 80% | < 60% |  **Analytics Data Flow:** ``` User Actions → Event Logging → Data Pipeline → Analytics Dashboard → Business Insights ```  **Reporting Capabilities:** - Real-time inventory levels and alerts - Customer behavior analytics and patterns - Order fulfillment metrics and bottlenecks - Revenue tracking and forecasting - System performance and reliability metrics  ## Disaster Recovery & Business Continuity  **Backup Strategy:** - **Database**: Automated daily backups with 30-day retention - **Application Code**: Git repository with multiple remotes - **Configuration**: Infrastructure as Code (Terraform) - **Secrets**: Encrypted backup in secure vault  **Recovery Time Objectives (RTO):** - **Critical Services**: 15 minutes - **Full System**: 2 hours - **Data Recovery**: 1 hour  **Recovery Point Objectives (RPO):** - **Transactional Data**: 5 minutes - **Configuration Changes**: 1 hour - **Analytics Data**: 24 hours  **Incident Response Procedures:** 1. **Detection**: Automated monitoring alerts 2. **Assessment**: Severity classification (P0-P4) 3. **Response**: Escalation matrix activation 4. **Communication**: Status page updates 5. **Resolution**: Root cause analysis 6. **Post-mortem**: Process improvement  ## Developer Experience & Onboarding  **Development Environment Setup:** ```bash # Clone repository git clone https://github.com/company/yellowsapphire-backend  # Install dependencies npm install  # Configure environment cp .env.example .env.local  # Start development server npm run dev  # Run tests npm test ```  **API Testing Tools:** - **Postman Collections**: Pre-configured request collections - **Newman CLI**: Automated API testing - **Swagger UI**: Interactive API documentation - **Jest**: Unit and integration testing - **Supertest**: HTTP assertion testing  **Code Quality Standards:** - **TypeScript**: Strict type checking enabled - **ESLint**: Consistent code style enforcement - **Prettier**: Automatic code formatting - **Husky**: Pre-commit hooks for quality gates - **SonarQube**: Code quality and security analysis  ## Troubleshooting Guide  **Common Issues & Solutions:**  | Issue | Symptoms | Root Cause | Solution | |-------|----------|------------|----------| | **High Response Time** | API calls > 2s | Database connection pool exhaustion | Restart service, check connection limits | | **Authentication Failures** | 401 errors increasing | JWT token expiration | Verify token generation and expiry settings | | **Stock Inconsistency** | Negative inventory | Race condition in concurrent updates | Review transaction isolation levels | | **Failed Email Delivery** | Emails not sending | SMTP service disruption | Check Brevo service status and credentials | | **Real-time Events Down** | Socket.IO disconnections | WebSocket connection limits | Scale Socket.IO instances |  **Debug Information Collection:** ```bash # System health check curl http://localhost:3000/health/detailed  # Application logs docker logs yellowsapphire-backend --tail=100  # Database connection status mongosh --eval \"db.adminCommand('connPoolStats')\"  # Memory usage analysis node --inspect app.js # Enable debugger ```  **Monitoring & Alerting:** - **Error Rate**: > 5% triggers immediate alert - **Response Time**: > 1s average triggers warning - **Database**: Connection pool > 80% triggers alert - **Memory**: Heap usage > 90% triggers critical alert - **Disk Space**: < 10% free triggers urgent alert  ## Feature Flags Configuration   **Environment Variables Reference:**  | Variable | Type | Default | Description | Required | |----------|------|---------|-------------|----------| | `NODE_ENV` | string | development | Runtime environment | ✅ | | `PORT` | number | 3000 | Server listening port | ✅ | | `MONGODB_URI` | string | - | MongoDB connection string | ✅ | | `JWT_SECRET` | string | - | JWT signing secret (256-bit) | ✅ | | `JWT_EXPIRES_IN` | string | 24h | Token expiration time | ❌ | | `BCRYPT_ROUNDS` | number | 12 | Password hashing rounds | ❌ | | `RATE_LIMIT_WINDOW` | number | 900000 | Rate limit window (15 min) | ❌ | | `RATE_LIMIT_MAX` | number | 100 | Max requests per window | ❌ | | `BREVO_API_KEY` | string | - | Email service API key | ✅ | | `FIREBASE_PROJECT_ID` | string | - | Firebase project identifier | ✅ | | `CLOUDINARY_CLOUD_NAME` | string | - | Image service cloud name | ✅ | | `SOCKET_IO_CORS_ORIGIN` | string | * | WebSocket CORS origins | ❌ | | `LOG_LEVEL` | string | info | Logging verbosity level | ❌ |  **Feature Flags & Toggles:** ```json {   \"features\": {     \"realTimeInventory\": true,     \"advancedAnalytics\": true,     \"multiCurrencySupport\": false,     \"socialAuthentication\": false,     \"advancedSearch\": true,     \"bulkOperations\": true,     \"webhookNotifications\": false,     \"experimentalFeatures\": false   },   \"limits\": {     \"maxOrderItems\": 50,     \"maxFileUploadSize\": \"10MB\",     \"maxConcurrentConnections\": 1000,     \"maxBulkOperationSize\": 100   } } ```  ##Security Features  **Input Validation & Sanitization:** ```typescript // DTO Validation Pipeline Request → Class Transformer → Class Validator → Business Logic  // Sanitization Rules - SQL Injection: Parameterized queries only - XSS Prevention: HTML entity encoding - NoSQL Injection: Schema validation - Path Traversal: Whitelist allowed paths - Command Injection: Input type validation ```  **Encryption Stds:** - **Passwords**: bcrypt 12 rounds - **JWT Tokens**: HMAC SHA-256 signing - **Data at Rest**: MongoDB encryption with customer-managed keys - **Data in Transit**: TLS 1.3 minimum, perfect forward secrecy - **Sensitive Fields**: AES-256-GCM for PII data  **Security Audit Trail:** ```yaml Authentication Events:   - Login attempts (success/failure)   - Password changes   - Account lockouts   - Token generation/expiration  Authorization Events:   - Permission checks   - Role assignments   - Access denials   - Privilege escalations  Data Access Events:   - Customer data queries   - Order modifications   - Inventory adjustments   - Admin operations ```  ## Scalability & Performance Patterns  **Horizontal Scaling Architecture:** ```mermaid graph TD     A[Load Balancer] --> B[App Instance 1]     A --> C[App Instance 2]      A --> D[App Instance N]          B --> E[MongoDB Primary]     C --> E     D --> E          E --> F[MongoDB Secondary 1]     E --> G[MongoDB Secondary 2]          H[Redis Cache] --> B     H --> C     H --> D          I[Socket.IO Adapter] --> B     I --> C     I --> D ```  **Caching Strategies:**  | Cache Type | Technology | TTL | Invalidation Strategy | |------------|------------|-----|----------------------| | **Application** | In-Memory Map | 5 min | Time-based expiry | | **Database Query** | Redis | 1 hour | Change stream triggers | | **Session Data** | Redis | 24 hours | User logout/timeout | | **Static Assets** | CDN | 1 year | Version-based cache busting | | **API Responses** | Redis | 15 min | Manual invalidation |  **Database Optimization Patterns:** ```javascript // Compound Indexes for Common Queries db.products.createIndex({    \"category\": 1,    \"price\": 1,    \"stock\": 1  });  // Partial Indexes for Conditional Queries db.orders.createIndex(   { \"customerId\": 1, \"status\": 1 },   { partialFilterExpression: { \"status\": { $ne: \"cancelled\" } } } );  // Text Search Indexes db.products.createIndex({   \"name\": \"text\",   \"description\": \"text\",   \"tags\": \"text\" }); ```  ## API Client SDKs & Libraries  **Official Client Libraries:**  | Language | Package Name | Version | Documentation | |----------|--------------|---------|---------------| | **JavaScript** | `@yellowsapphire/api-client` | 2.1.0 | [JS Docs](./sdk/javascript) | | **Python** | `yellowsapphire-sdk` | 2.1.0 | [Python Docs](./sdk/python) | | **PHP** | `yellowsapphire/api-client` | 2.1.0 | [PHP Docs](./sdk/php) | | **Java** | `com.yellowsapphire:api-client` | 2.1.0 | [Java Docs](./sdk/java) |  **Client Authentication Example:** ```javascript // JavaScript SDK Usage import { YellowSapphireClient } from '@yellowsapphire/api-client';  const client = new YellowSapphireClient({   baseURL: 'https://api.yellowsapphire.co.za',   apiKey: 'your-api-key',   timeout: 30000,   retries: 3 });  // Customer authentication const session = await client.auth.login({   email: 'customer@example.com',   password: 'secure-password' });  // Make authenticated requests const orders = await client.orders.list({   page: 1,   limit: 10,   status: 'confirmed' }); ```  ## Webhook System  **Webhook Event Types:**  | Event | Trigger | Payload | Retry Policy | |-------|---------|---------|--------------| | `order.created` | New order placed | Order object + customer | 5 attempts, exponential backoff | | `order.status_changed` | Status transition | Order ID + old/new status | 3 attempts | | `inventory.low_stock` | Stock below threshold | Product ID + current stock | 2 attempts | | `customer.registered` | New account | Customer ID + profile data | 3 attempts | | `payment.confirmed` | Payment success | Order ID + payment details | 5 attempts |  **Webhook Configuration:** ```json {   \"webhooks\": [     {       \"id\": \"wh_12345\",       \"url\": \"https://your-app.com/webhooks/yellowsapphire\",       \"events\": [\"order.created\", \"order.status_changed\"],       \"secret\": \"whsec_abc123...\",       \"active\": true,       \"created_at\": \"2025-07-04T12:00:00Z\"     }   ] } ```  **Webhook Security:** - HMAC SHA-256 signature verification - Timestamp validation (5-minute window) - IP whitelist restrictions - SSL/TLS certificate validation - Idempotency key support  ## Testing Framework  **Test Categories & Coverage:**  | Test Type | Framework | Coverage Target | Execution | |-----------|-----------|-----------------|-----------| | **Unit Tests** | Jest | > 90% | Pre-commit | | **Integration Tests** | Supertest | > 80% | CI Pipeline | | **E2E Tests** | Playwright | Critical paths | Nightly | | **Load Tests** | Artillery | Performance baseline | Weekly | | **Security Tests** | OWASP ZAP | Vulnerability scan | Release |  **Test Data Management:** ```javascript // Test Database Seeding beforeEach(async () => {   await TestDatabase.clear();   await TestDatabase.seed({     customers: fixtures.customers,     products: fixtures.products,     categories: fixtures.categories   }); });  // Mock External Services jest.mock('../services/BrevoEmailService', () => ({   sendEmail: jest.fn().mockResolvedValue({ messageId: 'test-123' }) })); ```  **Performance Testing Scenarios:** ```yaml Load Test Scenarios:   Normal Load:     - 100 concurrent users     - 1000 requests per minute     - 95th percentile < 500ms      Peak Load:     - 500 concurrent users       - 5000 requests per minute     - 95th percentile < 1000ms      Stress Test:     - 1000+ concurrent users     - Identify breaking point     - Graceful degradation ```  ## Compliance & Governance  **Data Protection & Privacy:** - **POPIA Compliance**: South African data protection laws - **GDPR Compliance**: EU data protection (if applicable) - **Data Minimization**: Collect only necessary information - **Right to Deletion**: Customer data removal on request - **Data Portability**: Export customer data in standard formats  **Audit & Compliance Reporting:** ```yaml Audit Logs:   Retention: 7 years   Format: JSON with digital signatures   Storage: Immutable append-only logs   Access: Audit trail for log access  Compliance Reports:   - Monthly security review   - Quarterly access audit   - Annual penetration testing   - Continuous vulnerability scanning ```  **Regulatory Requirements:** - **Financial**: Payment Card Industry (PCI) compliance - **Consumer Protection**: South African Consumer Protection Act - **Tax**: VAT calculation and reporting requirements - **Business**: Company registration and tax compliance 

    The version of the OpenAPI document: 2.2.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import io
import warnings

from pydantic import validate_call, Field, StrictFloat, StrictStr, StrictInt
from typing import Dict, List, Optional, Tuple, Union, Any

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

from pydantic import Field
from typing_extensions import Annotated
from datetime import date

from pydantic import StrictStr, field_validator

from typing import Optional

from yellowsapphire_sdk.models.add_rating200_response import AddRating200Response
from yellowsapphire_sdk.models.add_rating_request import AddRatingRequest
from yellowsapphire_sdk.models.cancel_order200_response import CancelOrder200Response
from yellowsapphire_sdk.models.create_order201_response import CreateOrder201Response
from yellowsapphire_sdk.models.create_order_request import CreateOrderRequest
from yellowsapphire_sdk.models.get_orderby_id200_response import GetOrderbyId200Response
from yellowsapphire_sdk.models.get_orders200_response import GetOrders200Response
from yellowsapphire_sdk.models.make_payment200_response import MakePayment200Response
from yellowsapphire_sdk.models.make_payment_request import MakePaymentRequest

from yellowsapphire_sdk.api_client import ApiClient
from yellowsapphire_sdk.api_response import ApiResponse
from yellowsapphire_sdk.rest import RESTResponseType


class CustomerOrderManagementApi:
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None) -> None:
        if api_client is None:
            api_client = ApiClient.get_default()
        self.api_client = api_client


    @validate_call
    def add_rating(
        self,
        id: Annotated[str, Field(strict=True, description="**Order ID (MongoDB ObjectId)** - Must be a delivered/completed order - Order must belong to authenticated customer - Order must not have been rated previously ")],
        add_rating_request: AddRatingRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> AddRating200Response:
        """Rate and review completed order

        **Customer Feedback and Rating System**  Enable customers to provide comprehensive feedback on their completed orders, helping improve service quality and assist future customers.  **Rating Categories:** - **Overall Rating** (1-5 stars) - General satisfaction with entire order experience - **Product Quality** (1-5 stars) - Product condition, specifications, and performance - **Service Rating** (1-5 stars) - Technical support, communication, and professionalism - **Delivery Rating** (1-5 stars) - Timeliness, packaging, and delivery experience  **Business Rules:** - Only orders with status `delivered` or `completed` can be rated - Each order can only be rated once (no duplicate ratings) - Ratings contribute to product and service improvement metrics - Customer feedback is visible to other customers (with approval) - Negative ratings trigger customer service follow-up  **Feedback Usage:** - Product ratings influence search ranking and recommendations - Service feedback helps identify training opportunities - Delivery ratings improve logistics partner performance - Detailed comments help resolve systemic issues  **Customer Benefits:** - Contribution to community knowledge base - Influence on product selection and pricing - Priority support for future orders (high-rating customers) - Exclusive access to new product previews 

        :param id: **Order ID (MongoDB ObjectId)** - Must be a delivered/completed order - Order must belong to authenticated customer - Order must not have been rated previously  (required)
        :type id: str
        :param add_rating_request: (required)
        :type add_rating_request: AddRatingRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._add_rating_serialize(
            id=id,
            add_rating_request=add_rating_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "AddRating200Response",
            '400': "AddRating400Response",
            '404': "CompareProducts400Response",
            '401': "AddRating401Response",
            '500': "GetOrders500Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def add_rating_with_http_info(
        self,
        id: Annotated[str, Field(strict=True, description="**Order ID (MongoDB ObjectId)** - Must be a delivered/completed order - Order must belong to authenticated customer - Order must not have been rated previously ")],
        add_rating_request: AddRatingRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[AddRating200Response]:
        """Rate and review completed order

        **Customer Feedback and Rating System**  Enable customers to provide comprehensive feedback on their completed orders, helping improve service quality and assist future customers.  **Rating Categories:** - **Overall Rating** (1-5 stars) - General satisfaction with entire order experience - **Product Quality** (1-5 stars) - Product condition, specifications, and performance - **Service Rating** (1-5 stars) - Technical support, communication, and professionalism - **Delivery Rating** (1-5 stars) - Timeliness, packaging, and delivery experience  **Business Rules:** - Only orders with status `delivered` or `completed` can be rated - Each order can only be rated once (no duplicate ratings) - Ratings contribute to product and service improvement metrics - Customer feedback is visible to other customers (with approval) - Negative ratings trigger customer service follow-up  **Feedback Usage:** - Product ratings influence search ranking and recommendations - Service feedback helps identify training opportunities - Delivery ratings improve logistics partner performance - Detailed comments help resolve systemic issues  **Customer Benefits:** - Contribution to community knowledge base - Influence on product selection and pricing - Priority support for future orders (high-rating customers) - Exclusive access to new product previews 

        :param id: **Order ID (MongoDB ObjectId)** - Must be a delivered/completed order - Order must belong to authenticated customer - Order must not have been rated previously  (required)
        :type id: str
        :param add_rating_request: (required)
        :type add_rating_request: AddRatingRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._add_rating_serialize(
            id=id,
            add_rating_request=add_rating_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "AddRating200Response",
            '400': "AddRating400Response",
            '404': "CompareProducts400Response",
            '401': "AddRating401Response",
            '500': "GetOrders500Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def add_rating_without_preload_content(
        self,
        id: Annotated[str, Field(strict=True, description="**Order ID (MongoDB ObjectId)** - Must be a delivered/completed order - Order must belong to authenticated customer - Order must not have been rated previously ")],
        add_rating_request: AddRatingRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Rate and review completed order

        **Customer Feedback and Rating System**  Enable customers to provide comprehensive feedback on their completed orders, helping improve service quality and assist future customers.  **Rating Categories:** - **Overall Rating** (1-5 stars) - General satisfaction with entire order experience - **Product Quality** (1-5 stars) - Product condition, specifications, and performance - **Service Rating** (1-5 stars) - Technical support, communication, and professionalism - **Delivery Rating** (1-5 stars) - Timeliness, packaging, and delivery experience  **Business Rules:** - Only orders with status `delivered` or `completed` can be rated - Each order can only be rated once (no duplicate ratings) - Ratings contribute to product and service improvement metrics - Customer feedback is visible to other customers (with approval) - Negative ratings trigger customer service follow-up  **Feedback Usage:** - Product ratings influence search ranking and recommendations - Service feedback helps identify training opportunities - Delivery ratings improve logistics partner performance - Detailed comments help resolve systemic issues  **Customer Benefits:** - Contribution to community knowledge base - Influence on product selection and pricing - Priority support for future orders (high-rating customers) - Exclusive access to new product previews 

        :param id: **Order ID (MongoDB ObjectId)** - Must be a delivered/completed order - Order must belong to authenticated customer - Order must not have been rated previously  (required)
        :type id: str
        :param add_rating_request: (required)
        :type add_rating_request: AddRatingRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._add_rating_serialize(
            id=id,
            add_rating_request=add_rating_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "AddRating200Response",
            '400': "AddRating400Response",
            '404': "CompareProducts400Response",
            '401': "AddRating401Response",
            '500': "GetOrders500Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _add_rating_serialize(
        self,
        id,
        add_rating_request,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> Tuple:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, str] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if add_rating_request is not None:
            _body_params = add_rating_request


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'bearerAuth'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/customer/order/{id}/rating',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def cancel_order(
        self,
        id: Annotated[str, Field(strict=True, description="**Order ID (MongoDB ObjectId)** - Must be a valid 24-character hexadecimal string - Order must belong to authenticated customer - Order must be in cancellable status ")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> CancelOrder200Response:
        """Cancel Product Order

        **Order Cancellation Workflow**  Allow customers to cancel their orders with appropriate business rules and automatic refund processing.  **Cancellation Rules:** - Only orders in `submitted` or `confirmed` status can be cancelled - Orders in `processing` or later stages cannot be cancelled (contact support) - Paid orders trigger automatic refund processing - Inventory reservations are immediately released  **Business Process:** 1. **Validation** - Check order ownership and cancellation eligibility 2. **Status Update** - Change order status to `cancelled` 3. **Inventory Release** - Return reserved stock to available inventory 4. **Refund Processing** - Initiate refund if payment was completed 5. **Notifications** - Notify customer and admin team of cancellation 6. **Audit Trail** - Log cancellation reason and timestamp  **Refund Timeline:** - Credit card: 3-5 business days - Bank transfer: 1-2 business days - Google Pay: Instant to 24 hours  **Support Contact:** For orders that cannot be self-cancelled, customers should contact support with their order number. 

        :param id: **Order ID (MongoDB ObjectId)** - Must be a valid 24-character hexadecimal string - Order must belong to authenticated customer - Order must be in cancellable status  (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._cancel_order_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CancelOrder200Response",
            '400': "CancelOrder400Response",
            '404': "CompareProducts400Response",
            '401': "CancelOrder401Response",
            '500': "GetOrders500Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def cancel_order_with_http_info(
        self,
        id: Annotated[str, Field(strict=True, description="**Order ID (MongoDB ObjectId)** - Must be a valid 24-character hexadecimal string - Order must belong to authenticated customer - Order must be in cancellable status ")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[CancelOrder200Response]:
        """Cancel Product Order

        **Order Cancellation Workflow**  Allow customers to cancel their orders with appropriate business rules and automatic refund processing.  **Cancellation Rules:** - Only orders in `submitted` or `confirmed` status can be cancelled - Orders in `processing` or later stages cannot be cancelled (contact support) - Paid orders trigger automatic refund processing - Inventory reservations are immediately released  **Business Process:** 1. **Validation** - Check order ownership and cancellation eligibility 2. **Status Update** - Change order status to `cancelled` 3. **Inventory Release** - Return reserved stock to available inventory 4. **Refund Processing** - Initiate refund if payment was completed 5. **Notifications** - Notify customer and admin team of cancellation 6. **Audit Trail** - Log cancellation reason and timestamp  **Refund Timeline:** - Credit card: 3-5 business days - Bank transfer: 1-2 business days - Google Pay: Instant to 24 hours  **Support Contact:** For orders that cannot be self-cancelled, customers should contact support with their order number. 

        :param id: **Order ID (MongoDB ObjectId)** - Must be a valid 24-character hexadecimal string - Order must belong to authenticated customer - Order must be in cancellable status  (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._cancel_order_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CancelOrder200Response",
            '400': "CancelOrder400Response",
            '404': "CompareProducts400Response",
            '401': "CancelOrder401Response",
            '500': "GetOrders500Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def cancel_order_without_preload_content(
        self,
        id: Annotated[str, Field(strict=True, description="**Order ID (MongoDB ObjectId)** - Must be a valid 24-character hexadecimal string - Order must belong to authenticated customer - Order must be in cancellable status ")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Cancel Product Order

        **Order Cancellation Workflow**  Allow customers to cancel their orders with appropriate business rules and automatic refund processing.  **Cancellation Rules:** - Only orders in `submitted` or `confirmed` status can be cancelled - Orders in `processing` or later stages cannot be cancelled (contact support) - Paid orders trigger automatic refund processing - Inventory reservations are immediately released  **Business Process:** 1. **Validation** - Check order ownership and cancellation eligibility 2. **Status Update** - Change order status to `cancelled` 3. **Inventory Release** - Return reserved stock to available inventory 4. **Refund Processing** - Initiate refund if payment was completed 5. **Notifications** - Notify customer and admin team of cancellation 6. **Audit Trail** - Log cancellation reason and timestamp  **Refund Timeline:** - Credit card: 3-5 business days - Bank transfer: 1-2 business days - Google Pay: Instant to 24 hours  **Support Contact:** For orders that cannot be self-cancelled, customers should contact support with their order number. 

        :param id: **Order ID (MongoDB ObjectId)** - Must be a valid 24-character hexadecimal string - Order must belong to authenticated customer - Order must be in cancellable status  (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._cancel_order_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CancelOrder200Response",
            '400': "CancelOrder400Response",
            '404': "CompareProducts400Response",
            '401': "CancelOrder401Response",
            '500': "GetOrders500Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _cancel_order_serialize(
        self,
        id,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> Tuple:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, str] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'bearerAuth'
        ]

        return self.api_client.param_serialize(
            method='DELETE',
            resource_path='/customer/order/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def create_order(
        self,
        create_order_request: CreateOrderRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> CreateOrder201Response:
        """Create new product order

        **Yellow Sapphire Order Creation Workflow**  This endpoint transforms cart items into a formal product order that enters the fulfillment pipeline:  **Prerequisites:** - Customer must be authenticated - Cart must contain at least one item - All cart products must be available in stock  **Business Process (Transaction-Safe):** 1. **Cart Validation** - Verifies all items are still available and in stock 2. **MongoDB Transaction Start** - ACID-compliant transaction begins 3. **Order Creation** - Generates unique order number (YS-TIMESTAMP-XXX format) 4. **Inventory Update** - Atomically reduces product stock levels 5. **Cart Clearance** - Customer's cart is emptied 6. **Transaction Commit** - All changes committed atomically or rolled back on failure 7. **Admin Notification** - Technical fulfillment team receives immediate notification 8. **Customer Confirmation** - Order confirmation sent via email/SMS  **Transaction Features:** - **ACID Compliance**: All database changes are atomic - either all succeed or all are rolled back - **Automatic Retry**: Up to 3 retry attempts with exponential backoff for transient failures - **Correlation Tracking**: Complete request tracing through transaction logs - **Rollback Guarantee**: Inventory is automatically restored if any step fails  **Next Steps After Order Creation:** - Technical staff will prepare and configure products - Order status progresses: submitted → confirmed → processing → ready → shipped → delivered - Customer receives status updates at each major milestone - In-person delivery for Johannesburg/Pretoria (with photo + signature) - Courier delivery elsewhere (with tracking number) 

        :param create_order_request: (required)
        :type create_order_request: CreateOrderRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._create_order_serialize(
            create_order_request=create_order_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '201': "CreateOrder201Response",
            '400': "CreateOrder400Response",
            '401': "CreateOrder401Response",
            '500': "CreateOrder500Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def create_order_with_http_info(
        self,
        create_order_request: CreateOrderRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[CreateOrder201Response]:
        """Create new product order

        **Yellow Sapphire Order Creation Workflow**  This endpoint transforms cart items into a formal product order that enters the fulfillment pipeline:  **Prerequisites:** - Customer must be authenticated - Cart must contain at least one item - All cart products must be available in stock  **Business Process (Transaction-Safe):** 1. **Cart Validation** - Verifies all items are still available and in stock 2. **MongoDB Transaction Start** - ACID-compliant transaction begins 3. **Order Creation** - Generates unique order number (YS-TIMESTAMP-XXX format) 4. **Inventory Update** - Atomically reduces product stock levels 5. **Cart Clearance** - Customer's cart is emptied 6. **Transaction Commit** - All changes committed atomically or rolled back on failure 7. **Admin Notification** - Technical fulfillment team receives immediate notification 8. **Customer Confirmation** - Order confirmation sent via email/SMS  **Transaction Features:** - **ACID Compliance**: All database changes are atomic - either all succeed or all are rolled back - **Automatic Retry**: Up to 3 retry attempts with exponential backoff for transient failures - **Correlation Tracking**: Complete request tracing through transaction logs - **Rollback Guarantee**: Inventory is automatically restored if any step fails  **Next Steps After Order Creation:** - Technical staff will prepare and configure products - Order status progresses: submitted → confirmed → processing → ready → shipped → delivered - Customer receives status updates at each major milestone - In-person delivery for Johannesburg/Pretoria (with photo + signature) - Courier delivery elsewhere (with tracking number) 

        :param create_order_request: (required)
        :type create_order_request: CreateOrderRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._create_order_serialize(
            create_order_request=create_order_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '201': "CreateOrder201Response",
            '400': "CreateOrder400Response",
            '401': "CreateOrder401Response",
            '500': "CreateOrder500Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def create_order_without_preload_content(
        self,
        create_order_request: CreateOrderRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Create new product order

        **Yellow Sapphire Order Creation Workflow**  This endpoint transforms cart items into a formal product order that enters the fulfillment pipeline:  **Prerequisites:** - Customer must be authenticated - Cart must contain at least one item - All cart products must be available in stock  **Business Process (Transaction-Safe):** 1. **Cart Validation** - Verifies all items are still available and in stock 2. **MongoDB Transaction Start** - ACID-compliant transaction begins 3. **Order Creation** - Generates unique order number (YS-TIMESTAMP-XXX format) 4. **Inventory Update** - Atomically reduces product stock levels 5. **Cart Clearance** - Customer's cart is emptied 6. **Transaction Commit** - All changes committed atomically or rolled back on failure 7. **Admin Notification** - Technical fulfillment team receives immediate notification 8. **Customer Confirmation** - Order confirmation sent via email/SMS  **Transaction Features:** - **ACID Compliance**: All database changes are atomic - either all succeed or all are rolled back - **Automatic Retry**: Up to 3 retry attempts with exponential backoff for transient failures - **Correlation Tracking**: Complete request tracing through transaction logs - **Rollback Guarantee**: Inventory is automatically restored if any step fails  **Next Steps After Order Creation:** - Technical staff will prepare and configure products - Order status progresses: submitted → confirmed → processing → ready → shipped → delivered - Customer receives status updates at each major milestone - In-person delivery for Johannesburg/Pretoria (with photo + signature) - Courier delivery elsewhere (with tracking number) 

        :param create_order_request: (required)
        :type create_order_request: CreateOrderRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._create_order_serialize(
            create_order_request=create_order_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '201': "CreateOrder201Response",
            '400': "CreateOrder400Response",
            '401': "CreateOrder401Response",
            '500': "CreateOrder500Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _create_order_serialize(
        self,
        create_order_request,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> Tuple:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, str] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if create_order_request is not None:
            _body_params = create_order_request


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'bearerAuth'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/customer/create-order',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def get_orderby_id(
        self,
        id: Annotated[str, Field(strict=True, description="**Order ID (MongoDB ObjectId)** - 24-character hexadecimal string - Unique identifier for the order - Obtained from order creation or order list endpoints  **Note:** This is different from the human-readable order number (YS-XXXX-XXX) ")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> GetOrderbyId200Response:
        """Get detailed order information

        **Comprehensive Order Details and Tracking**  Retrieve complete order information including product details, status history, tracking information, and delivery updates.  **Business Context:** - Real-time order status and progress tracking - Complete product information with images and specifications - Delivery tracking integration with courier services - Payment status and transaction details - Technical fulfillment notes (where applicable) - Customer communication history  **Security:** - Customers can only access their own orders - Order ownership validation enforced - Sensitive fulfillment details filtered for customer view  **Use Cases:** - Order status checking - Delivery tracking - Invoice/receipt generation - Product warranty information - Support ticket creation context 

        :param id: **Order ID (MongoDB ObjectId)** - 24-character hexadecimal string - Unique identifier for the order - Obtained from order creation or order list endpoints  **Note:** This is different from the human-readable order number (YS-XXXX-XXX)  (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_orderby_id_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "GetOrderbyId200Response",
            '404': "CompareProducts400Response",
            '401': "GetOrderbyId401Response",
            '500': "GetOrders500Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def get_orderby_id_with_http_info(
        self,
        id: Annotated[str, Field(strict=True, description="**Order ID (MongoDB ObjectId)** - 24-character hexadecimal string - Unique identifier for the order - Obtained from order creation or order list endpoints  **Note:** This is different from the human-readable order number (YS-XXXX-XXX) ")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[GetOrderbyId200Response]:
        """Get detailed order information

        **Comprehensive Order Details and Tracking**  Retrieve complete order information including product details, status history, tracking information, and delivery updates.  **Business Context:** - Real-time order status and progress tracking - Complete product information with images and specifications - Delivery tracking integration with courier services - Payment status and transaction details - Technical fulfillment notes (where applicable) - Customer communication history  **Security:** - Customers can only access their own orders - Order ownership validation enforced - Sensitive fulfillment details filtered for customer view  **Use Cases:** - Order status checking - Delivery tracking - Invoice/receipt generation - Product warranty information - Support ticket creation context 

        :param id: **Order ID (MongoDB ObjectId)** - 24-character hexadecimal string - Unique identifier for the order - Obtained from order creation or order list endpoints  **Note:** This is different from the human-readable order number (YS-XXXX-XXX)  (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_orderby_id_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "GetOrderbyId200Response",
            '404': "CompareProducts400Response",
            '401': "GetOrderbyId401Response",
            '500': "GetOrders500Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def get_orderby_id_without_preload_content(
        self,
        id: Annotated[str, Field(strict=True, description="**Order ID (MongoDB ObjectId)** - 24-character hexadecimal string - Unique identifier for the order - Obtained from order creation or order list endpoints  **Note:** This is different from the human-readable order number (YS-XXXX-XXX) ")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Get detailed order information

        **Comprehensive Order Details and Tracking**  Retrieve complete order information including product details, status history, tracking information, and delivery updates.  **Business Context:** - Real-time order status and progress tracking - Complete product information with images and specifications - Delivery tracking integration with courier services - Payment status and transaction details - Technical fulfillment notes (where applicable) - Customer communication history  **Security:** - Customers can only access their own orders - Order ownership validation enforced - Sensitive fulfillment details filtered for customer view  **Use Cases:** - Order status checking - Delivery tracking - Invoice/receipt generation - Product warranty information - Support ticket creation context 

        :param id: **Order ID (MongoDB ObjectId)** - 24-character hexadecimal string - Unique identifier for the order - Obtained from order creation or order list endpoints  **Note:** This is different from the human-readable order number (YS-XXXX-XXX)  (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_orderby_id_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "GetOrderbyId200Response",
            '404': "CompareProducts400Response",
            '401': "GetOrderbyId401Response",
            '500': "GetOrders500Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_orderby_id_serialize(
        self,
        id,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> Tuple:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, str] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'bearerAuth'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/customer/order/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def get_orders(
        self,
        page: Annotated[Optional[Annotated[int, Field(strict=True, ge=1)]], Field(description="Page number for pagination (1-based)")] = None,
        limit: Annotated[Optional[Annotated[int, Field(le=50, strict=True, ge=1)]], Field(description="Number of orders per page (max 50)")] = None,
        status: Annotated[Optional[StrictStr], Field(description="**Filter by order status:** - `submitted` - New orders awaiting confirmation - `confirmed` - Payment verified, in queue - `processing` - Technical team working on order - `ready` - Products prepared, awaiting dispatch - `shipped` - Order dispatched to customer - `delivered` - Successfully delivered - `completed` - Order closed with feedback - `cancelled` - Order cancelled ")] = None,
        date_from: Annotated[Optional[date], Field(description="Filter orders from date (YYYY-MM-DD)")] = None,
        date_to: Annotated[Optional[date], Field(description="Filter orders to date (YYYY-MM-DD)")] = None,
        search: Annotated[Optional[Annotated[str, Field(min_length=3, strict=True)]], Field(description="Search by order number or product name")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> GetOrders200Response:
        """Get customer order history

        **Customer Order History and Tracking**  Retrieve complete order history for the authenticated customer with comprehensive filtering and status tracking.  **Business Context:** - Shows complete order lifecycle from submission to delivery - Real-time status updates from fulfillment team - Tracking integration for shipped orders - Financial summary and payment status  **Order Status Workflow:** 1. `submitted` - Order placed, awaiting admin confirmation 2. `confirmed` - Payment verified, technical team notified 3. `processing` - Products being prepared and configured 4. `ready` - Technical work complete, ready for dispatch 5. `shipped` - Handed to courier or ready for pickup 6. `delivered` - Customer received Order 7. `completed` - Order fully closed with customer feedback 8. `cancelled` - Order cancelled (refund processed if paid)  - Pagination for large order histories - Status filtering for order management - Product details with images - Delivery tracking integration - Payment status visibility 

        :param page: Page number for pagination (1-based)
        :type page: int
        :param limit: Number of orders per page (max 50)
        :type limit: int
        :param status: **Filter by order status:** - `submitted` - New orders awaiting confirmation - `confirmed` - Payment verified, in queue - `processing` - Technical team working on order - `ready` - Products prepared, awaiting dispatch - `shipped` - Order dispatched to customer - `delivered` - Successfully delivered - `completed` - Order closed with feedback - `cancelled` - Order cancelled 
        :type status: str
        :param date_from: Filter orders from date (YYYY-MM-DD)
        :type date_from: date
        :param date_to: Filter orders to date (YYYY-MM-DD)
        :type date_to: date
        :param search: Search by order number or product name
        :type search: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_orders_serialize(
            page=page,
            limit=limit,
            status=status,
            date_from=date_from,
            date_to=date_to,
            search=search,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "GetOrders200Response",
            '404': "GetOrders404Response",
            '401': "GetOrders401Response",
            '500': "GetOrders500Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def get_orders_with_http_info(
        self,
        page: Annotated[Optional[Annotated[int, Field(strict=True, ge=1)]], Field(description="Page number for pagination (1-based)")] = None,
        limit: Annotated[Optional[Annotated[int, Field(le=50, strict=True, ge=1)]], Field(description="Number of orders per page (max 50)")] = None,
        status: Annotated[Optional[StrictStr], Field(description="**Filter by order status:** - `submitted` - New orders awaiting confirmation - `confirmed` - Payment verified, in queue - `processing` - Technical team working on order - `ready` - Products prepared, awaiting dispatch - `shipped` - Order dispatched to customer - `delivered` - Successfully delivered - `completed` - Order closed with feedback - `cancelled` - Order cancelled ")] = None,
        date_from: Annotated[Optional[date], Field(description="Filter orders from date (YYYY-MM-DD)")] = None,
        date_to: Annotated[Optional[date], Field(description="Filter orders to date (YYYY-MM-DD)")] = None,
        search: Annotated[Optional[Annotated[str, Field(min_length=3, strict=True)]], Field(description="Search by order number or product name")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[GetOrders200Response]:
        """Get customer order history

        **Customer Order History and Tracking**  Retrieve complete order history for the authenticated customer with comprehensive filtering and status tracking.  **Business Context:** - Shows complete order lifecycle from submission to delivery - Real-time status updates from fulfillment team - Tracking integration for shipped orders - Financial summary and payment status  **Order Status Workflow:** 1. `submitted` - Order placed, awaiting admin confirmation 2. `confirmed` - Payment verified, technical team notified 3. `processing` - Products being prepared and configured 4. `ready` - Technical work complete, ready for dispatch 5. `shipped` - Handed to courier or ready for pickup 6. `delivered` - Customer received Order 7. `completed` - Order fully closed with customer feedback 8. `cancelled` - Order cancelled (refund processed if paid)  - Pagination for large order histories - Status filtering for order management - Product details with images - Delivery tracking integration - Payment status visibility 

        :param page: Page number for pagination (1-based)
        :type page: int
        :param limit: Number of orders per page (max 50)
        :type limit: int
        :param status: **Filter by order status:** - `submitted` - New orders awaiting confirmation - `confirmed` - Payment verified, in queue - `processing` - Technical team working on order - `ready` - Products prepared, awaiting dispatch - `shipped` - Order dispatched to customer - `delivered` - Successfully delivered - `completed` - Order closed with feedback - `cancelled` - Order cancelled 
        :type status: str
        :param date_from: Filter orders from date (YYYY-MM-DD)
        :type date_from: date
        :param date_to: Filter orders to date (YYYY-MM-DD)
        :type date_to: date
        :param search: Search by order number or product name
        :type search: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_orders_serialize(
            page=page,
            limit=limit,
            status=status,
            date_from=date_from,
            date_to=date_to,
            search=search,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "GetOrders200Response",
            '404': "GetOrders404Response",
            '401': "GetOrders401Response",
            '500': "GetOrders500Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def get_orders_without_preload_content(
        self,
        page: Annotated[Optional[Annotated[int, Field(strict=True, ge=1)]], Field(description="Page number for pagination (1-based)")] = None,
        limit: Annotated[Optional[Annotated[int, Field(le=50, strict=True, ge=1)]], Field(description="Number of orders per page (max 50)")] = None,
        status: Annotated[Optional[StrictStr], Field(description="**Filter by order status:** - `submitted` - New orders awaiting confirmation - `confirmed` - Payment verified, in queue - `processing` - Technical team working on order - `ready` - Products prepared, awaiting dispatch - `shipped` - Order dispatched to customer - `delivered` - Successfully delivered - `completed` - Order closed with feedback - `cancelled` - Order cancelled ")] = None,
        date_from: Annotated[Optional[date], Field(description="Filter orders from date (YYYY-MM-DD)")] = None,
        date_to: Annotated[Optional[date], Field(description="Filter orders to date (YYYY-MM-DD)")] = None,
        search: Annotated[Optional[Annotated[str, Field(min_length=3, strict=True)]], Field(description="Search by order number or product name")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Get customer order history

        **Customer Order History and Tracking**  Retrieve complete order history for the authenticated customer with comprehensive filtering and status tracking.  **Business Context:** - Shows complete order lifecycle from submission to delivery - Real-time status updates from fulfillment team - Tracking integration for shipped orders - Financial summary and payment status  **Order Status Workflow:** 1. `submitted` - Order placed, awaiting admin confirmation 2. `confirmed` - Payment verified, technical team notified 3. `processing` - Products being prepared and configured 4. `ready` - Technical work complete, ready for dispatch 5. `shipped` - Handed to courier or ready for pickup 6. `delivered` - Customer received Order 7. `completed` - Order fully closed with customer feedback 8. `cancelled` - Order cancelled (refund processed if paid)  - Pagination for large order histories - Status filtering for order management - Product details with images - Delivery tracking integration - Payment status visibility 

        :param page: Page number for pagination (1-based)
        :type page: int
        :param limit: Number of orders per page (max 50)
        :type limit: int
        :param status: **Filter by order status:** - `submitted` - New orders awaiting confirmation - `confirmed` - Payment verified, in queue - `processing` - Technical team working on order - `ready` - Products prepared, awaiting dispatch - `shipped` - Order dispatched to customer - `delivered` - Successfully delivered - `completed` - Order closed with feedback - `cancelled` - Order cancelled 
        :type status: str
        :param date_from: Filter orders from date (YYYY-MM-DD)
        :type date_from: date
        :param date_to: Filter orders to date (YYYY-MM-DD)
        :type date_to: date
        :param search: Search by order number or product name
        :type search: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_orders_serialize(
            page=page,
            limit=limit,
            status=status,
            date_from=date_from,
            date_to=date_to,
            search=search,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "GetOrders200Response",
            '404': "GetOrders404Response",
            '401': "GetOrders401Response",
            '500': "GetOrders500Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_orders_serialize(
        self,
        page,
        limit,
        status,
        date_from,
        date_to,
        search,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> Tuple:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, str] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        if page is not None:
            
            _query_params.append(('page', page))
            
        if limit is not None:
            
            _query_params.append(('limit', limit))
            
        if status is not None:
            
            _query_params.append(('status', status))
            
        if date_from is not None:
            if isinstance(date_from, date):
                _query_params.append(
                    (
                        'dateFrom',
                        date_from.strftime(
                            self.api_client.configuration.date_format
                        )
                    )
                )
            else:
                _query_params.append(('dateFrom', date_from))
            
        if date_to is not None:
            if isinstance(date_to, date):
                _query_params.append(
                    (
                        'dateTo',
                        date_to.strftime(
                            self.api_client.configuration.date_format
                        )
                    )
                )
            else:
                _query_params.append(('dateTo', date_to))
            
        if search is not None:
            
            _query_params.append(('search', search))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'bearerAuth'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/customer/orders',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def make_payment(
        self,
        make_payment_request: MakePaymentRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> MakePayment200Response:
        """Process secure payment for order

        **Secure Payment Processing System**  Process payments for Yellow Sapphire product orders using multiple secure payment methods with comprehensive fraud protection and transaction tracking.  **Supported Payment Methods:** - **Credit/Debit Cards** - Visa, Mastercard, American Express (via Paystack) - **Google Pay** - Seamless mobile payment experience - **Bank Transfer** - Direct EFT for corporate customers - **Purchase Order** - Net 30-day terms for approved business customers  **Security ** - PCI DSS --> How do we do this? Dont store anything? - 3DSS - Fraud detection and prevention - Encrypted payment data transmission (we already use ssl) - Transaction logging and audit trails  **Payment Workflow:** 1. **Order Validation** - Verify order exists and is payable 2. **Payment Method Processing** - Secure payment gateway integration 3. **Fraud Screening** - Real-time fraud detection checks 4. **Transaction Completion** - Payment confirmation and receipt generation 5. **Order Status Update** - Automatic progression to confirmed status 6. **Inventory Reservation** - Stock allocation for paid orders 7. **Fulfillment Notification** - Technical team receives paid order alert  **Business Rules:** - Orders must be in `submitted` status to accept payment - Payment amount must match order total exactly - Failed payments allow 3 retry attempts before order expires - Successful payments trigger immediate order confirmation - Corporate customers can request invoice payment (we need to test and implennt this thing and the pdf quote gen and emailing) 

        :param make_payment_request: (required)
        :type make_payment_request: MakePaymentRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._make_payment_serialize(
            make_payment_request=make_payment_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "MakePayment200Response",
            '400': "MakePayment400Response",
            '404': "CompareProducts400Response",
            '401': "MakePayment401Response",
            '500': "MakePayment500Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def make_payment_with_http_info(
        self,
        make_payment_request: MakePaymentRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[MakePayment200Response]:
        """Process secure payment for order

        **Secure Payment Processing System**  Process payments for Yellow Sapphire product orders using multiple secure payment methods with comprehensive fraud protection and transaction tracking.  **Supported Payment Methods:** - **Credit/Debit Cards** - Visa, Mastercard, American Express (via Paystack) - **Google Pay** - Seamless mobile payment experience - **Bank Transfer** - Direct EFT for corporate customers - **Purchase Order** - Net 30-day terms for approved business customers  **Security ** - PCI DSS --> How do we do this? Dont store anything? - 3DSS - Fraud detection and prevention - Encrypted payment data transmission (we already use ssl) - Transaction logging and audit trails  **Payment Workflow:** 1. **Order Validation** - Verify order exists and is payable 2. **Payment Method Processing** - Secure payment gateway integration 3. **Fraud Screening** - Real-time fraud detection checks 4. **Transaction Completion** - Payment confirmation and receipt generation 5. **Order Status Update** - Automatic progression to confirmed status 6. **Inventory Reservation** - Stock allocation for paid orders 7. **Fulfillment Notification** - Technical team receives paid order alert  **Business Rules:** - Orders must be in `submitted` status to accept payment - Payment amount must match order total exactly - Failed payments allow 3 retry attempts before order expires - Successful payments trigger immediate order confirmation - Corporate customers can request invoice payment (we need to test and implennt this thing and the pdf quote gen and emailing) 

        :param make_payment_request: (required)
        :type make_payment_request: MakePaymentRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._make_payment_serialize(
            make_payment_request=make_payment_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "MakePayment200Response",
            '400': "MakePayment400Response",
            '404': "CompareProducts400Response",
            '401': "MakePayment401Response",
            '500': "MakePayment500Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def make_payment_without_preload_content(
        self,
        make_payment_request: MakePaymentRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Process secure payment for order

        **Secure Payment Processing System**  Process payments for Yellow Sapphire product orders using multiple secure payment methods with comprehensive fraud protection and transaction tracking.  **Supported Payment Methods:** - **Credit/Debit Cards** - Visa, Mastercard, American Express (via Paystack) - **Google Pay** - Seamless mobile payment experience - **Bank Transfer** - Direct EFT for corporate customers - **Purchase Order** - Net 30-day terms for approved business customers  **Security ** - PCI DSS --> How do we do this? Dont store anything? - 3DSS - Fraud detection and prevention - Encrypted payment data transmission (we already use ssl) - Transaction logging and audit trails  **Payment Workflow:** 1. **Order Validation** - Verify order exists and is payable 2. **Payment Method Processing** - Secure payment gateway integration 3. **Fraud Screening** - Real-time fraud detection checks 4. **Transaction Completion** - Payment confirmation and receipt generation 5. **Order Status Update** - Automatic progression to confirmed status 6. **Inventory Reservation** - Stock allocation for paid orders 7. **Fulfillment Notification** - Technical team receives paid order alert  **Business Rules:** - Orders must be in `submitted` status to accept payment - Payment amount must match order total exactly - Failed payments allow 3 retry attempts before order expires - Successful payments trigger immediate order confirmation - Corporate customers can request invoice payment (we need to test and implennt this thing and the pdf quote gen and emailing) 

        :param make_payment_request: (required)
        :type make_payment_request: MakePaymentRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._make_payment_serialize(
            make_payment_request=make_payment_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "MakePayment200Response",
            '400': "MakePayment400Response",
            '404': "CompareProducts400Response",
            '401': "MakePayment401Response",
            '500': "MakePayment500Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _make_payment_serialize(
        self,
        make_payment_request,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> Tuple:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, str] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if make_payment_request is not None:
            _body_params = make_payment_request


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'bearerAuth'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/customer/payment',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )


