from pydantic import BaseModel, GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core.core_schema import CoreSchema, any_schema
from typing import Any

class StructuredOutput:
    """
    A factory type that enables structured output behavior in Pydantic models.
    
    Example usage:
    ```python
    from pydantic_ai import Agent
    from pydantic import BaseModel
    from pydantic_ai.output import structured
    from pydantic_ai.output import StructuredOutput
    
    # structured is a type alias for StructuredOutput
    # StructuredOutput(Model) is equivalent to @structured <ModelDef>
    
    @structured
    class FooBar(BaseModel):
        foo: str
        bar: int
    
    class BarBaz(BaseModel):
        bar: str
        baz: int
    
    agent  =  Agent('test')
    result =  agent.run_sync(
        "Generate a sample object",
        output_type=[FooBar, StructuredOutput(BarBaz)]
    )
    
    assert isinstance(result.output, dict)
    ```
    """
    
    def __init__(self, model: BaseModel) -> None:
        self.json_schema = model.model_json_schema()
        self._model = model
        self.__name__ = model.__name__
        self.__doc__ = model.__doc__
        self.__qualname__ = model.__qualname__
    
    def __get_pydantic_core_schema__(
        self, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return any_schema()
    
    def __get_pydantic_json_schema__(
        self, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return self.json_schema

structured = StructuredOutput