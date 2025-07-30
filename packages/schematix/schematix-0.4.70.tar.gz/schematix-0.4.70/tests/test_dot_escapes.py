# ~/schematix/tests/test_dot_escapes.py
"""Tests for escaped dot functionality in target paths."""

import pytest
from schematix import Schema, Field


class TestDotEscapes:
    """Test escaped dot functionality in target assignment."""

    def test_simple_escaped_dot(self):
        """Test basic escaped dot becomes literal key."""
        class TestSchema(Schema):
            field = Field(source='value', target='designers\\.name')

        schema = TestSchema()
        result = {}
        schema._fields['field'].assign(result, ['Nike', 'Adidas'])

        assert result == {'designers.name': ['Nike', 'Adidas']}
        assert 'designers' not in result  # Should not create nested structure

    def test_multiple_escaped_dots(self):
        """Test multiple escaped dots in same key."""
        class TestSchema(Schema):
            field = Field(source='value', target='api\\.v2\\.endpoint')

        schema = TestSchema()
        result = {}
        schema._fields['field'].assign(result, '/users')

        assert result == {'api.v2.endpoint': '/users'}

    def test_normal_nested_unchanged(self):
        """Test normal nested behavior still works."""
        class TestSchema(Schema):
            field = Field(source='value', target='user.profile.name')

        schema = TestSchema()
        result = {}
        schema._fields['field'].assign(result, 'John Doe')

        expected = {'user': {'profile': {'name': 'John Doe'}}}
        assert result == expected

    def test_mixed_escaped_and_nested(self):
        """Test combination of escaped and unescaped dots."""
        class TestSchema(Schema):
            field = Field(source='value', target='user.api\\.key.data')

        schema = TestSchema()
        result = {}
        schema._fields['field'].assign(result, 'secret')

        expected = {'user': {'api.key': {'data': 'secret'}}}
        assert result == expected

    def test_complex_mixed_case(self):
        """Test complex mixed case with multiple escaped parts."""
        class TestSchema(Schema):
            field = Field(source='value', target='config.db\\.host.connection\\.pool.size')

        schema = TestSchema()
        result = {}
        schema._fields['field'].assign(result, 10)

        expected = {'config': {'db.host': {'connection.pool': {'size': 10}}}}
        assert result == expected

    def test_no_dots_unchanged(self):
        """Test simple assignment without dots still works."""
        class TestSchema(Schema):
            field = Field(source='value', target='simple_key')

        schema = TestSchema()
        result = {}
        schema._fields['field'].assign(result, 'value')

        assert result == {'simple_key': 'value'}

    def test_full_schema_transformation(self):
        """Test escaped dots work in full schema transformation."""
        class TestSchema(Schema):
            designers = Field(source='brands', target='designers\\.name')
            category = Field(source='cat', target='category.path')
            metadata = Field(source='meta', target='api\\.version')

        data = {
            'brands': ['Nike', 'Adidas'],
            'cat': 'clothing',
            'meta': 'v2.1'
        }

        schema = TestSchema()
        result = schema.transform(data)

        # Schema transformation uses field names as keys, not targets
        expected = {
            'designers': ['Nike', 'Adidas'],
            'category': 'clothing',
            'metadata': 'v2.1'
        }
        assert result == expected

        # Test that direct field assignment uses escaped targets correctly
        target_obj = {}
        schema._fields['designers'].assign(target_obj, ['Nike', 'Adidas'])
        schema._fields['metadata'].assign(target_obj, 'v2.1')

        assert target_obj['designers.name'] == ['Nike', 'Adidas']
        assert target_obj['api.version'] == 'v2.1'

    def test_escaped_dots_with_object_assignment(self):
        """Test escaped dots work with object attribute assignment."""
        class MockObject:
            pass

        class TestSchema(Schema):
            field = Field(source='value', target='weird\\.attr')

        schema = TestSchema()
        obj = MockObject()
        schema._fields['field'].assign(obj, 'test_value')

        assert hasattr(obj, 'weird.attr')
        assert getattr(obj, 'weird.attr') == 'test_value'

    def test_edge_case_only_escaped_dots(self):
        """Test edge case where all dots are escaped."""
        class TestSchema(Schema):
            field = Field(source='value', target='a\\.b\\.c\\.d')

        schema = TestSchema()
        result = {}
        schema._fields['field'].assign(result, 'value')

        assert result == {'a.b.c.d': 'value'}

    def test_edge_case_trailing_escaped_dot(self):
        """Test edge case with trailing escaped dot."""
        class TestSchema(Schema):
            field = Field(source='value', target='key\\.')

        schema = TestSchema()
        result = {}
        schema._fields['field'].assign(result, 'value')

        assert result == {'key.': 'value'}

    def test_real_world_designers_case(self):
        """Test the original designers.name case that prompted this feature."""
        class ProductSchema(Schema):
            brands = Field(source='designer_names', target='designers\\.name')

        data = {'designer_names': ['Gucci', 'Prada', 'Louis Vuitton']}

        schema = ProductSchema()
        result = schema.transform(data)

        # Schema transform uses field name 'brands' as key
        assert result == {'brands': ['Gucci', 'Prada', 'Louis Vuitton']}

        # Test direct assignment uses escaped target correctly
        target_obj = {}
        schema._fields['brands'].assign(target_obj, ['Gucci', 'Prada', 'Louis Vuitton'])
        assert target_obj == {'designers.name': ['Gucci', 'Prada', 'Louis Vuitton']}

        # Verify no nested structure was created
        assert isinstance(target_obj['designers.name'], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
