
class MockClient():
    """Mock client for testing purposes."""
    
    def __init__(self):
        self.data = {}

    def get(self, key):
        """Get a value by key."""
        return self.data.get(key, None)

    def set(self, key, value):
        """Set a value by key."""
        self.data[key] = value

    def delete(self, key):
        """Delete a value by key."""
        if key in self.data:
            del self.data[key]


mock_client = MockClient()