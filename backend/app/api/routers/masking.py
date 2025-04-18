from fastapi import APIRouter, Query, Response, Request, HTTPException, status
from typing import List, Optional
from services import MaskingMapService
from database.models import RuleCategory
from api.schemas import MaskingMapResponse
from io import StringIO
import csv
from logger import logger


class MaskingMapRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix = "/masking"

        # Register routes
        self.get(
            "/categories",
            response_model=List[str],
            summary="Get masking categories",
            description="Get all available masking categories",
        )(self.get_masking_categories)

        self.get(
            "/search",
            response_model=List[MaskingMapResponse],
            summary="Search masking maps",
            description="Search for masking maps based on query and filters",
        )(self.search_masking_maps)

        self.get(
            "/export",
            response_class=Response,
            summary="Export masking maps",
            description="Export masking maps to CSV format",
        )(self.export_masking_maps)

    def search_masking_maps(
        self,
        req: Request,
        query: Optional[str] = None,
        categories: Optional[List[str]] = Query(None),
        limit: Optional[int] = 100,
        offset: Optional[int] = 0,
        sort: Optional[str] = "created_at:desc",
    ) -> List[MaskingMapResponse]:
        """Search for masking maps based on query and filters."""
        try:
            # Get user and session from request state (set by middleware)
            user = req.state.user
            session = req.state.db

            service = MaskingMapService(session)

            # Validate sort parameter
            if sort:
                parts = sort.split(":")
                if len(parts) != 2 or parts[1].lower() not in ["asc", "desc"]:
                    sort = "created_at:desc"  # Default to created_at desc if invalid

            # Execute search
            results = service.search_masks(
                query=query,
                categories=categories,
                limit=limit,
                offset=offset,
                sort=sort,
            )

            # Convert to response schema
            return [MaskingMapResponse.model_validate(item) for item in results]
        except Exception as e:
            logger.error(f"Error searching masking maps: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to search masking maps",
            )

    def get_masking_categories(
        self,
        req: Request,
    ) -> List[str]:
        """Get all available masking categories."""
        try:
            # Get user and session from request state (set by middleware)
            user = req.state.user
            session = req.state.db

            service = MaskingMapService(session)
            categories = service.get_categories()

            # If no categories found, return all possible categories from the enum
            if not categories:
                categories = [cat.value for cat in RuleCategory]

            return categories
        except Exception as e:
            logger.error(f"Error fetching masking categories: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch masking categories",
            )

    def export_masking_maps(
        self,
        req: Request,
        query: Optional[str] = None,
        categories: Optional[List[str]] = Query(None),
        sort: Optional[str] = "created_at:desc",
    ) -> Response:
        """Export masking maps to CSV format."""
        try:
            # Get user and session from request state (set by middleware)
            user = req.state.user
            session = req.state.db

            service = MaskingMapService(session)

            # Get all results (no pagination for export)
            results = service.search_masks(
                query=query,
                categories=categories,
                limit=10000,  # Set a high limit
                offset=0,
                sort=sort,
            )

            # Create CSV content
            output = StringIO()
            writer = csv.writer(output)

            # Write header
            writer.writerow(["TYPE", "ORIGINAL VALUE", "MASKED VALUE", "CREATED AT"])

            # Write data rows
            for item in results:
                writer.writerow(
                    [
                        item.category.value,
                        item.original_value,
                        item.masked_value,
                        str(item.created_at),
                    ]
                )

            # Prepare the response
            response = Response(content=output.getvalue(), media_type="text/csv")
            response.headers["Content-Disposition"] = (
                f"attachment; filename=masking_maps.csv"
            )

            return response
        except Exception as e:
            logger.error(f"Error exporting masking maps: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to export masking maps",
            )
