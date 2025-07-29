"""
Model manager for LLM-as-judge metrics.
"""

class ModelManager:
    """Manages different LLM providers and models."""
    
    def __init__(self):
        self.clients = {}
    
    def get_client(self, model_id: str):
        """Get client for a specific model."""
        # TODO: Implement actual model clients
        return MockModelClient(model_id)


class MockModelClient:
    """Mock model client for testing."""
    
    def __init__(self, model_id: str):
        self.model_id = model_id
    
    def generate(self, prompt: str, config=None) -> str:
        """Generate response synchronously."""
        # Mock response
        return "0.75"
    
    async def generate_async(self, prompt: str, config=None) -> str:
        """Generate response asynchronously."""
        # Mock response
        return "0.75" 