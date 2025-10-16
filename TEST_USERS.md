# Olgahan Kimya ERP - Test Users

This document contains test user credentials for different roles and departments to facilitate comprehensive testing of the ERP system.

## 🔐 Test User Credentials

### Admin Users
| Name | Email | Role | Department | Status | Password |
|------|-------|------|------------|--------|----------|
| Ahmet Yılmaz | ahmet@olgahan.com | Admin | Üretim | Active | admin123 |

### Manager Users
| Name | Email | Role | Department | Status | Password |
|------|-------|------|------------|--------|----------|
| Fatma Özkan | fatma@olgahan.com | Manager | Üretim | Active | manager123 |
| Ayşe Demir | ayse@olgahan.com | Manager | Depo | Inactive | manager123 |
| Elif Korkmaz | elif@olgahan.com | Manager | Paketleme | Active | manager123 |
| Selin Aktaş | selin@olgahan.com | Manager | Sevkiyat | Active | manager123 |
| Gülay Yılmaz | gulay@olgahan.com | Manager | Plasiyer | Active | manager123 |

### Operator Users
| Name | Email | Role | Department | Status | Password |
|------|-------|------|------------|--------|----------|
| Mehmet Kaya | mehmet@olgahan.com | Operator | Paketleme | Active | operator123 |
| Ali Çelik | ali@olgahan.com | Operator | Üretim | Active | operator123 |
| Zeynep Arslan | zeynep@olgahan.com | Operator | Depo | Active | operator123 |
| Mustafa Yıldız | mustafa@olgahan.com | Operator | Sevkiyat | Active | operator123 |
| Hasan Güneş | hasan@olgahan.com | Operator | Plasiyer | Inactive | operator123 |
| Burak Şahin | burak@olgahan.com | Operator | Üretim | Active | operator123 |

## 🏢 Department Distribution

### Üretim (Production)
- **Admin**: Ahmet Yılmaz
- **Manager**: Fatma Özkan
- **Operators**: Ali Çelik, Burak Şahin

### Paketleme (Packaging)
- **Manager**: Elif Korkmaz
- **Operator**: Mehmet Kaya

### Depo (Warehouse)
- **Manager**: Ayşe Demir (Inactive)
- **Operator**: Zeynep Arslan

### Sevkiyat (Shipments)
- **Manager**: Selin Aktaş
- **Operator**: Mustafa Yıldız

### Plasiyer (Sales Representative)
- **Manager**: Gülay Yılmaz
- **Operator**: Hasan Güneş (Inactive)

## 🔑 Role Permissions

### Admin Role
- **Full System Access**: All permissions
- **User Management**: Create, edit, delete users
- **System Settings**: Configure system parameters
- **All Modules**: Complete access to all ERP modules

### Manager Role
- **View Reports**: Access to analytics and reports
- **Manage Orders**: Create, edit, approve orders
- **View Analytics**: Access to production and sales analytics
- **Department Management**: Manage department-specific operations
- **Limited User Management**: View users in their department

### Operator Role
- **Production Jobs**: Create and manage production jobs
- **Quality Control**: Perform quality checks and inspections
- **Inventory Updates**: Update inventory levels and locations
- **Basic Operations**: Access to operational modules only
- **No Administrative Access**: Cannot access user management or system settings

## 🧪 Testing Scenarios

### 1. Authentication Testing
- Test login with different role credentials
- Verify role-based access restrictions
- Test inactive user login attempts

### 2. Role-Based Access Control (RBAC)
- **Admin**: Should have access to all modules and settings
- **Manager**: Should have access to management functions but not system settings
- **Operator**: Should have limited access to operational modules only

### 3. Department-Specific Testing
- Test department-specific data visibility
- Verify cross-department access restrictions
- Test department manager permissions

### 4. User Management Testing
- **Admin**: Can create, edit, and delete users
- **Manager**: Can view users in their department
- **Operator**: Cannot access user management

### 5. Module Access Testing
- **Orders**: All roles can access (different permission levels)
- **Production Jobs**: All roles can access
- **Analytics**: Manager and Admin only
- **Settings**: Admin only
- **User Management**: Admin only

## 📊 User Statistics
- **Total Users**: 12
- **Active Users**: 10
- **Inactive Users**: 2
- **Admin Users**: 1
- **Manager Users**: 5
- **Operator Users**: 6

## 🔄 Last Login Information
- **Most Recent**: Selin Aktaş (2024-01-20T12:10:00Z)
- **Oldest Active**: Zeynep Arslan (2024-01-20T07:30:00Z)
- **Inactive Users**: Ayşe Demir, Hasan Güneş

## 🚀 Quick Test Setup

1. **Start the application**: `npm run serve`
2. **Access login page**: `http://localhost:3003/login`
3. **Use any test credentials** from the table above
4. **Test different roles** to verify RBAC functionality
5. **Check Settings page** to view all users and their details

## 📝 Notes
- All passwords are simple for testing purposes
- In production, implement strong password policies
- Consider implementing two-factor authentication
- Regular password rotation should be enforced
- User sessions should have appropriate timeout settings

## 🔧 Backend Integration
When integrating with the backend API, ensure:
- User authentication endpoints are properly configured
- Role-based permissions are enforced at the API level
- JWT tokens include role and department information
- Session management is properly implemented
- Password hashing is secure (bcrypt recommended)

