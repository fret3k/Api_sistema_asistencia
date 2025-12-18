from dotenv import load_dotenv
load_dotenv()  # Cargar variables de entorno desde .env

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from controllers.personal_controller import router as PersonalRouter
from controllers.asistencias_controller import router as asistencia_router
from controllers.encoding_face_controller import router as EncodigFaceRouter
from fastapi.middleware.cors import CORSMiddleware
from docs.api_info import API_TITLE, API_DESCRIPTION, API_VERSION, API_CONTACT
from controllers.horario_controller import router as HorariosRouter
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ocultar logs de httpx (URLs de Supabase)
logging.getLogger("httpx").setLevel(logging.WARNING)


app = FastAPI(
    # refencia a la documentacion de la api
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    contact=API_CONTACT
)


# Handler global para errores de validación - muestra detalles del error
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({
            "campo": field,
            "mensaje": error["msg"],
            "tipo_error": error["type"]
        })
    
    logger.error(f"Error de validación en {request.url}: {errors}")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Error de validación en los datos enviados",
            "errores": errors
        }
    )

# Lista de orígenes permitidos
origins = [
    "http://localhost:5174",      # Vite dev server
    "http://localhost:3000",      # Create React App (por si acaso)
    "http://127.0.0.1:5174",
    "http://localhost:5173",
    "https://app-sismt-asisten-f.vercel.app/",      # Alternativa localhost
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

app.include_router(HorariosRouter)
@app.get("/")
def root():
    return {"message": "API funcionando correctamente"}
