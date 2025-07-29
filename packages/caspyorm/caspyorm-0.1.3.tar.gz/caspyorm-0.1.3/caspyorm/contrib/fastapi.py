"""
Integração opcional com FastAPI para CaspyORM.

Este módulo fornece helpers para facilitar a integração entre CaspyORM e FastAPI,
incluindo injeção de dependência de sessão, conversão automática de modelos
e validação integrada.

Exemplo de uso:
    from fastapi import FastAPI, Depends
    from caspyorm.contrib.fastapi import get_session, as_response_model
    
    app = FastAPI()
    
    @app.get("/users/{user_id}")
    async def get_user(user_id: str, session = Depends(get_session)):
        user = await User.get_async(id=user_id)
        return as_response_model(user)
"""

from typing import Any, Type, Optional, List, Dict, Union, TYPE_CHECKING
from functools import wraps
import logging

if TYPE_CHECKING:
    from fastapi import Depends, HTTPException, status
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, create_model

try:
    from fastapi import Depends, HTTPException, status
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, create_model
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    # Dummy classes para quando FastAPI não está disponível
    class Depends:
        def __init__(self, dependency):
            pass
    
    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str):
            self.status_code = status_code
            self.detail = detail
    
    class JSONResponse:
        pass
    
    class BaseModel:
        pass
    
    class status:
        HTTP_503_SERVICE_UNAVAILABLE = 503
        HTTP_400_BAD_REQUEST = 400
        HTTP_500_INTERNAL_SERVER_ERROR = 500

from ..connection import get_session as _get_session, get_async_session as _get_async_session
from ..model import Model
from ..exceptions import ValidationError, ConnectionError

logger = logging.getLogger(__name__)


def get_session():
    """
    Dependency para injetar sessão síncrona do Cassandra em endpoints FastAPI.
    
    Returns:
        Sessão ativa do Cassandra
        
    Raises:
        HTTPException: Se não houver conexão ativa
    """
    if not FASTAPI_AVAILABLE:
        raise ImportError("FastAPI não está instalado. Instale com: pip install caspyorm[fastapi]")
    
    try:
        session = _get_session()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Serviço de banco de dados indisponível"
            )
        return session
    except Exception as e:
        logger.error(f"Erro ao obter sessão do Cassandra: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Erro de conexão com banco de dados"
        )


def get_async_session():
    """
    Dependency para injetar sessão assíncrona do Cassandra em endpoints FastAPI.
    
    Returns:
        Sessão assíncrona ativa do Cassandra
        
    Raises:
        HTTPException: Se não houver conexão ativa
    """
    if not FASTAPI_AVAILABLE:
        raise ImportError("FastAPI não está instalado. Instale com: pip install caspyorm[fastapi]")
    
    try:
        session = _get_async_session()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Serviço de banco de dados indisponível"
            )
        return session
    except Exception as e:
        logger.error(f"Erro ao obter sessão assíncrona do Cassandra: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Erro de conexão com banco de dados"
        )


def as_response_model(
    model_instance: Optional[Model],
    exclude: Optional[List[str]] = None,
    include: Optional[List[str]] = None
) -> Union[Dict[str, Any], None]:
    """
    Converte uma instância de Model para um dicionário adequado para resposta HTTP.
    
    Args:
        model_instance: Instância do modelo CaspyORM
        exclude: Lista de campos para excluir da resposta
        include: Lista de campos para incluir na resposta (se especificado, exclui todos os outros)
        
    Returns:
        Dicionário com os dados do modelo ou None se a instância for None
    """
    if model_instance is None:
        return None
    
    data = model_instance.model_dump()
    
    if include:
        # Incluir apenas os campos especificados
        return {k: v for k, v in data.items() if k in include}
    elif exclude:
        # Excluir os campos especificados
        return {k: v for k, v in data.items() if k not in exclude}
    
    return data


def as_response_models(
    model_instances: List[Model],
    exclude: Optional[List[str]] = None,
    include: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Converte uma lista de instâncias de Model para uma lista de dicionários.
    
    Args:
        model_instances: Lista de instâncias do modelo CaspyORM
        exclude: Lista de campos para excluir da resposta
        include: Lista de campos para incluir na resposta
        
    Returns:
        Lista de dicionários com os dados dos modelos
    """
    result = []
    for instance in model_instances:
        response = as_response_model(instance, exclude=exclude, include=include)
        if response is not None:
            result.append(response)
    return result


def create_response_model(
    model_class: Type[Model],
    name: Optional[str] = None,
    exclude: Optional[List[str]] = None,
    include: Optional[List[str]] = None
) -> Type[BaseModel]:
    """
    Cria um modelo Pydantic para resposta HTTP baseado em um modelo CaspyORM.
    
    Args:
        model_class: Classe do modelo CaspyORM
        name: Nome do modelo de resposta (padrão: {ModelName}Response)
        exclude: Lista de campos para excluir
        include: Lista de campos para incluir
        
    Returns:
        Classe Pydantic para resposta HTTP
    """
    if not FASTAPI_AVAILABLE:
        raise ImportError("FastAPI não está instalado. Instale com: pip install caspyorm[fastapi]")
    
    # Obter o modelo Pydantic base
    pydantic_model = model_class.as_pydantic()
    
    # Filtrar campos se necessário
    fields = {}
    
    # Detectar versão do Pydantic
    try:
        import pydantic
        pydantic_v2 = pydantic.VERSION.startswith('2')
    except ImportError:
        pydantic_v2 = False
    
    if pydantic_v2:
        # Pydantic v2: usar model_fields
        for field_name, field_info in pydantic_model.model_fields.items():
            if include and field_name not in include:
                continue
            if exclude and field_name in exclude:
                continue
            fields[field_name] = (field_info.annotation, field_info.default)
    else:
        # Pydantic v1: usar __fields__
        for field_name, field_info in pydantic_model.__fields__.items():
            if include and field_name not in include:
                continue
            if exclude and field_name in exclude:
                continue
            fields[field_name] = (field_info.type_, field_info.default)
    
    # Criar nome do modelo
    model_name = name or f"{model_class.__name__}Response"
    
    # Criar modelo de resposta
    return create_model(model_name, **fields)


def handle_caspyorm_errors(func):
    """
    Decorator para tratar erros específicos da CaspyORM em endpoints FastAPI.
    
    Converte exceções da CaspyORM em respostas HTTP apropriadas.
    """
    if not FASTAPI_AVAILABLE:
        raise ImportError("FastAPI não está instalado. Instale com: pip install caspyorm[fastapi]")
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ValidationError as e:
            logger.warning(f"Erro de validação: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro de validação: {str(e)}"
            )
        except ConnectionError as e:
            logger.error(f"Erro de conexão: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Erro de conexão com banco de dados"
            )
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno do servidor"
            )
    
    return wrapper


class CaspyORMDependency:
    """
    Classe para gerenciar dependências da CaspyORM em FastAPI.
    
    Fornece métodos para configurar e gerenciar conexões e sessões.
    """
    
    def __init__(self, auto_connect: bool = True):
        """
        Inicializa o gerenciador de dependências.
        
        Args:
            auto_connect: Se deve conectar automaticamente ao inicializar
        """
        self.auto_connect = auto_connect
        self._session = None
        self._async_session = None
    
    def get_session(self):
        """Retorna a sessão síncrona."""
        return get_session()
    
    def get_async_session(self):
        """Retorna a sessão assíncrona."""
        return get_async_session()
    
    def __call__(self):
        """Permite usar a instância como dependency."""
        return self.get_session()


# Instância padrão para uso direto
caspyorm_dependency = CaspyORMDependency()


# Aliases para facilitar o uso
get_caspyorm_session = get_session
get_caspyorm_async_session = get_async_session
model_to_response = as_response_model
models_to_response = as_response_models
create_response_schema = create_response_model 