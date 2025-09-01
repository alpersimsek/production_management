"""
GDPR Tool API Routers - Router Module Exports

This module exports all API router classes for the GDPR compliance tool.
It provides a centralized import point for all router components.

Exported Routers:
- FilesRouter: File management and processing endpoints
- UserRouter: User authentication and management endpoints
- MaskingMapRouter: Data masking map management endpoints
- PresetsRouter: Preset and rule management endpoints
- ProductsRouter: Product management endpoints
- RulesRouter: Rule configuration and management endpoints

Each router is a FastAPI APIRouter instance that provides RESTful endpoints
for specific functionality in the GDPR compliance tool.
"""

from api.routers.files import FilesRouter
from api.routers.users import UserRouter
from api.routers.masking import MaskingMapRouter
from api.routers.presets import PresetsRouter
from api.routers.products import ProductsRouter
from api.routers.rules import RulesRouter
