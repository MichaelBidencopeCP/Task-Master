from fastapi import FastAPI
from todo.api.v1.todos.simple_todo import router as simple_todo
from todo.api.healthcheck import router as healthcheck
from todo.api.auth.auth_endpoint import router as auth_router
from todo.settings import get_settings
def create_app():
    app = FastAPI()
    app.include_router(auth_router, prefix="/api", tags=["auth"])
    app.include_router(simple_todo, prefix="/api/v1", tags=["todos"])
    app.include_router(healthcheck, prefix="/api", tags=["healthcheck"])
    #healthcheck at / 
    @app.get("/")
    def health_check():
        return {"status": "ok"}
    @app.get("/testing123")
    def testing123():
        #return the jwt settings
        settings = get_settings()
        return {
            "jwt_secret": settings.jwt_secret,
            "jwt_alg": settings.jwt_alg,
            "jwt_exp_minutes": settings.jwt_exp_minutes
        }


    return app



app = create_app()