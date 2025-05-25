# Implementación de Agentes MCP

## Introducción
Este documento detalla cómo implementar y extender agentes MCP (Machine Conversation Protocol) en la API REST.

## Estructura de un Agente MCP

### 1. Definición Básica
```python
from typing import Dict, List, Optional
from pydantic import BaseModel

class MCPAgent(BaseModel):
    name: str
    description: str
    capabilities: List[str]
    tools: List[str]
    model: str
    temperature: float = 0.7
    max_tokens: int = 1000
    system_prompt: str
```

### 2. Implementación de un Agente
```python
class DatabaseAgent(MCPAgent):
    def __init__(self):
        super().__init__(
            name="Database Assistant",
            description="Agente especializado en operaciones de base de datos",
            capabilities=[
                "query_execution",
                "schema_analysis",
                "data_validation"
            ],
            tools=[
                "sql_executor",
                "schema_analyzer",
                "query_optimizer"
            ],
            model="gpt-4",
            system_prompt="""Eres un asistente especializado en bases de datos.
            Puedes ejecutar consultas SQL, analizar esquemas y optimizar queries.
            Siempre verifica la seguridad de las consultas antes de ejecutarlas."""
        )

    async def execute_query(self, query: str) -> Dict:
        # Implementación de ejecución de consulta
        pass

    async def analyze_schema(self, table: str) -> Dict:
        # Implementación de análisis de esquema
        pass
```

## Integración con la API

### 1. Registro de Agentes
```python
from fastapi import APIRouter, Depends
from typing import Dict

router = APIRouter()

class AgentRegistry:
    def __init__(self):
        self.agents: Dict[str, MCPAgent] = {}

    def register_agent(self, agent: MCPAgent):
        self.agents[agent.name] = agent

    def get_agent(self, name: str) -> Optional[MCPAgent]:
        return self.agents.get(name)

registry = AgentRegistry()

# Registrar agentes
registry.register_agent(DatabaseAgent())
```

### 2. Endpoints para Agentes
```python
@router.post("/agents/{agent_name}/chat")
async def chat_with_agent(
    agent_name: str,
    message: str,
    registry: AgentRegistry = Depends(get_agent_registry)
):
    agent = registry.get_agent(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail="Agente no encontrado")
    
    response = await agent.process_message(message)
    return response
```

## Herramientas del Agente

### 1. Definición de Herramientas
```python
from typing import Any, Callable, Dict

class AgentTool:
    def __init__(
        self,
        name: str,
        description: str,
        function: Callable,
        parameters: Dict[str, Any]
    ):
        self.name = name
        self.description = description
        self.function = function
        self.parameters = parameters

    async def execute(self, **kwargs) -> Any:
        return await self.function(**kwargs)
```

### 2. Implementación de Herramientas
```python
# Herramienta para ejecutar SQL
sql_executor = AgentTool(
    name="sql_executor",
    description="Ejecuta consultas SQL de forma segura",
    function=execute_safe_sql,
    parameters={
        "query": {"type": "string", "description": "Consulta SQL a ejecutar"},
        "timeout": {"type": "integer", "description": "Timeout en segundos"}
    }
)

# Herramienta para análisis de esquema
schema_analyzer = AgentTool(
    name="schema_analyzer",
    description="Analiza la estructura de una tabla",
    function=analyze_table_schema,
    parameters={
        "table": {"type": "string", "description": "Nombre de la tabla"}
    }
)
```

## Manejo de Contexto

### 1. Gestión de Conversación
```python
class ConversationContext:
    def __init__(self):
        self.messages: List[Dict] = []
        self.tools_used: List[str] = []
        self.variables: Dict[str, Any] = {}

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

    def get_context(self) -> List[Dict]:
        return self.messages

    def set_variable(self, key: str, value: Any):
        self.variables[key] = value
```

### 2. Persistencia de Contexto
```python
from redis import Redis

class ContextManager:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.ttl = 3600  # 1 hora

    async def save_context(self, session_id: str, context: ConversationContext):
        await self.redis.setex(
            f"mcp:context:{session_id}",
            self.ttl,
            context.json()
        )

    async def load_context(self, session_id: str) -> Optional[ConversationContext]:
        data = await self.redis.get(f"mcp:context:{session_id}")
        if data:
            return ConversationContext.parse_raw(data)
        return None
```

## Ejemplos de Uso

### 1. Crear un Nuevo Agente
```python
class CodeAnalysisAgent(MCPAgent):
    def __init__(self):
        super().__init__(
            name="Code Analyzer",
            description="Agente para análisis de código",
            capabilities=["code_review", "bug_detection", "optimization"],
            tools=["code_analyzer", "bug_detector", "optimizer"],
            model="gpt-4",
            system_prompt="""Eres un experto en análisis de código.
            Puedes revisar código, detectar bugs y sugerir optimizaciones."""
        )

    async def analyze_code(self, code: str) -> Dict:
        # Implementación del análisis
        pass
```

### 2. Usar el Agente
```python
# Crear instancia
agent = CodeAnalysisAgent()

# Registrar en el sistema
registry.register_agent(agent)

# Usar el agente
async def analyze_code_endpoint(code: str):
    response = await agent.analyze_code(code)
    return response
```

## Mejores Prácticas

### 1. Seguridad
- Validar todas las entradas
- Sanitizar consultas SQL
- Limitar acceso a herramientas
- Implementar rate limiting
- Monitorear uso de recursos

### 2. Rendimiento
- Usar caché para respuestas comunes
- Implementar timeouts
- Optimizar uso de memoria
- Manejar conexiones eficientemente
- Implementar circuit breakers

### 3. Mantenimiento
- Documentar todas las herramientas
- Mantener logs detallados
- Implementar métricas
- Realizar pruebas regulares
- Actualizar modelos y dependencias

## Recursos

### Documentación
- [MCP Specification](https://mcp-spec.ejemplo.com)
- [OpenAI API](https://platform.openai.com/docs)
- [FastAPI Agents](https://fastapi.tiangolo.com/advanced/agents/)

### Herramientas
- [LangChain](https://python.langchain.com/)
- [Redis](https://redis.io/documentation)
- [PostgreSQL](https://www.postgresql.org/docs/)

### Contacto
Para soporte con agentes MCP:
- Email: mcp-support@ejemplo.com
- Slack: #mcp-agents
- Documentación: https://docs.ejemplo.com/mcp 