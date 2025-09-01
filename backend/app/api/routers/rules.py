"""
GDPR Tool Rules Router - Rule Management API Endpoints

This module provides REST API endpoints for managing data masking rules in the GDPR compliance tool.
It handles rule creation, configuration, and management with comprehensive validation and admin controls.

Key Endpoints:
- GET /rules: Retrieve all rules with pagination, sorting, and filtering
- GET /rules/{rule_id}: Get specific rule details
- POST /rules: Create new rules with configuration validation
- PUT /rules/{rule_id}: Update rule configuration
- DELETE /rules/{rule_id}: Delete rules (with usage validation)

Rule Features:
- Rule Types: Support for regex, IP address, and MAC address matchers
- Category Management: Organize rules by data categories (IP, email, phone, etc.)
- Configuration Validation: Comprehensive validation of rule configurations
- Usage Tracking: Prevent deletion of rules in use by presets
- Pagination: Efficient handling of large rule sets

Rule Categories:
- ipv4_addr: IPv4 address patterns
- username: User name and identifier patterns
- phone_num: Phone number patterns
- domain: Domain name and URL patterns
- email: Email address patterns
- mac_addr: MAC address patterns
- And other GDPR-relevant data types

Security Features:
- Admin Access Control: All modification operations require admin privileges
- Input Validation: Comprehensive validation of rule data and configurations
- Usage Validation: Prevent deletion of rules with active associations
- Error Handling: Detailed error responses with proper HTTP status codes

The router integrates with RuleService for business logic and provides
a comprehensive rule management system for GDPR data masking workflows.
"""

from fastapi import APIRouter, HTTPException, Request, status, Query
from fastapi.responses import JSONResponse
from api.schemas import RuleResponse, RuleCreate, RuleUpdate
from services import RuleService
from database.models import Role, Rule, RuleCategory
from typing import List, Dict, Any
from sqlalchemy import or_

class RulesRouter(APIRouter):
    def __init__(self):
        super().__init__()

        # Rule Routes
        self.get("/rules", response_model=Dict[str, Any])(self.get_rules)
        self.get("/rules/{rule_id}", response_model=RuleResponse)(self.get_rule)
        self.post("/rules", response_model=RuleResponse)(self.create_rule)
        self.put("/rules/{rule_id}", response_model=RuleResponse)(self.update_rule)
        self.delete("/rules/{rule_id}")(self.delete_rule)

    def get_rules(self, req: Request, limit: int = Query(10, ge=1, le=100), offset: int = Query(0, ge=0),
                  sort: str = Query('name:asc'), category: str = Query(None)):
        """Get all rules with pagination, sorting, and filtering."""
        rule_service = RuleService(req.state.db)
        try:
            # Validate sort
            sort_field, sort_dir = sort.split(':') if ':' in sort else (sort, 'asc')
            if sort_field not in ['name', 'category'] or sort_dir not in ['asc', 'desc']:
                sort_field, sort_dir = 'name', 'asc'

            # Build query
            query = rule_service.session.query(Rule)
            if category:
                try:
                    query = query.filter(Rule.category == RuleCategory(category))
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid category. Must be one of: {', '.join([c.value for c in RuleCategory])}",
                    )

            # Apply sorting
            sort_column = getattr(Rule, sort_field)
            query = query.order_by(sort_column.asc() if sort_dir == 'asc' else sort_column.desc())

            # Get total count
            total = query.count()

            # Apply pagination
            rules = query.limit(limit).offset(offset).all()

            return {
                'data': [RuleResponse.model_validate(rule) for rule in rules],
                'total': total,
                'limit': limit,
                'offset': offset
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch rules: {str(e)}"
            )

    def get_rule(self, rule_id: int, req: Request):
        """Get a specific rule by ID."""
        rule_service = RuleService(req.state.db)
        try:
            rule = rule_service.get_by_id(rule_id)
            if not rule:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found"
                )
            return RuleResponse.model_validate(rule)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch rule: {str(e)}"
            )

    def create_rule(self, rule_data: RuleCreate, req: Request):
        """Create a new rule."""
        if not req.state.user or req.state.user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
            )

        rule_service = RuleService(req.state.db)
        try:
            try:
                category = RuleCategory(rule_data.category)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid category. Must be one of: {', '.join([c.value for c in RuleCategory])}",
                )

            # Validate config
            if rule_data.config.get('type') == 'regex' and not rule_data.config.get('pattern'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Pattern is required for regex rules"
                )

            rule = Rule(name=rule_data.name, category=category, config=rule_data.config)
            rule = rule_service.create(rule)
            return RuleResponse.model_validate(rule)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create rule: {str(e)}"
            )

    def update_rule(self, rule_id: int, rule_data: RuleUpdate, req: Request):
        """Update an existing rule."""
        if not req.state.user or req.state.user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
            )

        rule_service = RuleService(req.state.db)
        try:
            rule = rule_service.get_by_id(rule_id)
            if not rule:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found"
                )

            update_data = rule_data.model_dump(exclude_unset=True)
            if not update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update provided"
                )

            if "category" in update_data:
                try:
                    update_data["category"] = RuleCategory(update_data["category"])
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid category. Must be one of: {', '.join([c.value for c in RuleCategory])}",
                    )

            if "config" in update_data and update_data["config"].get('type') == 'regex':
                if not update_data["config"].get('pattern'):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, detail="Pattern is required for regex rules"
                    )

            rule = rule_service.update(rule, update_data)
            return RuleResponse.model_validate(rule)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update rule: {str(e)}"
            )

    def delete_rule(self, rule_id: int, req: Request):
        """Delete a rule."""
        if not req.state.user or req.state.user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
            )

        rule_service = RuleService(req.state.db)
        try:
            rule = rule_service.get_by_id(rule_id)
            if not rule:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found"
                )

            if hasattr(rule, "presets") and rule.presets:
                preset_names = [preset.preset.name for preset in rule.presets]
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot delete rule '{rule.name}' as it is used by presets: {', '.join(preset_names)}"
                )

            rule_service.delete(rule_id)
            return JSONResponse({"detail": "Rule deleted successfully"})
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete rule: {str(e)}"
            )