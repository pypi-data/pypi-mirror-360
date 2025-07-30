import unittest
from llm_json_fixer import fix_json, is_valid_json


class TestJSONFixer(unittest.TestCase):
    def test_valid_json(self):
        """Test already valid JSON."""
        result = fix_json('{"name": "John", "age": 30}')
        self.assertEqual(result, {"name": "John", "age": 30})
    
    def test_single_quotes(self):
        """Test fixing single quotes."""
        result = fix_json("{'name': 'John', 'age': 30}")
        self.assertEqual(result, {"name": "John", "age": 30})
    
    def test_trailing_commas(self):
        """Test removing trailing commas."""
        result = fix_json('{"name": "John", "age": 30,}')
        self.assertEqual(result, {"name": "John", "age": 30})
    
    def test_python_booleans(self):
        """Test fixing Python booleans."""
        result = fix_json('{"active": True, "deleted": False, "data": None}')
        self.assertEqual(result, {"active": True, "deleted": False, "data": None})
    
    def test_unquoted_keys(self):
        """Test fixing unquoted keys."""
        result = fix_json('{name: "John", age: 30}')
        self.assertEqual(result, {"name": "John", "age": 30})
    
    def test_markdown_blocks(self):
        """Test removing markdown code blocks."""
        result = fix_json('```json\n{"name": "John"}\n```')
        self.assertEqual(result, {"name": "John"})
    
    def test_extraction_from_text(self):
        """Test extracting JSON from surrounding text."""
        result = fix_json('Here is the JSON: {"name": "John"} and that\'s it.')
        self.assertEqual(result, {"name": "John"})
    
    def test_detailed_return(self):
        """Test detailed return format."""
        result = fix_json("{'name': 'John'}", return_dict=True)
        self.assertTrue(result['success'])
        self.assertEqual(result['data'], {"name": "John"})
        self.assertIsNone(result['error'])
    
    def test_is_valid_json(self):
        """Test JSON validation."""
        self.assertTrue(is_valid_json('{"name": "John"}'))
        self.assertFalse(is_valid_json("{'name': 'John'}"))
    
    def test_invalid_input(self):
        """Test handling invalid input."""
        result = fix_json(None)
        self.assertIsNone(result)
        
        result = fix_json("not json at all")
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()