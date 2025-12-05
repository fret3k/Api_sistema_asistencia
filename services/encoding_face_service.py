from uuid import UUID
from repository.encoding_face_repository import EncodingFaceRepository
from dto.codificacion_facial_dto.endodig_face_request_dto import EncodingFaceCreateDTO
from repository.personal_repository import PersonalRepository

class EncodingFaceService:

    @staticmethod
    async def create(data: EncodingFaceCreateDTO):
        """
        Crea una nueva codificación facial con validaciones.
        """
        # Validar que el embedding tenga exactamente 128 valores
        if not data.embedding:
            raise ValueError("El embedding no puede estar vacío")
        
        if len(data.embedding) != 128:
            raise ValueError(f"El embedding debe tener exactamente 128 valores, se recibieron {len(data.embedding)}")
        
        # Validar que todos los valores sean números
        if not all(isinstance(x, (int, float)) for x in data.embedding):
            raise ValueError("Todos los valores del embedding deben ser números")
        
        # Validar que el personal_id existe
        personal = await PersonalRepository.find_by_id(data.personal_id)
        if not personal:
            raise ValueError(f"El personal con ID {data.personal_id} no existe")
        
        # Convertir UUID a string para Supabase
        payload = data.model_dump()
        if isinstance(payload.get("personal_id"), UUID):
            payload["personal_id"] = str(payload["personal_id"])
        
        # Asegurar que embedding sea una lista de floats
        if payload.get("embedding"):
            payload["embedding"] = [float(x) for x in payload["embedding"]]
        
        return await EncodingFaceRepository.create(payload)

    @staticmethod
    async def list_all():
        return await EncodingFaceRepository.find_all()

    @staticmethod
    async def get_by_id(id: UUID):
        result = await EncodingFaceRepository.find_by_id(id)
        if not result:
            raise Exception("Codificación facial no encontrada")
        return result

    @staticmethod
    async def find_by_personal(personal_id: UUID):
        return await EncodingFaceRepository.find_by_personal_id(personal_id)

    @staticmethod
    async def delete(id: UUID):
        return await EncodingFaceRepository.delete(id)
