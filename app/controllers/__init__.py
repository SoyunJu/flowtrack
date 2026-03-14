from app.controllers.upload_controller import router as upload_router
from app.controllers.report_controller import router as report_router
from app.controllers.agent_controller import router as agent_router

__all__ = ["upload_router", "report_router", "agent_router"]
