class SecretsManagerConfigurationMixin:
    """
    Mixin for SecretsManager chainable configuration methods.
    """
    def secret_name(self, name: str):
        """Set the secret name"""
        return self

    def secret_type(self, secret_type: str):
        """Set the secret type (other, password, keypair, etc.)"""
        return self

    def value(self, secret_value: str):
        """Set the secret value"""
        return self

    def description(self, description: str):
        """Set the secret description"""
        return self

    def kms_key(self, kms_key_id: str):
        """Set the KMS key ID for encryption"""
        return self

    def generate_password(self, length: int, exclude_characters: str = ""):
        """Generate a random password for the secret"""
        self.password_length = length
        self.password_exclude_characters = exclude_characters
        return self

    def automatic_rotation(self, days: int):
        """Enable automatic rotation for the secret"""
        self.rotation_enabled = True
        self.rotation_days = days
        return self

    def rotation_lambda(self, lambda_arn: str):
        """Set the rotation Lambda function ARN"""
        return self

    def recovery_window(self, days: int):
        """Set the recovery window in days"""
        return self

    def tag(self, key: str, value: str):
        """Add a tag to the secret"""
        return self 