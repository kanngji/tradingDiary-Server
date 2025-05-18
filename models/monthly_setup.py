from pydantic import BaseModel

class MonthlySetupRequest(BaseModel):
    email: str
    start_amount: int


class ProfitLossRequest(BaseModel):
    email: str
    date: str
    profit_loss: int