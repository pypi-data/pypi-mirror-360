import unittest
import os
from dotenv import load_dotenv
from pylangdb import LangDb
from user_trends_analyzer import UserTrendsAnalyzer

load_dotenv()


class TestUserTrendsAnalyzer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set environment variables for testing
        cls.api_key = os.getenv("LANGDB_API_KEY")
        cls.project_id = os.getenv("LANGDB_PROJECT_ID")

        # Skip tests if environment variables are not set
        if not all([cls.api_key, cls.project_id]):
            raise unittest.SkipTest(
                "LANGDB_API_KEY and LANGDB_PROJECT_ID environment variables are required"
            )

    def setUp(self):
        # Initialize LangDb client and UserTrendsAnalyzer
        self.client = LangDb(api_key=self.api_key, project_id=self.project_id)
        self.analyzer = UserTrendsAnalyzer(
            api_key=self.api_key, project_id=self.project_id
        )

        # Create test threads with different types of questions
        self.thread_ids = self.create_test_threads()

    def create_test_threads(self):
        """Create test threads with diverse questions for analysis"""
        test_questions = [
            # Programming questions
            "What's the best way to handle errors in Python?",
            "How do I optimize a slow SQL query?",
            "Explain the difference between REST and GraphQL.",
            # Development workflow questions
            "How to set up CI/CD pipeline with GitHub Actions?",
            "Best practices for code review process?",
            # Architecture questions
            "When should I use microservices vs monolith?",
            "How to design a scalable message queue system?",
            # Security questions
            "How to prevent SQL injection attacks?",
            "Best practices for API authentication?",
            # General questions
            "Tools for monitoring production applications?",
        ]

        thread_ids = []
        available_models = self.client.list_models()
        model = available_models[0] if available_models else "gpt-4o-mini"

        for question in test_questions:
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful programming assistant.",
                },
                {"role": "user", "content": question},
            ]

            response = self.client.completion(
                model=model, messages=messages, temperature=0.7
            )
            thread_ids.append(response["thread_id"])

        return thread_ids

    def test_analyze_thread_trends(self):
        """Test the thread trends analysis functionality"""
        # Analyze trends
        trends = self.analyzer.analyze_thread_trends(self.thread_ids)

        # Check response structure
        self.assertIsInstance(trends, dict)
        self.assertIn("analysis", trends)
        self.assertIn("thread_count", trends)
        self.assertIn("message_count", trends)
        self.assertIn("time_range", trends)

        # Verify counts
        self.assertEqual(trends["thread_count"], len(self.thread_ids))
        self.assertGreater(trends["message_count"], 0)

    def test_get_topic_distribution(self):
        """Test the topic distribution analysis"""
        # Get topic distribution
        topics = self.analyzer.get_topic_distribution(self.thread_ids)

        # Check response structure
        self.assertIsInstance(topics, dict)
        self.assertIn("topic_distribution", topics)
        self.assertIn("total_messages", topics)

        # Verify message count
        self.assertGreater(topics["total_messages"], 0)

        # Parse topic distribution (it should be a JSON string)
        topic_dist = eval(
            topics["topic_distribution"]
        )  # Using eval since we know it's safe in this case
        self.assertIsInstance(topic_dist, dict)

        # Check expected topic categories based on our test questions
        expected_categories = {"Programming", "Development", "Architecture", "Security"}
        found_categories = {key.split()[0] for key in topic_dist.keys()}
        self.assertTrue(any(cat in found_categories for cat in expected_categories))

    def test_error_handling(self):
        """Test error handling with invalid inputs"""
        # Test with empty thread list
        empty_result = self.analyzer.analyze_thread_trends([])
        self.assertIn("error", empty_result)

        # Test with invalid thread ID
        invalid_result = self.analyzer.analyze_thread_trends(["invalid_thread_id"])
        self.assertIn("error", invalid_result)

    def tearDown(self):
        """Clean up any resources after tests"""
        # Note: In a real application, you might want to delete test threads
        # but the current API doesn't support thread deletion
        pass


if __name__ == "__main__":
    unittest.main()
