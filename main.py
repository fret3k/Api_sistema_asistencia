from fastapi import FastAPI
from controllers.personal_controller import router as PersonalRouter

app = FastAPI(title="API - Sistema de Asistencia con Reconocimiento Facial")

app.include_router(PersonalRouter)

@app.get("/")
def root():
    return {"message": "API funcionando correctamente"}
