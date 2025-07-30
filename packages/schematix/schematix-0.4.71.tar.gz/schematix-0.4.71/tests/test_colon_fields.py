# ~/schematix/tests/test_colon_fields.py
"""Tests for colon merge target functionality."""
import pytest
from schematix import Field, Schema


class TestColonMergeFields:
    """Test colon merge target functionality."""

    def test_simple_merge_target(self):
        """Test merging into simple target."""
        field = Field(target='filters:')
        target_obj = {'filters': {'existing': 'data'}}

        field.assign(target_obj, {'new': 'value', 'another': 'item'})

        expected = {
            'filters': {
                'existing': 'data',
                'new': 'value',
                'another': 'item'
            }
        }
        assert target_obj == expected

    def test_merge_target_creates_dict(self):
        """Test merge target creates dict if it doesn't exist."""
        field = Field(target='filters:')
        target_obj = {}

        field.assign(target_obj, {'new': 'value'})

        assert target_obj == {'filters': {'new': 'value'}}

    def test_nested_merge_target(self):
        """Test merging into nested target."""
        field = Field(target='config.filters:')
        target_obj = {'config': {'filters': {'existing': 'data'}}}

        field.assign(target_obj, {'new': 'value'})

        expected = {
            'config': {
                'filters': {
                    'existing': 'data',
                    'new': 'value'
                }
            }
        }
        assert target_obj == expected

    def test_escaped_colon_literal(self):
        """Test escaped colon is treated as literal."""
        field = Field(target='filters\\:')
        target_obj = {}

        field.assign(target_obj, 'literal_value')

        assert target_obj == {'filters:': 'literal_value'}

    def test_merge_target_non_dict_error(self):
        """Test error when trying to merge into non-dict."""
        field = Field(target='filters:')
        target_obj = {'filters': 'not_a_dict'}

        with pytest.raises(ValueError):
            field.assign(target_obj, {'new': 'value'})

    def test_merge_target_non_dict_value_error(self):
        """Test error when trying to merge non-dict value."""
        field = Field(target='filters:')
        target_obj = {}

        with pytest.raises(ValueError):
            field.assign(target_obj, 'not_a_dict')

    def test_merge_with_schema(self):
        """Test merge functionality in full schema."""
        class TestSchema(Schema):
            base_data = Field(source='base', target='filters.base')
            merge_data = Field(source='merge', target='filters:')

        data = {
            'base': 'base_value',
            'merge': {'new_key': 'new_value', 'another': 'data'}
        }

        result = TestSchema().transform(data)

        expected = {
            'base_data': 'base_value',  # Field name, not target
            'merge_data': {'new_key': 'new_value', 'another': 'data'}  # Field name, not target
        }
        assert result == expected
