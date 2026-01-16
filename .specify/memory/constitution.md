# Todo Application Full-Stack Constitution

## Core Principles

### I. Full-Stack Integration
Frontend and backend must work seamlessly together with shared authentication mechanisms. All API requests must include proper JWT tokens for authentication. Cross-service communication follows RESTful principles with consistent error handling.

### II. Secure Authentication First
Better Auth integration with JWT tokens must be implemented from the start. Authentication state must be properly managed on both frontend and backend. All API endpoints require valid authentication tokens.

### III. Environment Consistency
Shared secrets (like BETTER_AUTH_SECRET) must be identical across frontend and backend environments. Configuration management follows the principle of least privilege with environment-specific values.

### IV. Type Safety Throughout
Full TypeScript support on frontend and Pydantic/SQLModel validation on backend. Type definitions must be consistent between frontend and backend API contracts.

### V. Conversational Interface Excellence
Natural language processing must be intuitive and robust. The AI chatbot should understand varied user expressions for todo operations. Error recovery and clarification prompts enhance user experience.

### VI. Secure Tool Execution
MCP tools must implement proper authorization checks. Agent access to backend functions requires authentication verification. Input sanitization prevents injection attacks through conversational interface.

### VII. API-First Development
Backend API endpoints are designed first with clear contracts. Frontend implementation follows API specifications with proper error handling and loading states.

## Security Requirements
All authentication flows must use HTTPS in production. JWT tokens have appropriate expiration times. Passwords are never stored in plain text. Input validation prevents injection attacks. Conversational inputs are sanitized and validated before processing.

## Development Workflow
Feature development follows Spec-Driven Development methodology. All changes must be documented in specifications before implementation. Code reviews verify compliance with architectural decisions.

## Governance
<!-- Example: Constitution supersedes all other practices; Amendments require documentation, approval, migration plan -->

This constitution governs all development decisions for the Todo Application. All PRs must verify compliance with these principles. Any architectural changes require updates to this constitution.

**Version**: 2.0.0 | **Ratified**: 2026-01-11 | **Last Amended**: 2026-01-11
<!-- Example: Version: 2.1.1 | Ratified: 2025-06-13 | Last Amended: 2025-07-16 -->
