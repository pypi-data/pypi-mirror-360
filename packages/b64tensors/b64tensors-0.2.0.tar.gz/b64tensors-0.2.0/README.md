# b64tensors

[![PyPI version](https://badge.fury.io/py/b64tensors.svg)](https://badge.fury.io/py/b64tensors)
[![Python Support](https://img.shields.io/pypi/pyversions/b64tensors.svg)](https://pypi.org/project/b64tensors/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A Python package for encoding and decoding PyTorch tensors as base64 strings using the b64tensor format specification.

## Features

- 🚀 **Fast**: Built on safetensors for efficient serialization
- 🔒 **Safe**: Type-safe encoding/decoding with validation
- 📦 **Simple**: Easy-to-use API with just 2 functions
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
float32##(100,200)##...
```

**3D Float16 Tensor:**
```
float16##(3,224,224)##...
```

**1D Integer Tensor:**
```
int32##(1000,)##...
```

**Scalar Boolean:**
```
bool##()##...
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
- safetensors >= 0.5.3
- This project does not require PyTorch while installing, but your environment should have PyTorch installed.

## License

This project is licensed under the Apache-2.0 License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
