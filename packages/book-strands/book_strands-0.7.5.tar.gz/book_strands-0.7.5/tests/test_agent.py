import unittest
from unittest.mock import Mock, patch

from book_strands.agent import agent
from book_strands.constants import BEDROCK_NOVA_PRO_MODEL
from book_strands.tools import (
    download_ebook,
    file_delete,
    file_move,
    lookup_books,
    path_list,
)


class TestAgent(unittest.TestCase):
    def setUp(self):
        self.mock_response = Mock()
        self.mock_response.metrics.accumulated_usage = 100

    @patch("book_strands.agent.Agent")
    @patch("book_strands.agent.calculate_bedrock_cost")
    def test_agent_with_all_features_enabled(self, mock_cost, mock_agent_class):
        # Setup mocks
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        mock_agent.return_value = self.mock_response
        mock_cost.return_value = 0.001

        # Call agent with all features enabled
        agent(
            output_path="/test/path",
            output_format="{Title} - {Author}",
            query="test query",
            enable_downloads=True,
            enable_deletions=True,
            enable_renaming=True,
        )

        # Get the tools passed to Agent constructor
        mock_agent_class.assert_called_once()
        call_args = mock_agent_class.call_args
        kwargs = call_args[1]  # Get the keyword arguments
        tools = kwargs["tools"]

        # Verify all expected tools are present
        self.assertIn(lookup_books, tools)
        self.assertIn(path_list, tools)
        self.assertIn(download_ebook, tools)
        self.assertIn(file_delete, tools)
        self.assertIn(file_move, tools)

        # Verify model is correct
        self.assertEqual(kwargs["model"], BEDROCK_NOVA_PRO_MODEL)

    @patch("book_strands.agent.Agent")
    @patch("book_strands.agent.calculate_bedrock_cost")
    def test_agent_with_all_features_disabled(self, mock_cost, mock_agent_class):
        # Setup mocks
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        mock_agent.return_value = self.mock_response
        mock_cost.return_value = 0.001

        # Call agent with all optional features disabled
        agent(
            output_path="/test/path",
            output_format="{Title} - {Author}",
            query="test query",
            enable_downloads=False,
            enable_deletions=False,
            enable_renaming=False,
        )

        # Get the tools passed to Agent constructor
        _, kwargs = mock_agent_class.call_args
        tools = kwargs["tools"]

        # Verify only base tools are present
        self.assertIn(lookup_books, tools)
        self.assertIn(path_list, tools)

        # Verify optional tools are not present
        self.assertNotIn(download_ebook, tools)
        self.assertNotIn(file_delete, tools)
        self.assertNotIn(file_move, tools)

    @patch("book_strands.agent.Agent")
    @patch("book_strands.agent.calculate_bedrock_cost")
    def test_agent_with_mixed_features(self, mock_cost, mock_agent_class):
        # Setup mocks
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        mock_agent.return_value = self.mock_response
        mock_cost.return_value = 0.001

        # Call agent with mixed features
        agent(
            output_path="/test/path",
            output_format="{Title} - {Author}",
            query="test query",
            enable_downloads=True,
            enable_deletions=False,
            enable_renaming=True,
        )

        # Get the tools passed to Agent constructor
        _, kwargs = mock_agent_class.call_args
        tools = kwargs["tools"]

        # Verify expected tools are present
        self.assertIn(lookup_books, tools)
        self.assertIn(path_list, tools)
        self.assertIn(download_ebook, tools)
        self.assertIn(file_move, tools)

        # Verify disabled tool is not present
        self.assertNotIn(file_delete, tools)
