from functools import lru_cache

from app.core.config import Settings, settings
from app.repositories.vector_store import VectorStoreRepository
from app.repositories.llm_client import LLMClient
from app.repositories.embed_client import EmbedClient
from app.services.embedder import EmbedderService
from app.services.retriever import RetrieverService
from app.services.llm import LLMService
from app.services.recommend import RecommendService


def get_settings() -> Settings:
    return settings


@lru_cache
def get_vector_store() -> VectorStoreRepository:
    return VectorStoreRepository()


@lru_cache
def get_llm_client() -> LLMClient:
    return LLMClient()


@lru_cache
def get_embed_client() -> EmbedClient:
    return EmbedClient()


def get_embedder_service() -> EmbedderService:
    return EmbedderService(embed_client=get_embed_client())


def get_retriever_service() -> RetrieverService:
    return RetrieverService(vector_store=get_vector_store())


def get_llm_service() -> LLMService:
    return LLMService(llm_client=get_llm_client())


def get_recommend_service() -> RecommendService:
    return RecommendService(
        embedder=get_embedder_service(),
        retriever=get_retriever_service(),
        llm=get_llm_service(),
    )
