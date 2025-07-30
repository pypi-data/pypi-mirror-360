class SNSLifecycleMixin:
    """
    Mixin for SNS topic lifecycle operations (create, update, destroy).
    """
    def create(self):
        """Create/update topic and remove any that are no longer needed"""
        pass

    def destroy(self):
        """Destroy the topic"""
        pass 