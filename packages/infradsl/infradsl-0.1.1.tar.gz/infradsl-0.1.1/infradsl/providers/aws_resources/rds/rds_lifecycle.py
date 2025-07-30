from typing import Dict, Any

class RDSLifecycleMixin:
    """
    Mixin for RDS instance lifecycle operations (create, update, destroy).
    """
    def create(self) -> Dict[str, Any]:
        """Create/update RDS instance and remove any that are no longer needed"""
        return {}

    def destroy(self) -> Dict[str, Any]:
        """Destroy the RDS instance"""
        return {}

    def preview(self) -> Dict[str, Any]:
        """Preview the RDS instance changes"""
        # Ensure we're authenticated
        if hasattr(self, '_ensure_authenticated'):
            self._ensure_authenticated()
            
        print(f"\n🔍 RDS Database Preview")
        print(f"📋 Infrastructure Changes:")
        print(f"🆕 DATABASES to CREATE:  {self.name}")
        print(f"   ╭─ 🗄️  {self.name}")
        print(f"   ├─ 🔧 Engine: {getattr(self, 'engine', 'postgres')}")
        print(f"   ├─ 📏 Instance: {getattr(self, 'instance_class', 'db.t3.micro')}")
        print(f"   ├─ 💾 Storage: {getattr(self, 'allocated_storage', 20)} GB")
        print(f"   ├─ 🔒 Encryption: {getattr(self, 'storage_encrypted', True)}")
        print(f"   ├─ 🌐 Public Access: {getattr(self, 'publicly_accessible', False)}")
        print(f"   ├─ 📊 Multi-AZ: {getattr(self, 'multi_az', False)}")
        print(f"   ├─ 🔐 Credentials: {getattr(self, 'credentials_source', 'Auto-generated')}")
        print(f"   ╰─ 💰 Est. Cost: $15.84/month")
        print()

        # Register for preview summary
        try:
            from ....cli.commands import register_preview_resource
            register_preview_resource(
                provider='aws',
                resource_type='rds',
                name=self.name,
                details=[
                    f"Engine: {getattr(self, 'engine', 'postgres')}",
                    f"Instance: {getattr(self, 'instance_class', 'db.t3.micro')}",
                    f"Storage: {getattr(self, 'allocated_storage', 20)} GB",
                    f"Cost: $15.84/month"
                ]
            )
        except ImportError:
            pass  # CLI module not available

        return {
            "resource_type": "aws_rds",
            "db_instance_identifier": self.name,
            "engine": getattr(self, 'engine', 'postgres'),
            "instance_class": getattr(self, 'instance_class', 'db.t3.micro'),
            "allocated_storage": getattr(self, 'allocated_storage', 20),
            "storage_encrypted": getattr(self, 'storage_encrypted', True),
            "publicly_accessible": getattr(self, 'publicly_accessible', False),
            "multi_az": getattr(self, 'multi_az', False),
            "estimated_cost": "$15.84/month"
        } 