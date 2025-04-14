from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse
from api.schemas import RuleResponse, RuleCreate, RuleUpdate
from services import RuleService
from database.models import Role, Rule, RuleCategory
from typing import List, Dict, Any


class RulesRouter(APIRouter):
    def __init__(self):
        super().__init__()

        # Rule Routes
        self.get("/rules", response_model=List[RuleResponse])(self.get_rules)
        self.get("/rules/{rule_id}", response_model=RuleResponse)(self.get_rule)
        self.post("/rules", response_model=RuleResponse)(self.create_rule)
        self.put("/rules/{rule_id}", response_model=RuleResponse)(self.update_rule)
        self.delete("/rules/{rule_id}")(self.delete_rule)

    def get_rules(self, req: Request):
        """Get all rules."""
        rule_service = RuleService(req.state.db)
        try:
            rules = rule_service.get_all()
            return [RuleResponse.model_validate(rule) for rule in rules]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
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
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    def create_rule(self, rule_data: RuleCreate, req: Request):
        """Create a new rule."""
        # Check admin role
        if not req.state.user or req.state.user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
            )

        rule_service = RuleService(req.state.db)
        try:
            # Validate category
            try:
                category = RuleCategory(rule_data.category)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid category. Must be one of: {', '.join([c.value for c in RuleCategory])}",
                )

            # Create rule
            rule = Rule(name=rule_data.name, category=category, config=rule_data.config)
            rule = rule_service.create(rule)
            return RuleResponse.model_validate(rule)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    def update_rule(self, rule_id: int, rule_data: RuleUpdate, req: Request):
        """Update an existing rule."""
        # Check admin role
        if not req.state.user or req.state.user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
            )

        rule_service = RuleService(req.state.db)
        try:
            # Check if rule exists
            rule = rule_service.get_by_id(rule_id)
            if not rule:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found"
                )

            # Update fields if provided
            update_data = rule_data.model_dump(exclude_unset=True)
            if not update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields to update provided",
                )

            # If category is provided, validate it
            if "category" in update_data:
                try:
                    update_data["category"] = RuleCategory(update_data["category"])
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid category. Must be one of: {', '.join([c.value for c in RuleCategory])}",
                    )

            # Update rule
            rule = rule_service.update(rule, update_data)
            return RuleResponse.model_validate(rule)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    def delete_rule(self, rule_id: int, req: Request):
        """Delete a rule."""
        # Check admin role
        if not req.state.user or req.state.user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
            )

        rule_service = RuleService(req.state.db)
        try:
            # Check if rule exists
            rule = rule_service.get_by_id(rule_id)
            if not rule:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found"
                )

            # Check if rule is in use
            if hasattr(rule, "presets") and rule.presets:
                preset_names = [preset.preset.name for preset in rule.presets]
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot delete rule that is in use by presets: {', '.join(preset_names)}",
                )

            # Delete rule
            rule_service.delete(rule_id)
            return JSONResponse({"detail": "Rule deleted successfully"})
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )
