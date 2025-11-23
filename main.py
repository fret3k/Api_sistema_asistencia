from fastapi import FastAPI
from controllers.personal_controller import router as PersonalRouter
from controllers.asistencias_controller import router as asistencia_router

app = FastAPI(title="API - Sistema de Asistencia con Reconocimiento Facial")

app.include_router(PersonalRouter)
app.include_router(asistencia_router)

@app.get("/")
def root():
    return {"message": "API funcionando correctamente"}
