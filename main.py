from fastapi import FastAPI
from controllers.personal_controller import router as PersonalRouter
from controllers.asistencias_controller import router as asistencia_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API - Sistema de Asistencia con Reconocimiento Facial")


# Lista de orígenes permitidos
origins = [
    "http://localhost:5173",      # Vite dev server
    "http://localhost:3000",      # Create React App (por si acaso)
    "http://127.0.0.1:5173",      # Alternativa localhost
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         # Orígenes permitidos
    allow_credentials=True,        # Permite cookies y headers de autenticación
    allow_methods=["*"],           # Permite GET, POST, PUT, DELETE, OPTIONS, etc.
    allow_headers=["*"],           # Permite todos los headers (Authorization, Content-Type, etc.)
)


app.include_router(PersonalRouter)
app.include_router(asistencia_router)

@app.get("/")
def root():
    return {"message": "API funcionando correctamente"}
