# imports
import os
import unittest
import spacy
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from langchain.document_loaders import PyPDFLoader
from unittest.mock import patch, MagicMock

from KG import (
    summarize_section,
    classify_and_generate_queries,
    summarize_in_points
    )

# summarize_section
class TestSummarizeSection(unittest.TestCase):
    """
    Testing summarize_section function based on four instances:
        1: Test with empty input: warning message stating no summary provided in the function is returned
        2: Test with a single sentence: same sentence is returned
        3: Test with multiple sentences: the resulting output would be part of the input
        4: Test with invalid input: warning message stating no summary provided in the function is returned
    """

    def test_empty_text(self):
        """Test summarization with empty input."""
        result = summarize_section("")
        self.assertEqual(result, "No summary available")

    def test_single_sentence(self):
        """Test summarization with a single sentence."""
        text = "Artificial Intelligence is transforming industries."
        result = summarize_section(text)
        self.assertEqual(result, text)

    def test_multiple_sentences(self):
        """Test summarization with multiple sentences."""
        text = (
            "Machine learning is a subset of artificial intelligence. "
            "Deep learning is a specialized form of machine learning. "
            "Neural networks are used in deep learning."
        )
        result = summarize_section(text)
        self.assertIn(result, text)

    def test_unusual_input(self):
        """Test summarization with numbers and symbols."""
        text = "*&^#$%"
        result = summarize_section(text)
        self.assertEqual(result, "No summary available")

# Generating and classifying quereis
class TestClassifyAndGenerateQueries(unittest.TestCase):
    """
    Test Cypher queries are properly generated when provided with a json file
    containing the corresponding descriptions, entities and relations
    """
    def setUp(self):
        self.test_json_data = [
            {
                "summary": "Apple provides open-source software.",
                "entities": [("Apple", "PERSON"), ("license", "DUTY")],
                "relations": [("Apple", "HAS_LICENSE", "license")]
            }
        ]

    def test_classification_and_query_generation(self):
        """Test correct classification and Cypher query generation."""
        with unittest.mock.patch("builtins.open", unittest.mock.mock_open()) as mock_file:
            queries = classify_and_generate_queries(self.test_json_data, "queries.txt")

        self.assertGreater(len(queries), 0)
        self.assertTrue(any("MERGE" in query for query in queries))
        mock_file.assert_called_once_with("queries.txt", "w")

# Final summarisation in bullet points
class TestSummarizeInPoints(unittest.TestCase):
    """
    Test the final summarization done with LLMChain done by obtaining the nodes
    descriptions and the final summary of them. Several cases are tested:
        1. Test with an empty list of summaries
        2. Test with a single sentence
        3. Test with a portion of a PDF
    """

    # Helper function to extract some section of the PDF employed in this project
    def extract_text_from_pdf(self, pdf_path):
        """Extracts text from the first few pages of a PDF file."""
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        extracted_text = " ".join([page.page_content for page in pages[:2]])
        return extracted_text if extracted_text else "No text found."

    @patch("KG.LLMChain")
    def test_empty_summaries(self, mock_llm_chain):
        """Test summarization with an empty list of summaries."""
        mock_llm_chain.return_value.run.return_value = "No summary available"
        llm = MagicMock()

        result = summarize_in_points([], llm)
        self.assertEqual(result, "No summary available")

    @patch("KG.LLMChain")
    def test_single_short_summary(self, mock_llm_chain):
        """Test summarization with a single short summary."""
        mock_llm_chain.return_value.run.side_effect = lambda x: f"Summary of: {x['text']}"
        llm = MagicMock()

        summaries = ["This is a test summary."]
        result = summarize_in_points(summaries, llm)

        self.assertIn("Summary of:", result)

    @patch("KG.LLMChain")
    def test_long_text_chunking(self, mock_llm_chain):
        """Test summarization with long text extracted from a real PDF file."""
        mock_llm_chain.return_value.run.side_effect = lambda x: f"Processed summary: {x['text']}"
        llm = MagicMock()

        pdf_path = os.path.join("../TCs", "Apple_MacOS_English.pdf")
        text = self.extract_text_from_pdf(pdf_path)

        summary = [text]
        result = summarize_in_points(summary, llm)

        self.assertIn("Processed summary:", result)
        self.assertTrue(len(result.strip()) > 0)
        self.assertTrue(any(keyword in result.lower() for keyword in ["apple software", "licence agreement"]))


if __name__ == "__main__":
    unittest.main()