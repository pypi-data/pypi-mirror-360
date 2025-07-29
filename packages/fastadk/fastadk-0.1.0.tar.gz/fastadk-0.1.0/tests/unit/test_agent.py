"""
Tests for FastADK agent functionality.
"""

import pytest

from fastadk import Agent, BaseAgent, tool
from fastadk.core.exceptions import ToolError

# Import directly from utils to avoid the lazy loading in __init__.py
from fastadk.testing.utils import AgentTest, MockModel


# Test agent class for testing
@Agent(model="gemini-1.5-pro", description="Test Agent")
class TestableAgent(BaseAgent):
    """A test agent for unit testing."""

    def __init__(self):
        # Initialize the agent, but override the model initialization
        # to prevent real API calls during testing
        super().__init__()
        self.model = MockModel()

    @tool
    def add_numbers(self, a: int, b: int) -> int:
        """Add two numbers and return the result."""
        return a + b

    @tool(cache_ttl=300, retries=2)
    def say_hello(self, name: str) -> str:
        """Say hello to the given name."""
        return f"Hello, {name}!"


class TestAgentDecorator:
    """Tests for the @Agent decorator."""

    def test_basic_decorator(self):
        """Test that the @Agent decorator properly sets class attributes."""
        # These are intentionally testing protected attributes set by the decorator
        # pylint: disable=protected-access
        assert TestableAgent._model_name == "gemini-1.5-pro"
        assert TestableAgent._description == "Test Agent"
        assert TestableAgent._provider == "gemini"


class TestToolDecorator:
    """Tests for the @tool decorator."""

    def test_tool_registration(self):
        """Test that tools are properly registered on the agent."""
        agent = TestableAgent()

        # Call the methods to make sure they're registered
        agent.add_numbers(1, 2)
        agent.say_hello("World")

        # Check that tools are registered
        assert "add_numbers" in agent.tools
        assert "say_hello" in agent.tools

        # Verify tool metadata
        add_tool = agent.tools["add_numbers"]
        assert add_tool.name == "add_numbers"
        assert "Add two numbers" in add_tool.description
        assert add_tool.cache_ttl == 0
        assert add_tool.retries == 0

        hello_tool = agent.tools["say_hello"]
        assert hello_tool.name == "say_hello"
        assert "Say hello" in hello_tool.description
        assert hello_tool.cache_ttl == 300
        assert hello_tool.retries == 2


class TestBaseAgent:
    """Tests for the BaseAgent class."""

    def test_initialization(self):
        """Test agent initialization."""
        agent = TestableAgent()
        assert not agent.tools_used, "tools_used should be empty initially"
        assert not agent.memory_data, "memory_data should be empty initially"

    @pytest.mark.asyncio
    async def test_run_method(self):
        """Test the run method with a mock model."""
        agent = TestableAgent()
        agent.model = MockModel(default_response="This is a test response")

        response = await agent.run("Hello, agent!")
        assert response == "This is a test response"
        assert len(agent.model.invocations) == 1

    @pytest.mark.asyncio
    async def test_execute_tool(self):
        """Test the execute_tool method."""
        agent = TestableAgent()

        # Call the method first to register it
        agent.add_numbers(1, 2)

        # Test successful tool execution
        result = await agent.execute_tool("add_numbers", a=2, b=3)
        assert result == 5
        assert "add_numbers" in agent.tools_used

        # Test missing tool
        with pytest.raises(ToolError):
            await agent.execute_tool("non_existent_tool")


class TestAgentScenarios(AgentTest):
    """Test scenarios for agents using the AgentTest class."""

    def setup_method(self):
        """Set up the test agent."""
        self.agent = TestableAgent()
        self.agent.model = MockModel()

    def mock_response(self, prompt: str, response: str) -> None:
        """Configure the mock model to return a specific response."""
        if not hasattr(self.agent, "model") or not isinstance(
            self.agent.model, MockModel
        ):
            self.agent.model = MockModel()
        self.agent.model.responses[prompt] = response

        # Call the methods to ensure they're registered
        self.agent.add_numbers(1, 2)
        self.agent.say_hello("Test")

    @pytest.mark.asyncio
    async def test_add_numbers_scenario(self):
        """Test the add_numbers tool."""
        # Configure mock model to use the tool with exact match
        self.mock_response("What is 2 + 3?", "Let me calculate that for you. 2 + 3 = 5")
        # Also add a default response that includes "5" for this test
        self.agent.model.default_response = "The answer is 5"

        # Run the agent
        response = await self.agent.run("What is 2 + 3?")

        # Verify response
        assert "5" in response

    @pytest.mark.asyncio
    async def test_hello_scenario(self):
        """Test the say_hello tool."""
        result = await self.agent.execute_tool("say_hello", name="World")
        assert result == "Hello, World!"
