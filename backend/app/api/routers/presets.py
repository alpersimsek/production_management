from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from api.schemas import (
    PresetResponse,
    PresetCreate,
    PresetUpdate,
    PresetRuleResponse,
    PresetRuleCreate,
    PresetRuleUpdate,
    RuleResponse,
)
from services import PresetService, RuleService, PresetRuleService
from database.models import Role
from typing import List


class PresetsRouter(APIRouter):
    def __init__(self):
        super().__init__()

        # Preset Routes
        self.get("/presets", response_model=List[PresetResponse])(self.get_presets)
        self.get("/presets/{preset_id}", response_model=PresetResponse)(self.get_preset)
        self.post("/presets", response_model=PresetResponse)(self.create_preset)
        self.put("/presets/{preset_id}", response_model=PresetResponse)(
            self.update_preset
        )
        self.delete("/presets/{preset_id}")(self.delete_preset)

        # Preset Rule Routes
        self.get("/presets/{preset_id}/rules", response_model=List[PresetRuleResponse])(
            self.get_preset_rules
        )
        self.post("/preset-rules", response_model=PresetRuleResponse)(
            self.create_preset_rule
        )
        self.put(
            "/preset-rules/{preset_id}/{rule_id}", response_model=PresetRuleResponse
        )(self.update_preset_rule)
        self.delete("/preset-rules/{preset_id}/{rule_id}")(self.delete_preset_rule)

    # Preset Endpoints
    def get_presets(self, req: Request):
        """Get all presets."""
        preset_service = PresetService(req.state.db)
        try:
            presets = preset_service.get_all()
            return [PresetResponse.model_validate(preset) for preset in presets]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    def get_preset(self, preset_id: int, req: Request):
        """Get a specific preset by ID."""
        preset_service = PresetService(req.state.db)
        try:
            preset = preset_service.get_by_id(preset_id)
            if not preset:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found"
                )
            return PresetResponse.model_validate(preset)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    def create_preset(self, preset_data: PresetCreate, req: Request):
        """Create a new preset."""
        # Check admin role
        if not req.state.user or req.state.user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
            )

        preset_service = PresetService(req.state.db)
        try:
            # Check if product exists
            from services import ProductService

            product_service = ProductService(req.state.db)
            product = product_service.get_by_id(preset_data.product_id)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
                )

            # Create preset
            from database.models import Preset

            preset = Preset(
                name=preset_data.name,
                product_id=preset_data.product_id,
                header=preset_data.header,
            )
            preset = preset_service.create(preset)
            return PresetResponse.model_validate(preset)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    def update_preset(self, preset_id: int, preset_data: PresetUpdate, req: Request):
        """Update an existing preset."""
        # Check admin role
        if not req.state.user or req.state.user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
            )

        preset_service = PresetService(req.state.db)
        try:
            # Check if preset exists
            preset = preset_service.get_by_id(preset_id)
            if not preset:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found"
                )

            # Update fields if provided
            update_data = preset_data.model_dump(exclude_unset=True)
            if not update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields to update provided",
                )

            # If product_id is provided, verify it exists
            if "product_id" in update_data:
                from services import ProductService

                product_service = ProductService(req.state.db)
                product = product_service.get_by_id(update_data["product_id"])
                if not product:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Product not found",
                    )

            # Update preset
            preset = preset_service.update(preset, update_data)
            return PresetResponse.model_validate(preset)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    def delete_preset(self, preset_id: int, req: Request):
        """Delete a preset."""
        # Check admin role
        if not req.state.user or req.state.user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
            )

        preset_service = PresetService(req.state.db)
        try:
            # Check if preset exists
            preset = preset_service.get_by_id(preset_id)
            if not preset:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found"
                )

            # Check if preset is in use
            if hasattr(preset, "files") and preset.files:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete preset that is in use by files",
                )

            # Delete preset (this will cascade delete preset rules)
            preset_service.delete(preset_id)
            return JSONResponse({"detail": "Preset deleted successfully"})
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    # Preset Rule Endpoints
    def get_preset_rules(self, preset_id: int, req: Request):
        """Get all rules for a specific preset."""
        preset_service = PresetService(req.state.db)
        try:
            # Check if preset exists
            preset = preset_service.get_by_id(preset_id)
            if not preset:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found"
                )

            # Return preset rules
            preset_rules = preset.rules
            return [PresetRuleResponse.model_validate(rule) for rule in preset_rules]
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    def create_preset_rule(self, rule_data: PresetRuleCreate, req: Request):
        """Create a new preset rule association."""
        # Check admin role
        if not req.state.user or req.state.user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
            )
        print('CREATE RULE')
        preset_rule_service = PresetRuleService(req.state.db)
        try:
            # Check if preset exists
            preset_service = PresetService(req.state.db)
            preset = preset_service.get_by_id(rule_data.preset_id)
            if not preset:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found"
                )

            # Check if rule exists
            rule_service = RuleService(req.state.db)
            rule = rule_service.get_by_id(rule_data.rule_id)
            if not rule:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found"
                )

            # Check if association already exists
            existing_rules = [
                pr for pr in preset.rules if pr.rule_id == rule_data.rule_id
            ]
            if existing_rules:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Rule is already associated with this preset",
                )

            # Create preset rule
            from database.models import PresetRule

            preset_rule = PresetRule(
                preset_id=rule_data.preset_id,
                rule_id=rule_data.rule_id,
                action=rule_data.action,
            )
            preset_rule = preset_rule_service.create(preset_rule)

            # Set rule info in response
            response = PresetRuleResponse.model_validate(preset_rule)
            response.rule = RuleResponse.model_validate(rule)
            return response
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    def update_preset_rule(
        self, preset_id: int, rule_id: int, rule_data: PresetRuleUpdate, req: Request
    ):
        """Update an existing preset rule association."""
        # Check admin role
        if not req.state.user or req.state.user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
            )
            
        print(rule_id)
        print(rule_data)

        preset_rule_service = PresetRuleService(req.state.db)
        try:
            # Find the preset rule
            preset_service = PresetService(req.state.db)
            preset = preset_service.get_by_id(preset_id)
            if not preset:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found"
                )

            # Find the specific preset rule
            preset_rule = None
            for pr in preset.rules:
                if pr.rule_id == rule_id:
                    preset_rule = pr
                    break

            if not preset_rule:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Rule is not associated with this preset",
                )

            # Update the action
            update_data = {"action": rule_data.action}
            preset_rule = preset_rule_service.update(preset_rule, update_data)

            # Set rule info in response
            rule_service = RuleService(req.state.db)
            rule = rule_service.get_by_id(rule_id)

            response = PresetRuleResponse.model_validate(preset_rule)
            response.rule = RuleResponse.model_validate(rule)
            return response
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    def delete_preset_rule(self, preset_id: int, rule_id: int, req: Request):
        """Delete a preset rule association."""
        # Check admin role
        if not req.state.user or req.state.user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
            )

        preset_service = PresetService(req.state.db)
        try:
            # Check if preset exists
            preset = preset_service.get_by_id(preset_id)
            if not preset:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found"
                )

            # Find the specific preset rule
            preset_rule = None
            for pr in preset.rules:
                if pr.rule_id == rule_id:
                    preset_rule = pr
                    break

            if not preset_rule:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Rule is not associated with this preset",
                )

            # Delete the preset rule
            # We need to construct a composite key for deletion
            from sqlalchemy import delete
            from database.models import PresetRule

            stmt = delete(PresetRule).where(
                PresetRule.preset_id == preset_id, PresetRule.rule_id == rule_id
            )
            req.state.db.execute(stmt)
            req.state.db.commit()

            return JSONResponse({"detail": "Rule removed from preset successfully"})
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )
