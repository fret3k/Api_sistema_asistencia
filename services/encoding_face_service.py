from uuid import UUID
from repository.encoding_face_repository import EncodingFaceRepository
from dto.codificacion_facial_dto.endodig_face_request_dto import EncodingFaceCreateDTO

class EncodingFaceService:

    @staticmethod
    async def create(data: EncodingFaceCreateDTO):
        # mode='json' convierte UUID a string automáticamente
        payload = data.model_dump(mode='json')
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
