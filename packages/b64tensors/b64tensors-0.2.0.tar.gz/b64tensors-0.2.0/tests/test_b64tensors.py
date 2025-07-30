"""
Test suite for b64tensors package.
"""

import pytest
import torch
import b64tensors


class TestB64Tensors:
    """Test cases for b64tensors encoding and decoding."""
    
    def test_encode_decode_float32_2d(self):
        """Test encoding and decoding a 2D float32 tensor."""
        original = torch.randn(10, 20, dtype=torch.float32)
        encoded = b64tensors.encode(original)
        decoded = b64tensors.decode(encoded)
        
        assert torch.equal(original, decoded)
        assert decoded.dtype == torch.float32
        assert decoded.shape == (10, 20)
    
    def test_encode_decode_float16_3d(self):
        """Test encoding and decoding a 3D float16 tensor."""
        original = torch.randn(3, 224, 224, dtype=torch.float16)
        encoded = b64tensors.encode(original)
        decoded = b64tensors.decode(encoded)
        
        assert torch.equal(original, decoded)
        assert decoded.dtype == torch.float16
        assert decoded.shape == (3, 224, 224)
    
    def test_encode_decode_int32_1d(self):
        """Test encoding and decoding a 1D int32 tensor."""
        original = torch.randint(0, 1000, (1000,), dtype=torch.int32)
        encoded = b64tensors.encode(original)
        decoded = b64tensors.decode(encoded)
        
        assert torch.equal(original, decoded)
        assert decoded.dtype == torch.int32
        assert decoded.shape == (1000,)
    
    def test_encode_decode_bool_scalar(self):
        """Test encoding and decoding a scalar boolean tensor."""
        original = torch.tensor(True, dtype=torch.bool)
        encoded = b64tensors.encode(original)
        decoded = b64tensors.decode(encoded)
        
        assert torch.equal(original, decoded)
        assert decoded.dtype == torch.bool
        assert decoded.shape == ()
    
    def test_encode_decode_all_dtypes(self):
        """Test encoding and decoding for all supported data types."""
        test_cases = [
            (torch.float16, torch.randn(5, 5, dtype=torch.float16)),
            (torch.float32, torch.randn(5, 5, dtype=torch.float32)),
            (torch.bfloat16, torch.randn(5, 5, dtype=torch.bfloat16)),
            (torch.int32, torch.randint(0, 100, (5, 5), dtype=torch.int32)),
            (torch.int64, torch.randint(0, 100, (5, 5), dtype=torch.int64)),
            (torch.uint8, torch.randint(0, 255, (5, 5), dtype=torch.uint8)),
            (torch.bool, torch.randint(0, 2, (5, 5), dtype=torch.bool)),
        ]
        
        for expected_dtype, original in test_cases:
            encoded = b64tensors.encode(original)
            decoded = b64tensors.decode(encoded)
            
            assert torch.equal(original, decoded)
            assert decoded.dtype == expected_dtype
            assert decoded.shape == original.shape
    
    def test_encode_dict(self):
        """Test encoding a dictionary of tensors."""
        tensor_dict = {
            "weights": torch.randn(10, 20, dtype=torch.float32),
            "biases": torch.randn(20, dtype=torch.float32),
            "labels": torch.randint(0, 2, (10,), dtype=torch.int32)
        }
        
        encoded_dict = b64tensors.encode_dict(tensor_dict)
        
        assert len(encoded_dict) == 3
        assert all(isinstance(v, str) for v in encoded_dict.values())
        assert all(k in encoded_dict for k in tensor_dict.keys())
    
    def test_decode_dict(self):
        """Test decoding a dictionary of encoded tensors."""
        original_dict = {
            "weights": torch.randn(10, 20, dtype=torch.float32),
            "biases": torch.randn(20, dtype=torch.float32),
            "labels": torch.randint(0, 2, (10,), dtype=torch.int32)
        }
        
        encoded_dict = b64tensors.encode_dict(original_dict)
        decoded_dict = b64tensors.decode_dict(encoded_dict)
        
        assert len(decoded_dict) == 3
        assert all(k in decoded_dict for k in original_dict.keys())
        
        for key in original_dict:
            assert torch.equal(original_dict[key], decoded_dict[key])
            assert original_dict[key].dtype == decoded_dict[key].dtype
            assert original_dict[key].shape == decoded_dict[key].shape
    
    def test_format_parsing(self):
        """Test that the encoded format matches the specification."""
        tensor = torch.randn(100, 200, dtype=torch.float32)
        encoded = b64tensors.encode(tensor)
        
        # Should have format: <data_type>##<shape>##<b64_encoded_data>
        parts = encoded.split("##")
        assert len(parts) == 3
        
        dtype_str, shape_str, b64_data = parts
        assert dtype_str == "float32"
        assert shape_str == "(100,200)"
        assert len(b64_data) > 0
    
    def test_invalid_encoded_string(self):
        """Test that invalid encoded strings raise appropriate errors."""
        with pytest.raises(ValueError, match="Invalid encoded string format"):
            b64tensors.decode("invalid")
        
    
    def test_unsupported_dtype(self):
        """Test that unsupported data types raise appropriate errors."""
        # Create a tensor with unsupported dtype (complex64)
        # Note: This test assumes complex64 is not supported
        with pytest.raises(ValueError, match="Unsupported tensor dtype"):
            tensor = torch.complex(torch.randn(5, 5), torch.randn(5, 5))
            b64tensors.encode(tensor)
    
    def test_invalid_dtype_string(self):
        """Test that invalid dtype strings raise appropriate errors."""
        with pytest.raises(ValueError, match="Unsupported dtype string"):
            b64tensors.decode("invalid_dtype##(5,5)##SGVsbG8=")
    
    def test_round_trip_consistency(self):
        """Test multiple round-trip operations for consistency."""
        original = torch.randn(50, 50, dtype=torch.float32)
        
        # Perform multiple encode/decode cycles
        current = original
        for _ in range(5):
            encoded = b64tensors.encode(current)
            current = b64tensors.decode(encoded)
        
        assert torch.equal(original, current)
    


if __name__ == "__main__":
    pytest.main([__file__]) 