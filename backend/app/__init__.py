"""
GDPR Tool Application Package

This package contains the main application components for the GDPR compliance tool.
It provides a comprehensive system for data masking, file processing, and GDPR compliance.

Key Components:
- main.py: FastAPI application entry point and configuration
- services.py: Core business logic and data processing services
- settings.py: Application configuration and environment variables
- storage.py: File storage and archive management
- logger.py: Structured logging system
- api/: API endpoints and middleware
- gdpr/: GDPR-specific processing components
- database/: Database models and session management

The application provides a RESTful API for GDPR data masking operations with support for:
- User authentication and authorization
- File upload, processing, and download
- Product-based preset selection and rule application
- Data masking with multiple matcher types
- Archive processing with recursive extraction
- Comprehensive logging and error handling
"""
