from langchain_core.tools import tool # Updated import for modern LangChain
from pydantic import BaseModel, Field

# --- Pydantic Schemas for Tool Inputs ---
class AddToolInput(BaseModel):
    x: int = Field(..., description="The first number for addition")
    y: int = Field(..., description="The second number for addition")

class MultiplyToolInput(BaseModel):
    x: int = Field(..., description="The first number for multiplication")
    y: int = Field(..., description="The second number for multiplication")

# --- Tool Definitions ---
@tool(args_schema=AddToolInput)
def add_two(x: int, y: int) -> int:
    """Add two numbers. Expects input according to AddToolInput schema."""
    # The decorator @tool with args_schema handles parsing the input dict
    # into AddToolInput and then passes the fields (x, y) to this function.
    # So, the function signature remains simple (x: int, y: int).
    # If we wanted the function to receive the Pydantic model itself,
    # the tool definition and invocation would be slightly different, often
    # by defining a custom Tool class or using StructuredTool.from_function
    # where the function takes the Pydantic model.
    # For @tool, it unpacks the validated args.
    return x + y

@tool(args_schema=MultiplyToolInput)
def multiply_two(x: int, y: int) -> int:
    """Multiply two numbers. Expects input according to MultiplyToolInput schema."""
    # Similar to add_two, @tool unpacks the validated fields from MultiplyToolInput.
    return x * y
