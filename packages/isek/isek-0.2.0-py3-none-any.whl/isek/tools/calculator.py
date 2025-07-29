from isek.tools.toolkit import Toolkit


def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


def multiply_numbers(a: int, b: int) -> int:
    """Multiply two numbers together."""
    return a * b


# Create toolkit with debug enabled
calculator_tools = Toolkit(
    name="calculator",
    tools=[add_numbers, multiply_numbers],
    instructions="Use these tools for basic math operations",
    debug=True,
)


# Register additional function
def divide_numbers(a: int, b: int) -> float:
    """Divide a by b."""
    return a / b


calculator_tools.register(divide_numbers)

# Optionally, for demonstration, call list_functions and execute_function in debug mode
if __name__ == "__main__":
    calculator_tools.list_functions()
    result = calculator_tools.execute_function("add_numbers", a=5, b=3)
    print(result)  # This print is for script run, not for import
