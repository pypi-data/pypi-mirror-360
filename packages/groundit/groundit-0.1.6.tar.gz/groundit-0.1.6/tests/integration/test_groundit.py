"""Integration tests for the complete groundit pipeline.

This module tests the full end-to-end workflow of using groundit
for data extraction with both Pydantic models and JSON schemas.
"""

from typing import Literal
import pytest
from pydantic import BaseModel, Field
from rich.pretty import pprint

from groundit import groundit, create_model_with_source, FieldWithSourceAndConfidence
from tests.utils import validate_source_spans


class Patient(BaseModel):
    """Simple patient model for testing extraction."""

    first_name: str = Field(description="The given name of the patient")
    last_name: str = Field(description="The family name of the patient")
    birthDate: str = Field(description="The date of birth for the individual")
    gender: Literal["male", "female", "other"] = Field(
        description="The gender of the patient"
    )


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.xfail(
    strict=False, reason="Flaky - usually passes but may fail due to LLMs"
)
class TestGrounditPipeline:
    """Integration tests for the complete groundit pipeline."""

    @pytest.mark.parametrize(
        "llm_model",
        [
            "openai/gpt-4.1",
            "huggingface/nebius/mistralai/Mistral-Small-3.1-24B-Instruct-2503",
        ],
    )
    def test_pydantic_model(self, openai_client, test_document, llm_model):
        """
        Test the complete groundit pipeline using Pydantic models.

        This test verifies the unified groundit() function works with Pydantic models.
        """
        # Use the unified groundit function
        final_result = groundit(
            document=test_document, extraction_model=Patient, llm_model=llm_model
        )

        # Validate the complete pipeline result
        # Validate structure can be loaded back into the model
        patient_with_source = create_model_with_source(Patient)
        validated_instance = patient_with_source.model_validate(final_result)
        assert validated_instance is not None

        # Validate that source spans are correct
        validate_source_spans(final_result, test_document)

        # Validate confidence scores exist and are valid probabilities
        assert 0 < final_result["first_name"]["value_confidence"] <= 1.0
        assert 0 < final_result["last_name"]["value_confidence"] <= 1.0
        assert 0 < final_result["birthDate"]["value_confidence"] <= 1.0
        assert 0 < final_result["gender"]["value_confidence"] <= 1.0
        assert 0 < final_result["first_name"]["source_quote_confidence"] <= 1.0
        assert 0 < final_result["last_name"]["source_quote_confidence"] <= 1.0
        assert 0 < final_result["birthDate"]["source_quote_confidence"] <= 1.0
        assert 0 < final_result["gender"]["source_quote_confidence"] <= 1.0

        pprint(final_result, expand_all=True)

    @pytest.mark.parametrize(
        "llm_model",
        [
            "openai/gpt-4.1",
            "huggingface/nebius/mistralai/Mistral-Small-3.1-24B-Instruct-2503",
        ],
    )
    def test_json_schema(self, openai_client, test_document, llm_model):
        """
        Test the complete groundit pipeline using JSON schemas.

        This test verifies the unified groundit() function works with JSON schemas.
        """

        json_schema = Patient.model_json_schema()

        final_result = groundit(
            document=test_document, extraction_schema=json_schema, llm_model=llm_model
        )

        # validate the result
        patient_with_source = create_model_with_source(Patient)
        validated_instance = patient_with_source.model_validate(final_result)
        assert validated_instance is not None

        # validate the source spans
        validate_source_spans(final_result, test_document)

        # Validate confidence scores exist and are valid probabilities
        assert 0 < final_result["first_name"]["value_confidence"] <= 1.0
        assert 0 < final_result["last_name"]["value_confidence"] <= 1.0
        assert 0 < final_result["birthDate"]["value_confidence"] <= 1.0
        assert 0 < final_result["gender"]["value_confidence"] <= 1.0
        assert 0 < final_result["first_name"]["source_quote_confidence"] <= 1.0
        assert 0 < final_result["last_name"]["source_quote_confidence"] <= 1.0
        assert 0 < final_result["birthDate"]["source_quote_confidence"] <= 1.0
        assert 0 < final_result["gender"]["source_quote_confidence"] <= 1.0

        pprint(final_result, expand_all=True)

    def test_pipeline_consistency(self, openai_client, test_document):
        """
        Test that Pydantic model and JSON schema approaches produce equivalent results.

        This test verifies that both transformation approaches (runtime model vs schema)
        produce structurally identical results when used in the groundit() function.
        """

        # Get results from both approaches using the unified function
        # Pydantic approach
        pydantic_result = groundit(document=test_document, extraction_model=Patient)

        # JSON schema approach
        schema_result = groundit(
            document=test_document,
            extraction_schema=Patient.model_json_schema(),
        )

        # Both should have the same structure (keys and nested structure)
        assert set(pydantic_result.keys()) == set(schema_result.keys())

        # Both should be valid according to the source model
        patient_with_source = create_model_with_source(Patient)
        patient_with_source.model_validate(pydantic_result)
        patient_with_source.model_validate(schema_result)

    @pytest.mark.parametrize("llm_model", ["anthropic/claude-sonnet-4-20250514"])
    def test_verbalized_confidence_pydantic_model(
        self, openai_client, test_document, llm_model
    ):
        """
        Test the verbalized confidence pipeline using Pydantic models.

        This test verifies the verbalized confidence path works and returns properly structured results.
        """
        # Use verbalized confidence
        final_result = groundit(
            document=test_document,
            extraction_model=Patient,
            llm_model=llm_model,
            verbalized_confidence=True,
        )

        print("\n=== VERBALIZED CONFIDENCE RESULT ===")
        pprint(final_result, expand_all=True)

        # Each field should have the verbalized confidence structure
        for field_value in final_result.values():
            assert "value" in field_value
            assert "source_quote" in field_value
            assert "value_confidence" in field_value
            assert "source_quote_confidence" in field_value

            # Confidence values should be in valid range
            assert 0.0 <= field_value["value_confidence"] <= 1.0
            assert 0.0 <= field_value["source_quote_confidence"] <= 1.0

        # Should be able to validate with FieldWithSourceAndConfidence model (used when verbalized confidence is True)
        patient_with_src_and_confidence = create_model_with_source(
            model=Patient, enrichment_class=FieldWithSourceAndConfidence
        )
        validated_instance = patient_with_src_and_confidence.model_validate(
            final_result
        )
        assert validated_instance is not None

    @pytest.mark.parametrize("llm_model", ["anthropic/claude-sonnet-4-20250514"])
    def test_verbalized_confidence_json_schema(
        self, openai_client, test_document, llm_model
    ):
        """
        Test the verbalized confidence pipeline using JSON schemas.

        This test verifies the verbalized confidence path works with JSON schema approach.
        """
        # Use verbalized confidence with JSON schema
        final_result = groundit(
            document=test_document,
            extraction_schema=Patient.model_json_schema(),
            llm_model=llm_model,
            verbalized_confidence=True,
        )

        print("\n=== VERBALIZED CONFIDENCE JSON SCHEMA RESULT ===")
        pprint(final_result, expand_all=True)

        # Each field should have the verbalized confidence structure
        for field_value in final_result.values():
            assert "value" in field_value
            assert "source_quote" in field_value
            assert "value_confidence" in field_value
            assert "source_quote_confidence" in field_value

            # Confidence values should be in valid range
            assert 0.0 <= field_value["value_confidence"] <= 1.0
            assert 0.0 <= field_value["source_quote_confidence"] <= 1.0

        # Should be able to validate with FieldWithSourceAndConfidence model
        patient_with_src_and_confidence = create_model_with_source(
            model=Patient, enrichment_class=FieldWithSourceAndConfidence
        )
        validated_instance = patient_with_src_and_confidence.model_validate(
            final_result
        )
        assert validated_instance is not None
