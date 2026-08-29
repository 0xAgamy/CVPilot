from openai import OpenAI
from src.helpers.config import get_settings
import instructor
from src.agents.graph import graph_builder
from typing import Optional
class AppDependencies:
    def __init__(self):
        self.settings= get_settings()
        self.llm_client= self._get_llm_client()

        self.graph= graph_builder(
            llm_client=self.llm_client,
            model_name=self.settings.MODEL_NAME
        )





    def _get_llm_client(self):
        gen_client= OpenAI(
            api_key=self.settings.API_KEY,
            base_url=self.settings.BASE_URL
        )
        return instructor.from_openai(gen_client)


# Singleton instance
_app_deps: Optional[AppDependencies] = None

def get_app_dependencies() -> AppDependencies:
    if _app_deps is None:
        raise RuntimeError("AppDependencies not initialized")
    return _app_deps

def init_app_dependencies() -> AppDependencies:
    global _app_deps
    _app_deps = AppDependencies()
    return _app_deps

def shutdown_app_dependencies():
    global _app_deps
    if _app_deps:
        _app_deps.cleanup()
        _app_deps = None