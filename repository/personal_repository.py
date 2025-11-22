from config.supabaseClient import get_supabase
from uuid import UUID
from dto.personal_dto.personal_request_dto import PersonalCreateDTO

class PersonalRepository:

    table = "personal"

    @staticmethod
    async def create(data: PersonalCreateDTO):
        supabase = get_supabase()
        result = supabase.table(PersonalRepository.table).insert(data.dict()).execute()
        return result.data[0] if result.data else None

    @staticmethod
    async def find_all():
        supabase = get_supabase()
        result = supabase.table(PersonalRepository.table).select("*").execute()
        return result.data

    @staticmethod
    async def find_by_id(personal_id: UUID):
        supabase = get_supabase()
        result = supabase.table(PersonalRepository.table).select("*").eq("id", str(personal_id)).execute()
        return result.data[0] if result.data else None

    @staticmethod
    async def delete(personal_id: UUID):
        supabase = get_supabase()
        result = supabase.table(PersonalRepository.table).delete().eq("id", str(personal_id)).execute()
        return result.data
