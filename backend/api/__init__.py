from .upload import router as upload_router
from .extraction import router as extraction_router
from .assignment import router as assignment_router
from .calculation import router as calculation_router

__all__ = ["upload_router", "extraction_router", "assignment_router", "calculation_router"]
