from uuid import UUID
from repository.personal_repository import PersonalRepository
from dto.personal_dto.personal_request_dto import PersonalCreateDTO

class PersonalService:

    @staticmethod
    async def create(data: PersonalCreateDTO):
        return await PersonalRepository.create(data)

    @staticmethod
    async def list_all():
        return await PersonalRepository.find_all()

    @staticmethod
    async def get_by_id(personal_id: UUID):
        result = await PersonalRepository.find_by_id(personal_id)
        if not result:
            raise Exception("El personal no existe")
        return result

    @staticmethod
    async def delete(personal_id: UUID):
        return await PersonalRepository.delete(personal_id)
