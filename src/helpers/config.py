from pydantic_settings import BaseSettings , SettingsConfigDict
from pydantic import ValidationError


class Settings(BaseSettings):

    BASE_URL:str
    API_KEY:str
    MODEL_NAME:str


    model_config = SettingsConfigDict(env_file="../.env")



def get_settings():
    try:
        return Settings()
    except ValidationError as e:
        print("Missing required environment variables")
        raise e