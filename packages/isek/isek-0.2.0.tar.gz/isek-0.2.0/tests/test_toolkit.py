import pytest
from isek.tools.toolkit import Toolkit, SimpleFunction
from typing import Optional


@pytest.fixture
def toolkit():
    return Toolkit(name="TestToolkit", debug=True)


@pytest.fixture
def sample_functions():
    """Sample functions for testing"""

    def add(a: int, b: int) -> int:
        """Add two numbers together."""
        return a + b

    def greet(name: str, greeting: str = "Hello") -> str:
        """Greet someone with a custom message."""
        return f"{greeting}, {name}!"

    def multiply(x: float, y: float) -> float:
        """Multiply two numbers."""
        return x * y

    return [add, greet, multiply]


def test_toolkit_initialization():
    """Test toolkit initialization with different parameters"""
    # Basic initialization
    toolkit = Toolkit()
    assert toolkit.name == "toolkit"
    assert len(toolkit.functions) == 0
    assert toolkit.debug is False

    # Custom initialization
    toolkit = Toolkit(name="CustomToolkit", debug=True)
    assert toolkit.name == "CustomToolkit"
    assert toolkit.debug is True


def test_register_function(toolkit):
    """Test registering individual functions"""

    def test_function(x: int) -> int:
        """Test function that doubles a number."""
        return x * 2

    # Register function
    simple_func = toolkit.register(test_function)

    # Check registration
    assert "test_function" in toolkit.functions
    assert toolkit.get_function("test_function") is not None
    assert simple_func.name == "test_function"
    assert simple_func.description == "Test function that doubles a number."

    # Test execution
    result = toolkit.execute_function("test_function", x=5)
    assert result == 10


def test_register_with_custom_name(toolkit):
    """Test registering function with custom name"""

    def original_function():
        return "test"

    # Register with custom name
    toolkit.register(original_function, name="custom_name")

    # Check registration
    assert "custom_name" in toolkit.functions
    assert "original_function" not in toolkit.functions


def test_auto_register_tools(sample_functions):
    """Test automatic registration of tools during initialization"""
    toolkit = Toolkit(
        name="AutoToolkit", tools=sample_functions, auto_register=True, debug=True
    )

    # Check that all functions were registered
    assert len(toolkit.functions) == 3
    assert "add" in toolkit.functions
    assert "greet" in toolkit.functions
    assert "multiply" in toolkit.functions


def test_no_auto_register():
    """Test toolkit without auto-registration"""

    def test_func():
        return "test"

    toolkit = Toolkit(name="ManualToolkit", tools=[test_func], auto_register=False)

    # Check that no functions were registered
    assert len(toolkit.functions) == 0


def test_execute_function(toolkit):
    """Test function execution"""

    def add_numbers(a: int, b: int, c: int = 0) -> int:
        """Add three numbers with optional third parameter."""
        return a + b + c

    toolkit.register(add_numbers)

    # Test basic execution
    result = toolkit.execute_function("add_numbers", a=1, b=2)
    assert result == 3

    # Test with optional parameter
    result = toolkit.execute_function("add_numbers", a=1, b=2, c=3)
    assert result == 6


def test_execute_nonexistent_function(toolkit):
    """Test error handling for non-existent function"""
    with pytest.raises(ValueError, match="Function 'nonexistent' not found"):
        toolkit.execute_function("nonexistent", x=1)


def test_list_functions(toolkit, sample_functions):
    """Test listing registered functions"""
    # Register functions
    for func in sample_functions:
        toolkit.register(func)

    # Get function list
    function_names = toolkit.list_functions()

    # Check results
    assert len(function_names) == 3
    assert "add" in function_names
    assert "greet" in function_names
    assert "multiply" in function_names


def test_get_function(toolkit):
    """Test getting function by name"""

    def test_func():
        return "test"

    toolkit.register(test_func)

    # Get function
    func = toolkit.get_function("test_func")
    assert func is not None
    assert func.name == "test_func"
    assert func.entrypoint == test_func

    # Get non-existent function
    func = toolkit.get_function("nonexistent")
    assert func is None


def test_simple_function_execution():
    """Test SimpleFunction execution directly"""

    def test_func(x: int, y: str = "default") -> str:
        return f"{y}: {x}"

    simple_func = SimpleFunction(
        name="test", entrypoint=test_func, description="Test function"
    )

    # Test execution
    result = simple_func.execute(x=5, y="Value")
    assert result == "Value: 5"

    # Test with default parameter
    result = simple_func.execute(x=10)
    assert result == "default: 10"


def test_simple_function_to_dict():
    """Test SimpleFunction to_dict method"""

    def test_func(x: int) -> int:
        """Test function."""
        return x * 2

    simple_func = SimpleFunction(
        name="test_func",
        entrypoint=test_func,
        description="Test function.",
        parameters={
            "type": "object",
            "properties": {"x": {"type": "integer"}},
            "required": ["x"],
        },
    )

    func_dict = simple_func.to_dict()

    assert func_dict["name"] == "test_func"
    assert func_dict["description"] == "Test function."
    assert "parameters" in func_dict
    assert func_dict["parameters"]["type"] == "object"


def test_toolkit_repr(toolkit):
    """Test toolkit string representation"""

    def test_func():
        pass

    toolkit.register(test_func)

    repr_str = repr(toolkit)
    assert "Toolkit" in repr_str
    assert "TestToolkit" in repr_str
    assert "test_func" in repr_str


def test_toolkit_with_instructions():
    """Test toolkit with instructions"""
    instructions = "This toolkit provides mathematical operations."
    toolkit = Toolkit(name="MathToolkit", instructions=instructions)

    assert toolkit.instructions == instructions


def test_function_parameter_schema(toolkit):
    """Test that function parameter schemas are properly generated"""

    def complex_function(
        name: str, age: int, active: bool = True, scores: Optional[list] = None
    ) -> str:
        """A function with various parameter types."""
        return f"{name} is {age} years old"

    toolkit.register(complex_function)

    func = toolkit.get_function("complex_function")
    assert func is not None

    # Check that parameters schema exists
    assert func.parameters is not None
    assert "properties" in func.parameters

    # Test execution
    result = toolkit.execute_function("complex_function", name="Alice", age=30)
    assert result == "Alice is 30 years old"


def test_multiple_toolkits():
    """Test that multiple toolkits can coexist independently"""
    toolkit1 = Toolkit(name="Toolkit1")
    toolkit2 = Toolkit(name="Toolkit2")

    def func1():
        return "toolkit1"

    def func2():
        return "toolkit2"

    toolkit1.register(func1)
    toolkit2.register(func2)

    # Check independence
    assert len(toolkit1.functions) == 1
    assert len(toolkit2.functions) == 1
    assert "func1" in toolkit1.functions
    assert "func2" in toolkit2.functions

    # Test execution
    assert toolkit1.execute_function("func1") == "toolkit1"
    assert toolkit2.execute_function("func2") == "toolkit2"
