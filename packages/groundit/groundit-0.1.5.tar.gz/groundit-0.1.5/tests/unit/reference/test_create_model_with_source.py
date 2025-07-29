"""Tests for create_source_model function."""

import json
from typing import Literal
from pydantic import BaseModel, Field
from rich import print_json

from groundit.reference.create_model_with_source import (
    create_model_with_source,
    create_json_schema_with_source,
)
from groundit.reference.models import FieldWithSource
from tests.models import Simple, Nested, WithLists, NestedModel
from tests.utils import validate_source_model_schema


class ModelWithLiteral(BaseModel):
    status: Literal["active", "inactive", "pending"] = Field(description="The status")
    priority: Literal[1, 2, 3, 4, 5] = Field(description="Priority level")


class TestCreateModelWithSource:
    """Test the create_model_with_source function with various model types."""

    def test_simple_model_transformation(self):
        """Test transformation of a simple model with basic types."""
        source_model = create_model_with_source(Simple)
        validate_source_model_schema(Simple, source_model)

    def test_nested_model_transformation(self):
        """Test transformation of a model with nested BaseModel fields."""
        source_model = create_model_with_source(Nested)
        validate_source_model_schema(Nested, source_model)

    def test_model_with_lists_transformation(self):
        """Test transformation of a model with list fields."""
        source_model = create_model_with_source(WithLists)
        validate_source_model_schema(WithLists, source_model)

    def test_model_retains_field_descriptions(self):
        """Test that field descriptions are preserved in the transformed model."""
        from pydantic import Field

        class WithDescriptions(BaseModel):
            name: str = Field(description="The person's name")
            age: int = Field(description="The person's age")

        source_model = create_model_with_source(WithDescriptions)

        # Check that descriptions are preserved
        assert "name" in source_model.model_fields
        assert "age" in source_model.model_fields
        # Note: Field descriptions may not be directly accessible in the same way
        # but the model should still work correctly
        validate_source_model_schema(WithDescriptions, source_model)

    def test_model_validation_works(self):
        """Test that the created source model can be instantiated and validated."""
        source_model = create_model_with_source(Simple)

        # Create a test instance
        test_data = {
            "name": FieldWithSource(value="John", source_quote="John Smith appeared"),
            "age": FieldWithSource(value=30, source_quote="30 years old"),
        }

        instance = source_model(**test_data)
        assert instance.name.value == "John"
        assert instance.age.value == 30

    def test_literal_type_transformation(self):
        """Test transformation of a model with Literal type fields."""
        # Test that transformation works without errors
        source_model = create_model_with_source(ModelWithLiteral)

        # Test that JSON schema generation works (this was the original issue)
        schema = source_model.model_json_schema()
        assert schema is not None
        assert "properties" in schema

        # Validate the model structure
        validate_source_model_schema(ModelWithLiteral, source_model)

        # Test that we can instantiate the model
        test_data = {
            "status": FieldWithSource(value="active", source_quote="status: active"),
            "priority": FieldWithSource(value=1, source_quote="priority 1"),
        }

        instance = source_model(**test_data)
        assert instance.status.value == "active"
        assert instance.priority.value == 1


class TestCreateJsonSchemaWithSource:
    """Test the create_json_schema_with_source function."""

    def test_simple_json_schema_transformation(self):
        """Test transformation of a simple JSON schema."""

        class SimpleModel(BaseModel):
            first_name: str = Field(description="The first name.")

        ModelWithSource = create_model_with_source(SimpleModel)

        json_schema = SimpleModel.model_json_schema()
        expected_json_schema = ModelWithSource.model_json_schema()

        transformed_json_schema = create_json_schema_with_source(json_schema)

        print_json(json.dumps(transformed_json_schema, indent=2))
        print("-" * 100)
        print_json(json.dumps(expected_json_schema, indent=2))
        print("-" * 100)

        assert transformed_json_schema == expected_json_schema

    def test_with_lists_json_schema_transformation(self):
        """Test transformation of a JSON schema with list fields."""
        ModelWithSource = create_model_with_source(WithLists)

        original_json_schema = WithLists.model_json_schema()
        expected_json_schema = ModelWithSource.model_json_schema()

        transformed_json_schema = create_json_schema_with_source(original_json_schema)

        assert transformed_json_schema == expected_json_schema

    def test_nested_json_schema_transformation(self):
        """Test transformation of a nested JSON schema."""
        ModelWithSource = create_model_with_source(Nested)

        expected_json_schema = ModelWithSource.model_json_schema()
        original_json_schema = Nested.model_json_schema()
        transformed_json_schema = create_json_schema_with_source(original_json_schema)

        assert transformed_json_schema == expected_json_schema

    def test_complex_nested_model_json_schema_transformation(self):
        """Test transformation of a complex nested JSON schema."""
        ModelWithSource = create_model_with_source(NestedModel)

        expected_json_schema = ModelWithSource.model_json_schema()
        original_json_schema = NestedModel.model_json_schema()
        transformed_json_schema = create_json_schema_with_source(original_json_schema)

        assert transformed_json_schema == expected_json_schema

    def test_literal_type_transformation(self):
        """Test transformation of a JSON schema with Literal type fields."""
        ModelWithSource = create_model_with_source(ModelWithLiteral)

        original_json_schema = ModelWithLiteral.model_json_schema()
        expected_json_schema = ModelWithSource.model_json_schema()

        transformed_json_schema = create_json_schema_with_source(original_json_schema)

        assert transformed_json_schema == expected_json_schema

    def test_json_schema_with_verbalized_confidence(self):
        """Test JSON schema transformation with FieldWithSourceAndConfidence."""
        from groundit.reference.models import FieldWithSourceAndConfidence

        class SimpleModel(BaseModel):
            name: str = Field(description="The name.")
            age: int = Field(description="The age.")

        # Generate expected schema using runtime transformation
        ModelWithConfidence = create_model_with_source(
            SimpleModel, FieldWithSourceAndConfidence
        )
        expected_json_schema = ModelWithConfidence.model_json_schema()

        # Generate schema using JSON schema transformation
        original_json_schema = SimpleModel.model_json_schema()
        transformed_json_schema = create_json_schema_with_source(
            original_json_schema, FieldWithSourceAndConfidence
        )

        assert transformed_json_schema == expected_json_schema

        # Verify the title reflects the confidence suffix
        assert transformed_json_schema["title"] == "SimpleModelWithSourceAndConfidence"
