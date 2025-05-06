from pydantic import BaseModel
from typing import Optional, Dict

class UserCreate(BaseModel):
    email: str
    name: str
    password: str

class User(BaseModel):
    id: int
    email: str
    name: str

class Prediction(BaseModel):
    id: int
    predicted: float
    accuracy: float
    algorithm: str
    input_json: Dict
    timestamp: str
