# API Specification: Todo Application REST Endpoints

## 1. Overview
**Feature Name:** Todo Application REST API
**Version:** 1.0
**Author:** [Author Name]
**Date:** 2025-12-31
**Status:** Draft

### 1.1 Purpose
This document specifies the RESTful API endpoints for the Todo Application, including request/response formats, authentication requirements, and error handling.

### 1.2 API Base URL
- **Development:** `http://localhost:8000/api`
- **Production:** `https://your-domain.com/api`

### 1.3 Authentication
- All endpoints require JWT token in Authorization header
- Format: `Authorization: Bearer <jwt_token>`
- Unauthorized requests return 401 status code

## 2. Common Headers
- `Content-Type: application/json`
- `Authorization: Bearer <jwt_token>`

## 3. Common Error Responses
- `401 Unauthorized`: Invalid or missing JWT token
- `403 Forbidden`: User not authorized to access resource
- `404 Not Found`: Resource does not exist
- `422 Unprocessable Entity`: Validation error in request body
- `500 Internal Server Error`: Server-side error

## 4. API Endpoints

### 4.1 List All Tasks
- **Endpoint:** `GET /api/tasks`
- **Description:** Retrieve all tasks for the authenticated user
- **Authentication Required:** Yes
- **Authorization:** User can only access their own tasks

#### Request
- **Headers:**
  - `Authorization: Bearer <jwt_token>`
- **Parameters:** None
- **Body:** None

#### Response
- **Success Status:** `200 OK`
- **Response Body:**
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Sample task",
      "description": "Sample description",
      "completed": false,
      "user_id": "user-uuid",
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

#### Error Responses
- `401 Unauthorized`: Invalid or missing token
- `500 Internal Server Error`: Server error during retrieval

### 4.2 Create New Task
- **Endpoint:** `POST /api/tasks`
- **Description:** Create a new task for the authenticated user
- **Authentication Required:** Yes
- **Authorization:** User can only create tasks for themselves

#### Request
- **Headers:**
  - `Authorization: Bearer <jwt_token>`
- **Parameters:** None
- **Body:**
```json
{
  "title": "New task title",
  "description": "Task description (optional)",
  "completed": false
}
```

#### Response
- **Success Status:** `201 Created`
- **Response Body:**
```json
{
  "id": 1,
  "title": "New task title",
  "description": "Task description (optional)",
  "completed": false,
  "user_id": "user-uuid",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

#### Validation Rules
- `title` is required and must be 1-255 characters
- `description` is optional and max 1000 characters
- `completed` defaults to false if not provided

#### Error Responses
- `400 Bad Request`: Invalid request body format
- `401 Unauthorized`: Invalid or missing token
- `422 Unprocessable Entity`: Validation errors
- `500 Internal Server Error`: Server error during creation

### 4.3 Update Task Details
- **Endpoint:** `PUT /api/tasks/{id}`
- **Description:** Update all details of an existing task
- **Authentication Required:** Yes
- **Authorization:** User can only update their own tasks

#### Request
- **Headers:**
  - `Authorization: Bearer <jwt_token>`
- **Parameters:**
  - `id` (path): Task ID to update
- **Body:**
```json
{
  "title": "Updated task title",
  "description": "Updated description",
  "completed": true
}
```

#### Response
- **Success Status:** `200 OK`
- **Response Body:**
```json
{
  "id": 1,
  "title": "Updated task title",
  "description": "Updated description",
  "completed": true,
  "user_id": "user-uuid",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-02T00:00:00Z"
}
```

#### Validation Rules
- Task must exist and belong to the authenticated user
- `title` is required and must be 1-255 characters
- `description` is optional and max 1000 characters

#### Error Responses
- `400 Bad Request`: Invalid request body format
- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: Task does not belong to user
- `404 Not Found`: Task does not exist
- `422 Unprocessable Entity`: Validation errors
- `500 Internal Server Error`: Server error during update

### 4.4 Delete Task
- **Endpoint:** `DELETE /api/tasks/{id}`
- **Description:** Remove a task from the user's list
- **Authentication Required:** Yes
- **Authorization:** User can only delete their own tasks

#### Request
- **Headers:**
  - `Authorization: Bearer <jwt_token>`
- **Parameters:**
  - `id` (path): Task ID to delete
- **Body:** None

#### Response
- **Success Status:** `200 OK`
- **Response Body:**
```json
{
  "success": true,
  "message": "Task deleted successfully"
}
```

#### Error Responses
- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: Task does not belong to user
- `404 Not Found`: Task does not exist
- `500 Internal Server Error`: Server error during deletion

### 4.5 Toggle Task Completion
- **Endpoint:** `PATCH /api/tasks/{id}/complete`
- **Description:** Toggle the completion status of a task
- **Authentication Required:** Yes
- **Authorization:** User can only toggle their own tasks

#### Request
- **Headers:**
  - `Authorization: Bearer <jwt_token>`
- **Parameters:**
  - `id` (path): Task ID to toggle
- **Body:** None

#### Response
- **Success Status:** `200 OK`
- **Response Body:**
```json
{
  "id": 1,
  "title": "Task title",
  "description": "Task description",
  "completed": true,
  "user_id": "user-uuid",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-02T00:00:00Z"
}
```

#### Error Responses
- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: Task does not belong to user
- `404 Not Found`: Task does not exist
- `500 Internal Server Error`: Server error during toggle

## 5. Authentication and Authorization

### 5.1 JWT Token Verification
- All endpoints require valid JWT token in Authorization header
- Token must not be expired
- Token signature must be valid
- User ID must be extractable from token

### 5.2 User Authorization
- Each request verifies that the authenticated user owns the requested resource
- Database queries are scoped to the authenticated user's data
- Unauthorized access attempts return 403 Forbidden

### 5.3 Error Handling
- Authentication failures return 401 Unauthorized
- Authorization failures return 403 Forbidden
- Detailed error messages are logged but not exposed to clients

## 6. Data Validation

### 6.1 Input Validation
- All string inputs are validated for length and format
- Required fields are validated for presence
- Data types are validated before database operations

### 6.2 Response Validation
- All responses follow consistent JSON structure
- Timestamps are returned in ISO 8601 format
- Error responses follow consistent format

## 7. Performance Considerations

### 7.1 Query Optimization
- Use indexed fields for filtering and sorting
- Implement pagination for large result sets
- Cache frequently accessed data where appropriate

### 7.2 Rate Limiting
- Implement rate limiting to prevent abuse
- Consider per-user rate limits
- Return appropriate error codes for rate limit exceeded

## 8. Security Considerations

### 8.1 Data Protection
- All data transmission uses HTTPS
- Sensitive data is not exposed in responses
- Input validation prevents injection attacks

### 8.2 Authentication Security
- JWT tokens have appropriate expiration times
- Secure token storage and transmission
- Regular token refresh mechanism

## 9. Testing Requirements

### 9.1 Unit Tests
- Test individual endpoint functions
- Test authentication and authorization logic
- Test input validation

### 9.2 Integration Tests
- Test complete request/response cycles
- Test database interactions
- Test error handling

### 9.3 Security Tests
- Test unauthorized access attempts
- Test token validation
- Test data isolation between users