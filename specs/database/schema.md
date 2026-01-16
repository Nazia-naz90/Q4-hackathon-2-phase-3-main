# Database Schema Specification: Todo Application

## 1. Overview
**Feature Name:** Todo Application Database Schema
**Version:** 1.0
**Author:** [Author Name]
**Date:** 2025-12-31
**Status:** Draft

### 1.1 Purpose
This document specifies the database schema for the Todo Application, including tables, relationships, indexes, and constraints.

### 1.2 Database System
- **Database Type:** PostgreSQL
- **Provider:** Neon Serverless
- **ORM:** SQLModel
- **Authentication:** Better Auth (manages users table)

## 2. Database Tables

### 2.1 Users Table (Managed by Better Auth)
**Table Name:** `users` (managed by Better Auth)

#### 2.1.1 Fields
- `id`: VARCHAR(255) - Primary key, unique identifier for the user
- `email`: VARCHAR(255) - Unique, not null, user's email address
- `name`: VARCHAR(255) - Nullable, user's display name
- `email_verified`: TIMESTAMP - Nullable, timestamp when email was verified
- `image`: TEXT - Nullable, URL to user's profile image
- `created_at`: TIMESTAMP - Not null, default: current timestamp
- `updated_at`: TIMESTAMP - Not null, default: current timestamp, auto-update

#### 2.1.2 Constraints
- Primary Key: `id`
- Unique Constraint: `email`
- Index: `email` (for efficient lookups)

#### 2.1.3 Notes
- This table is managed by Better Auth
- Custom fields can be added as needed
- Authentication-related fields are handled by Better Auth

### 2.2 Tasks Table
**Table Name:** `tasks`

#### 2.2.1 Fields
- `id`: INTEGER - Primary key, auto-increment
- `user_id`: VARCHAR(255) - Foreign key referencing users.id (from Better Auth)
- `title`: VARCHAR(255) - Not null, task title (1-255 characters)
- `description`: TEXT - Nullable, task description
- `completed`: BOOLEAN - Not null, default: false, completion status
- `created_at`: TIMESTAMP - Not null, default: current timestamp
- `updated_at`: TIMESTAMP - Not null, default: current timestamp, auto-update

#### 2.2.2 Constraints
- Primary Key: `id`
- Foreign Key: `user_id` references `users.id`
- Not Null Constraints: `user_id`, `title`, `completed`
- Check Constraint: `title` length between 1 and 255 characters

#### 2.2.3 Relationships
- One-to-Many: Users to Tasks (one user can have many tasks)
- Foreign Key: `tasks.user_id` → `users.id`

## 3. Indexes

### 3.1 Required Indexes
1. **Index on user_id** (`idx_tasks_user_id`)
   - Purpose: Efficient retrieval of tasks for a specific user
   - Fields: `user_id`
   - Type: B-tree

2. **Index on completed status** (`idx_tasks_completed`)
   - Purpose: Efficient filtering of completed vs incomplete tasks
   - Fields: `completed`
   - Type: B-tree

3. **Composite Index** (`idx_tasks_user_completed`)
   - Purpose: Efficient retrieval of tasks for a user with specific completion status
   - Fields: `user_id`, `completed`
   - Type: B-tree

### 3.2 Additional Indexes (Optional)
4. **Index on created_at** (`idx_tasks_created_at`)
   - Purpose: Efficient ordering by creation date
   - Fields: `created_at`
   - Type: B-tree

## 4. Database Constraints and Validation

### 4.1 Data Validation
- Task title must be 1-255 characters
- Task title cannot be empty or whitespace only
- User ID must reference an existing user in the users table
- Completed field defaults to false

### 4.2 Referential Integrity
- Foreign key constraint ensures tasks.user_id references valid users.id
- Cascading behavior: Define behavior when user is deleted (likely cascade delete tasks)

## 5. Sample SQL Schema

```sql
-- Users table is managed by Better Auth
-- The following represents the tasks table structure

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX idx_tasks_user_id ON tasks (user_id);
CREATE INDEX idx_tasks_completed ON tasks (completed);
CREATE INDEX idx_tasks_user_completed ON tasks (user_id, completed);
```

## 6. ORM Model Mapping (SQLModel)

### 6.1 Base Models
- Use SQLModel for type-safe database interactions
- Implement proper validation at the model level
- Use Pydantic validation for field constraints

### 6.2 Relationship Mapping
- Define relationship between User and Task models
- Implement proper foreign key relationships
- Handle cascading operations appropriately

## 7. Migration Strategy

### 7.1 Initial Migration
- Create tasks table with all required fields
- Add necessary indexes
- Set up foreign key constraints

### 7.2 Future Migrations
- Use Alembic for database schema migrations
- Maintain backward compatibility
- Test migrations on staging before production

## 8. Performance Considerations

### 8.1 Query Optimization
- Indexes on frequently queried fields (user_id, completed)
- Efficient pagination for large datasets
- Consider partial indexes for common query patterns

### 8.2 Scalability
- Serverless PostgreSQL handles scaling automatically
- Proper indexing ensures performance under load
- Consider partitioning if data volume grows significantly

## 9. Security Considerations

### 9.1 Data Access
- Ensure proper authentication before accessing tasks
- Implement user-specific data access controls
- Validate user_id matches authenticated user

### 9.2 Data Protection
- Encrypt sensitive data at rest if required
- Use parameterized queries to prevent SQL injection
- Implement proper input validation

## 10. Backup and Recovery

### 10.1 Backup Strategy
- Leverage Neon's built-in backup capabilities
- Regular automated backups
- Point-in-time recovery options

### 10.2 Recovery Procedures
- Document recovery procedures
- Test backup restoration periodically
- Ensure data consistency after recovery