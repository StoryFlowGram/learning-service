from app.application.protocols.card_protocol import CardProtocol



class IUnitOfWork:
    cards: CardProtocol

    async def __aenter__(self):
        ...
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        ...
    
    async def commit(self):
        ...
    
    async def rollback(self):
        ...