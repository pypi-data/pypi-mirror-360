from typing import Dict, Any

class SecretsManagerLifecycleMixin:
    """
    Mixin for SecretsManager lifecycle operations (create, update, destroy).
    """
    def create(self) -> Dict[str, Any]:
        """Create/update secret and remove any that are no longer needed"""
        return {}

    def destroy(self) -> Dict[str, Any]:
        """Destroy the secret"""
        return {}

    def preview(self) -> Dict[str, Any]:
        """Preview the secret changes"""
        # Ensure we're authenticated
        if hasattr(self, '_ensure_authenticated'):
            self._ensure_authenticated()
            
        print(f"\n🔍 SecretsManager Preview")
        print(f"📋 Infrastructure Changes:")
        print(f"🆕 SECRETS to CREATE:  {self.name}")
        print(f"   ╭─ 🔐 {self.name}")
        print(f"   ├─ 📝 Description: {getattr(self, 'description', 'No description')}")
        print(f"   ├─ 🔄 Rotation: {getattr(self, 'rotation_enabled', False)}")
        if getattr(self, 'rotation_enabled', False):
            print(f"   ├─ 📅 Rotation Period: {getattr(self, 'rotation_days', 30)} days")
        print(f"   ├─ 🔑 KMS Key: {getattr(self, 'kms_key_id', 'aws/secretsmanager')}")
        print(f"   ├─ 🗑️  Recovery Window: {getattr(self, 'recovery_window', 30)} days")
        print(f"   ╰─ 💰 Est. Cost: $0.40/month")
        print()

        # Register for preview summary
        try:
            from ....cli.commands import register_preview_resource
            register_preview_resource(
                provider='aws',
                resource_type='secrets_manager',
                name=self.name,
                details=[
                    f"Rotation: {getattr(self, 'rotation_enabled', False)}",
                    f"Recovery: {getattr(self, 'recovery_window', 30)} days",
                    f"Cost: $0.40/month"
                ]
            )
        except ImportError:
            pass  # CLI module not available

        return {
            "resource_type": "aws_secrets_manager",
            "secret_name": self.name,
            "description": getattr(self, 'description', 'No description'),
            "rotation_enabled": getattr(self, 'rotation_enabled', False),
            "rotation_days": getattr(self, 'rotation_days', 30),
            "kms_key_id": getattr(self, 'kms_key_id', 'aws/secretsmanager'),
            "recovery_window": getattr(self, 'recovery_window', 30),
            "estimated_cost": "$0.40/month"
        } 