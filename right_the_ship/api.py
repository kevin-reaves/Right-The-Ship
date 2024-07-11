from ninja import NinjaAPI
from .core.api.user import router as user_router

api = NinjaAPI()

api.add_router("/users", user_router)