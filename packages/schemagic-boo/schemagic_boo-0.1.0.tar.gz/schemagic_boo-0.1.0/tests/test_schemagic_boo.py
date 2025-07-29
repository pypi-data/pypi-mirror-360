"""
Tests for schemagic_boo
"""
import sys
import os

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemagic_boo import generate_model_code, generate_from_json, generate_from_dict


def test_simple_json():
    """Test simple JSON to model conversion."""
    json_data = '{"name": "Alice", "age": 30, "active": true}'
    result = generate_from_json(json_data, "User")
    
    assert "class User(BaseModel):" in result
    assert "name: str" in result
    assert "age: int" in result
    assert "active: bool" in result


def test_nested_structure():
    """Test nested structure conversion."""
    data = {
        "user": {
            "name": "Alice",
            "age": 30
        },
        "active": True
    }
    result = generate_from_dict(data, "UserProfile")
    
    assert "class User(BaseModel):" in result
    assert "class UserProfile(BaseModel):" in result
    assert "user: User" in result


def test_optional_fields():
    """Test handling of None values."""
    data = {"name": "Alice", "email": None}
    result = generate_from_dict(data, "User")
    
    assert "email: Optional[str] = None" in result


def test_list_handling():
    """Test handling of lists."""
    data = {"tags": ["python", "pydantic"], "scores": [1, 2, 3]}
    result = generate_from_dict(data, "TestModel")
    
    assert "tags: List[str]" in result
    assert "scores: List[int]" in result


def test_invalid_json():
    """Test handling of invalid JSON."""
    try:
        generate_from_json("invalid json", "Test")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Invalid JSON" in str(e)


def test_non_dict_root():
    """Test handling of non-dict root."""
    try:
        generate_from_json('[1, 2, 3]', "Test")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "must represent an object" in str(e)


def test_field_sanitization():
    """Test field name sanitization."""
    data = {"user-name": "Alice", "2nd_field": "value", "class": "reserved"}
    result = generate_from_dict(data, "TestModel")
    
    # Should contain sanitized field names
    assert "user_name:" in result
    assert "field_2nd_field:" in result
    assert ("class_:" in result or "field_class:" in result)


# Simple test runner for when pytest is not available
if __name__ == "__main__":
    print("🧪 Running schemagic_boo tests...")
    
    tests = [
        test_simple_json,
        test_nested_structure,
        test_optional_fields,
        test_list_handling,
        test_invalid_json,
        test_non_dict_root,
        test_field_sanitization
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            print(f"✅ {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")