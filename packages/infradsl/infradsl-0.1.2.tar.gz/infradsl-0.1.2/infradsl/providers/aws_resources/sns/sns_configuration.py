class SNSConfigurationMixin:
    """
    Mixin for SNS chainable configuration methods.
    """
    def topic_name(self, name: str):
        """Set the topic name"""
        return self

    def display_name(self, display_name: str):
        """Set the display name for the topic"""
        return self

    def fifo(self, enabled: bool = True):
        """Enable or disable FIFO topic"""
        return self

    def content_based_deduplication(self, enabled: bool = True):
        """Enable or disable content-based deduplication"""
        return self

    def delivery_policy(self, policy: dict):
        """Set the delivery policy for the topic"""
        return self

    def tag(self, key: str, value: str):
        """Add a tag to the topic"""
        return self 