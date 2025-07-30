# Marco Polo

A Python implementation of the classic game of Marco Polo.

## Description

This library provides a simple Python function that implements the Marco Polo game logic. When you call "Marco", it responds with "Polo"!

## Installation

Install the package using pip:

```bash
pip install marco-polo
```

Or if you're using uv:

```bash
uv add marco-polo
```

## Requirements

- Python 3.12 or higher
- pandas >= 2.3.1

## Usage

```python
from marco_polo import marco_polo

# Basic usage
result = marco_polo("Marco")
print(result)  # Output: "Polo"

# Other inputs return None
result = marco_polo("Hello")
print(result)  # Output: None
```

## API Reference

### `marco_polo(name: str) -> str | None`

Returns "Polo" if the name is "Marco", otherwise returns None.

**Parameters:**
- `name` (str): The name to check

**Returns:**
- `str | None`: "Polo" if the name is "Marco", otherwise None

**Example:**
```python
from marco_polo import marco_polo

assert marco_polo("Marco") == "Polo"
assert marco_polo("Polo") is None
assert marco_polo("John") is None
```

## Development

This project uses:
- **Build system**: Hatchling
- **Dependencies**: pandas
- **Type hints**: Fully typed with py.typed marker

## License

This project is open source. See the license file for details.

## Author

- **JuanCobo** - juan.cobo@baobabsoluciones.es

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
