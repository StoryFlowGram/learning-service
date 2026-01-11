from fastapi import Header, HTTPException



async def card_protocol():
    raise NotImplementedError("Должен быть переопределён в infa слое")


async def uow_dependencies():
    raise NotImplementedError("Должен быть переопределён в infa слое")

async def get_current_user(x_user_id: str = Header(None, alias="X-User-Id")) -> int:
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="X-User-Id заголовок отсутствует")
    return int(x_user_id)