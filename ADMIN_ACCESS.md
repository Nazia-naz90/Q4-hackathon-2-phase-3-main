# Admin User Management

This application includes role-based access control with admin functionality. Here's how to manage admin users:

## Setting up an Admin User

By default, all new users are created as regular users (`is_admin = False`). To promote a user to admin status, use the admin utility script.

### Using the Admin Utility Script

From the backend directory, you can use the admin utility to manage admin users:

```bash
# Promote a user to admin (using email or username)
python admin_utils.py promote --identifier user@example.com
python admin_utils.py promote --identifier username

# Demote an admin user back to regular user
python admin_utils.py demote --identifier user@example.com

# List all admin users
python admin_utils.py list
```

## Admin Access Control

### Frontend Protection
- The `/admin` route checks for admin privileges before allowing access
- Non-admin users attempting to access the admin dashboard will see an "Access Denied" message and be redirected to the home page
- The admin menu item only appears in the sidebar if the user has admin privileges

### Backend Protection
- The `/api/admin/stats` endpoint verifies that the requesting user has `is_admin = True`
- Requests from non-admin users return a 403 Forbidden response

## Features Available to Admins

- Access to the admin dashboard showing system-wide statistics
- View total users and tasks across the system
- View task distribution by priority and status
- View recent task activity trends

## Security Measures

- JWT tokens contain admin status information
- Both frontend and backend verify admin privileges
- Admin status is stored in localStorage for quick access but verified against the backend
- Session management follows security best practices