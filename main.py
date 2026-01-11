from fastapi import FastAPI
from app.infrastructure import di
from app.presentation.api import depends
from app.presentation.api.v1.card_controller import card_router




app = FastAPI()

app.include_router(card_router)


app.dependency_overrides[depends.uow_dependencies] = di.uow_dependencies
app.dependency_overrides[depends.card_protocol] = di.card_protocol


