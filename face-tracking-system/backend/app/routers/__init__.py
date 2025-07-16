from importlib import import_module

# Re-export submodules so they can be imported via
# `from app.routers import streaming` etc.
streaming = import_module("app.routers.streaming")
embeddings = import_module("app.routers.embeddings")
employees = import_module("app.routers.employees")
attendance = import_module("app.routers.attendance")
auth = import_module("app.routers.auth")

# Additionally expose the `router` objects for convenient access
streaming_router = streaming.router
embeddings_router = embeddings.router
employees_router = employees.router
attendance_router = attendance.router
auth_router = auth.router

__all__ = [
    "streaming",
    "embeddings",
    "employees",
    "attendance",
    "auth",
    "streaming_router",
    "embeddings_router",
    "employees_router",
    "attendance_router",
    "auth_router",
]