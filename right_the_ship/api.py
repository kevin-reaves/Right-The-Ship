from ninja import NinjaAPI

from .core.api.user import router as user_router
from .core.api.task import router as task_router

api = NinjaAPI()

api.add_router("/users", user_router)
api.add_router("/tasks", task_router)
