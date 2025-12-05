from fastapi import FastAPI
from controllers.personal_controller import router as PersonalRouter
from controllers.asistencias_controller import router as asistencia_router
from controllers.encoding_face_controller import router as EncodigFaceRouter
from fastapi.middleware.cors import CORSMiddleware
from docs.api_info import API_TITLE, API_DESCRIPTION, API_VERSION, API_CONTACT

app = FastAPI(
    # refencia a la documentacion de la api
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    contact=API_CONTACT
)

# Lista de orígenes permitidos
origins = [
    "http://localhost:5174",      # Vite dev server
    "http://localhost:3000",      # Create React App (por si acaso)
    "http://127.0.0.1:5174",
    "http://localhost:5173",      # Alternativa localhost
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
app.include_router(EncodigFaceRouter)
@app.get("/")
def root():
    return {"message": "API funcionando correctamente"}
