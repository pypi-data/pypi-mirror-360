A factory type that enables structured output behavior in Pydantic models.

Example usage:

```python
from pydantic_ai import Agent
from pydantic import BaseModel
from pydantic_outputs import structured, StructuredOutput

# structured is a type alias for StructuredOutput
# StructuredOutput(Model) is equivalent to @structured <ModelDef>

@structured
class FooBar(BaseModel):
    foo: str
    bar: int

class BarBaz(BaseModel):
    bar: str
    baz: int

agent = Agent('test')
result = agent.run_sync(
    "Generate a sample object",
    output_type=[FooBar, StructuredOutput(BarBaz)]
)

assert isinstance(result.output, dict)
```