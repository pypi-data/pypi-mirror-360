# b64tensors

[![PyPI version](https://badge.fury.io/py/b64tensors.svg)](https://badge.fury.io/py/b64tensors)
[![Python Support](https://img.shields.io/pypi/pyversions/b64tensors.svg)](https://pypi.org/project/b64tensors/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A Python package for encoding and decoding PyTorch tensors as base64 strings using the b64tensor format specification.

## Features

- 🚀 **Fast**: Built on safetensors for efficient serialization
- 🔒 **Safe**: Type-safe encoding/decoding with validation
- 📦 **Simple**: Easy-to-use API with just 4 functions
- 🎯 **Comprehensive**: Supports all major PyTorch data types
- 🔄 **Reliable**: Extensive test coverage and error handling

## Installation

```bash
pip install b64tensors
```

## Quick Start

```python
import torch
import b64tensors

# Create a tensor
tensor = torch.randn(100, 200, dtype=torch.float32)

# Encode to base64 string
encoded = b64tensors.encode(tensor)
print(encoded)  # float32##(100,200)##<base64_data>

# Decode back to tensor
decoded = b64tensors.decode(encoded)
print(torch.equal(tensor, decoded))  # True
```

## API Reference

### Core Functions

#### `encode(tensor: torch.Tensor) -> str`

Encode a PyTorch tensor as a base64 string.

**Parameters:**
- `tensor`: The PyTorch tensor to encode

**Returns:**
- Base64-encoded string in format: `<data_type>##<shape>##<b64_encoded_data>`

**Example:**
```python
tensor = torch.randn(10, 20, dtype=torch.float32)
encoded = b64tensors.encode(tensor)
```

#### `decode(encoded_str: str) -> torch.Tensor`

Decode a base64-encoded tensor string back to a PyTorch tensor.

**Parameters:**
- `encoded_str`: The base64-encoded tensor string

**Returns:**
- The decoded PyTorch tensor

**Example:**
```python
decoded = b64tensors.decode(encoded_str)
```

#### `encode_dict(tensor_dict: Dict[str, torch.Tensor]) -> Dict[str, str]`

Encode a dictionary of PyTorch tensors as base64 strings.

**Parameters:**
- `tensor_dict`: Dictionary mapping keys to PyTorch tensors

**Returns:**
- Dictionary mapping the same keys to base64-encoded tensor strings

**Example:**
```python
tensors = {
    "weights": torch.randn(10, 20),
    "biases": torch.randn(20)
}
encoded_dict = b64tensors.encode_dict(tensors)
```

#### `decode_dict(encoded_dict: Dict[str, str]) -> Dict[str, torch.Tensor]`

Decode a dictionary of base64-encoded tensor strings back to PyTorch tensors.

**Parameters:**
- `encoded_dict`: Dictionary mapping keys to base64-encoded tensor strings

**Returns:**
- Dictionary mapping the same keys to decoded PyTorch tensors

**Example:**
```python
decoded_dict = b64tensors.decode_dict(encoded_dict)
```

## Supported Data Types

- `torch.float16` - 16-bit floating point
- `torch.float32` - 32-bit floating point
- `torch.bfloat16` - Brain floating point (16-bit)
- `torch.int32` - 32-bit integer
- `torch.int64` - 64-bit integer
- `torch.uint8` - 8-bit unsigned integer
- `torch.bool` - Boolean

## Format Specification

The b64tensor format follows this structure:
```
<data_type>##<shape>##<b64_encoded_data>
```

### Examples

**2D Float32 Tensor:**
```
float32##(100,200)##SGVsbG8gV29ybGQhIFRoaXMgaXMgYSBzYW1wbGUgYmFzZTY0IGVuY29kZWQgdGVuc29yIGRhdGE...
```

**3D Float16 Tensor:**
```
float16##(3,224,224)##QWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXpBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWg...
```

**1D Integer Tensor:**
```
int32##(1000,)##MTIzNDU2Nzg5MGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6QUJDREVGR0hJSktMTU5PUFF...
```

**Scalar Boolean:**
```
bool##()##dHJ1ZQ==
```

## Advanced Usage

### Working with Model Weights

```python
import torch
import torch.nn as nn
import b64tensors

# Create a simple model
model = nn.Linear(784, 10)

# Encode all model parameters
encoded_weights = b64tensors.encode_dict(dict(model.named_parameters()))

# Save to file or send over network
with open('model_weights.txt', 'w') as f:
    for name, encoded_tensor in encoded_weights.items():
        f.write(f"{name}: {encoded_tensor}\n")

# Later, decode the weights
decoded_weights = b64tensors.decode_dict(encoded_weights)

# Load back into model
for name, param in model.named_parameters():
    param.data = decoded_weights[name]
```

### Batch Processing

```python
import torch
import b64tensors

# Process multiple tensors
tensors = [
    torch.randn(100, 200, dtype=torch.float32),
    torch.randint(0, 10, (50, 50), dtype=torch.int32),
    torch.randn(3, 224, 224, dtype=torch.float16)
]

# Encode all tensors
encoded_tensors = [b64tensors.encode(t) for t in tensors]

# Decode all tensors
decoded_tensors = [b64tensors.decode(e) for e in encoded_tensors]

# Verify they match
for original, decoded in zip(tensors, decoded_tensors):
    assert torch.equal(original, decoded)
```

## Error Handling

The package provides comprehensive error handling:

```python
import b64tensors

try:
    # Invalid format
    b64tensors.decode("invalid_format")
except ValueError as e:
    print(f"Error: {e}")

try:
    # Unsupported dtype
    tensor = torch.complex(torch.randn(5, 5), torch.randn(5, 5))
    b64tensors.encode(tensor)
except ValueError as e:
    print(f"Error: {e}")
```

## Development

### Setting up Development Environment

```bash
git clone https://github.com/44670/b64tensors.git
cd b64tensors
pip install -e .
pip install pytest torch safetensors
```

### Running Tests

```bash
pytest tests/
```

### Building Package

```bash
python -m build
```

## Requirements

- Python >= 3.8
- PyTorch >= 1.10.0
- safetensors >= 0.6.0

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Changelog

### 0.1.0
- Initial release
- Basic encode/decode functionality
- Support for all major PyTorch data types
- Dictionary encoding/decoding
- Comprehensive test suite