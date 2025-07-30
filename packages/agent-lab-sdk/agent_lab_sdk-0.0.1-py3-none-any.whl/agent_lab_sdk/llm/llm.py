from langchain_gigachat.chat_models import GigaChat
from agent_lab_sdk.llm.gigachat_token_manager import GigaChatTokenManager
import os

def get_model(**kwargs) -> GigaChat:
    access_token = kwargs.pop("access_token", None)
    if not access_token:
        access_token = GigaChatTokenManager.get_token()
    timeout = kwargs.pop("timeout", None)
    if not timeout:
        timeout=int(os.getenv("GLOBAL_GIGACHAT_TIMEOUT", "120"))
        
    scope = kwargs.pop("scope", None)
    if not scope:
        scope = os.getenv("GIGACHAT_SCOPE")

    verify_ssl_certs = kwargs.pop("verify_ssl_certs", False)

    if not scope:
        raise ValueError("GIGACHAT_SCOPE environment variable is not set.")

    return GigaChat(
        access_token=access_token,
        verify_ssl_certs=verify_ssl_certs,
        scope=scope,
        timeout=timeout,
        **kwargs
        )
