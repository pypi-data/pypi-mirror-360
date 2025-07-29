"""
b64tensors: Base64 tensor encoding and decoding for PyTorch tensors.

This package provides functions to encode PyTorch tensors as base64 strings
and decode them back to tensors, following the b64tensor format specification.
"""

import base64
from typing import Dict, Tuple, Union
import torch
from safetensors.torch import save, load


__version__ = "0.1.0"
__all__ = ["encode", "decode", "encode_dict", "decode_dict"]


# Supported data types mapping
DTYPE_MAP = {
    torch.float16: "float16",
    torch.float32: "float32",
    torch.bfloat16: "bfloat16",
    torch.int32: "int32",
    torch.int64: "int64",
    torch.uint8: "uint8",
    torch.bool: "bool",
}

REVERSE_DTYPE_MAP = {v: k for k, v in DTYPE_MAP.items()}


def _get_dtype_string(tensor: torch.Tensor) -> str:
    """Get the string representation of a tensor's data type."""
    if tensor.dtype not in DTYPE_MAP:
        raise ValueError(f"Unsupported tensor dtype: {tensor.dtype}")
    return DTYPE_MAP[tensor.dtype]


def _parse_dtype_string(dtype_str: str) -> torch.dtype:
    """Parse a dtype string back to a torch.dtype."""
    if dtype_str not in REVERSE_DTYPE_MAP:
        raise ValueError(f"Unsupported dtype string: {dtype_str}")
    return REVERSE_DTYPE_MAP[dtype_str]


def _format_shape(shape: Tuple[int, ...]) -> str:
    """Format a tensor shape as a string."""
    if len(shape) == 0:
        return "()"
    elif len(shape) == 1:
        return f"({shape[0]},)"
    else:
        return f"({','.join(map(str, shape))})"


def _parse_shape(shape_str: str) -> Tuple[int, ...]:
    """Parse a shape string back to a tuple of integers."""
    if shape_str == "()":
        return ()
    
    # Remove parentheses and split by comma
    inner = shape_str.strip("()")
    if not inner:
        return ()
    
    parts = inner.split(",")
    shape = []
    for part in parts:
        part = part.strip()
        if part:  # Skip empty parts (e.g., from trailing comma)
            shape.append(int(part))
    
    return tuple(shape)


def encode(tensor: torch.Tensor) -> str:
    """
    Encode a PyTorch tensor as a base64 string.
    
    Args:
        tensor: The PyTorch tensor to encode.
        
    Returns:
        A base64-encoded string in the format: <data_type>##<shape>##<b64_encoded_data>
        
    Raises:
        ValueError: If the tensor's data type is not supported.
    """
    # Verify type of tensor
    if not isinstance(tensor, torch.Tensor):
        raise ValueError(f"Tensor must be a PyTorch tensor, got {type(tensor)}")
    # Verify that tensor is not empty
    if tensor.numel() == 0:
        raise ValueError("Tensor is empty")
    
    # Get data type string
    dtype_str = _get_dtype_string(tensor)
    
    # Format shape
    shape_str = _format_shape(tensor.shape)
    
    # Encode tensor data using safetensors
    tensor_bytes = save({"tensor": tensor})
    
    # Encode as base64
    b64_data = base64.b64encode(tensor_bytes).decode('utf-8')
    
    # Combine components
    return f"{dtype_str}##{shape_str}##{b64_data}"


def decode(encoded_str: str) -> torch.Tensor:
    """
    Decode a base64-encoded tensor string back to a PyTorch tensor.
    
    Args:
        encoded_str: The base64-encoded tensor string.
        
    Returns:
        The decoded PyTorch tensor.
        
    Raises:
        ValueError: If the encoded string is malformed or contains unsupported data types.
    """
    # Verify type of encoded_str
    if not isinstance(encoded_str, str):
        raise ValueError(f"Encoded string must be a string, got {type(encoded_str)}")
    
    # Verify that encoded_str is not empty
    if not encoded_str:
        raise ValueError("Encoded string is empty")
    
    # Split the encoded string
    parts = encoded_str.split("##", 2)
    if len(parts) != 3:
        raise ValueError(f"Invalid encoded string format. Expected 3 parts, got {len(parts)}")
    
    dtype_str, shape_str, b64_data = parts
    
    # Parse data type
    expected_dtype = _parse_dtype_string(dtype_str)
    
    # Parse shape
    expected_shape = _parse_shape(shape_str)
    
    # Decode base64 data
    try:
        tensor_bytes = base64.b64decode(b64_data)
    except Exception as e:
        raise ValueError(f"Failed to decode base64 data: {e}")
    
    tensors = load(tensor_bytes)
    tensor = tensors["tensor"]
    
    # Validate tensor properties
    if tensor.dtype != expected_dtype:
        raise ValueError(f"Tensor dtype mismatch. Expected {expected_dtype}, got {tensor.dtype}")
    
    if tensor.shape != expected_shape:
        raise ValueError(f"Tensor shape mismatch. Expected {expected_shape}, got {tensor.shape}")
    
    return tensor


def encode_dict(tensor_dict: Dict[str, torch.Tensor]) -> Dict[str, str]:
    """
    Encode a dictionary of PyTorch tensors as base64 strings.
    
    Args:
        tensor_dict: Dictionary mapping keys to PyTorch tensors.
        
    Returns:
        Dictionary mapping the same keys to base64-encoded tensor strings.
    """
    return {key: encode(tensor) for key, tensor in tensor_dict.items()}


def decode_dict(encoded_dict: Dict[str, str]) -> Dict[str, torch.Tensor]:
    """
    Decode a dictionary of base64-encoded tensor strings back to PyTorch tensors.
    
    Args:
        encoded_dict: Dictionary mapping keys to base64-encoded tensor strings.
        
    Returns:
        Dictionary mapping the same keys to decoded PyTorch tensors.
    """
    return {key: decode(encoded_str) for key, encoded_str in encoded_dict.items()} 