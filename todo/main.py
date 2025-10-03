from fastapi import FastAPI
from todo.api.v1.todos.simple_todo import router as simple_todo
from todo.api.healthcheck import router as healthcheck
from todo.api.auth.auth_endpoint import router as auth_router
def create_app():
    app = FastAPI()
    app.include_router(auth_router, prefix="/api", tags=["auth"])
    app.include_router(simple_todo, prefix="/api/v1", tags=["todos"])
    app.include_router(healthcheck, prefix="/api", tags=["healthcheck"])
    #healthcheck at / 
    @app.get("/")
    def health_check():
        return {"status": "ok"}

    return app



app = create_app()