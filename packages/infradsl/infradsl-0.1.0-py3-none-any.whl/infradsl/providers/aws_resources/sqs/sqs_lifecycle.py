from typing import Dict, Any, List
import uuid

class SQSLifecycleMixin:
    """
    Mixin for SQS queue lifecycle operations (create, update, destroy).
    """
    
    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        self._ensure_authenticated()
        
        # Mock discovery for now - in real implementation this would use AWS SDK
        existing_queues = {}
        
        # Determine desired state
        desired_queue_name = self.queue_name or self.name
        if self.fifo_queue and not desired_queue_name.endswith('.fifo'):
            desired_queue_name = f"{desired_queue_name}.fifo"
        
        # Categorize queues
        to_create = []
        to_keep = []
        to_remove = []
        
        # Check if our desired queue exists
        queue_exists = desired_queue_name in existing_queues
        
        if not queue_exists:
            to_create.append({
                'name': desired_queue_name,
                'queue_type': self.queue_type or 'standard',
                'fifo_queue': self.fifo_queue,
                'visibility_timeout': self.visibility_timeout_seconds or 30,
                'message_retention_period': self.message_retention_period or (4 * 24 * 60 * 60),
                'maximum_message_size': self.maximum_message_size or (256 * 1024),
                'delay_seconds': self.delay_seconds or 0,
                'receive_message_wait_time': self.receive_message_wait_time or 0,
                'dead_letter_queue_arn': self.dead_letter_queue_arn,
                'max_receive_count': self.max_receive_count,
                'content_based_deduplication': self.content_based_deduplication if self.fifo_queue else None,
                'fifo_throughput_limit': self.fifo_throughput_limit if self.fifo_queue else None,
                'deduplication_scope': self.deduplication_scope if self.fifo_queue else None,
                'kms_master_key_id': getattr(self, 'kms_master_key_id', None),
                'tags': self.tags
            })
        else:
            to_keep.append(existing_queues[desired_queue_name])
        
        self._display_preview(to_create, to_keep, to_remove)
        
        return {
            'resource_type': 'AWS SQS Queue',
            'name': desired_queue_name,
            'queue_url': f"https://sqs.us-east-1.amazonaws.com/123456789/{desired_queue_name}",  # Mock URL
            'to_create': to_create,
            'to_keep': to_keep,
            'to_remove': to_remove,
            'existing_queues': existing_queues,
            'queue_type': self.queue_type or 'standard',
            'fifo_queue': self.fifo_queue,
            'estimated_cost': self._estimate_monthly_cost()
        }
    
    def _display_preview(self, to_create: List[Dict], to_keep: List[Dict], to_remove: List[Dict]):
        """Display preview information in a clean format"""
        print(f"\n📬 SQS Queue Preview")
        
        # Show queues to create
        if to_create:
            print(f"╭─ 📨 Queues to CREATE: {len(to_create)}")
            for queue in to_create:
                print(f"├─ 🆕 {queue['name']}")
                print(f"│  ├─ 🏷️  Type: {queue['queue_type'].upper()}")
                if queue['fifo_queue']:
                    print(f"│  ├─ 🔢 FIFO: ✅ Enabled")
                    if queue['content_based_deduplication']:
                        print(f"│  │  ├─ 🔄 Content-based deduplication: ✅")
                    if queue['fifo_throughput_limit']:
                        print(f"│  │  ├─ ⚡ Throughput: {queue['fifo_throughput_limit']}")
                    if queue['deduplication_scope']:
                        print(f"│  │  └─ 📊 Deduplication scope: {queue['deduplication_scope']}")
                else:
                    print(f"│  ├─ 🔢 FIFO: ❌ Standard queue")
                
                print(f"│  ├─ ⏱️  Visibility timeout: {queue['visibility_timeout']}s")
                print(f"│  ├─ 📅 Message retention: {queue['message_retention_period'] // (24 * 60 * 60)} days")
                print(f"│  ├─ 📏 Max message size: {queue['maximum_message_size'] // 1024}KB")
                print(f"│  ├─ ⏰ Delay: {queue['delay_seconds']}s")
                print(f"│  ├─ 🔄 Long polling: {queue['receive_message_wait_time']}s")
                
                if queue['dead_letter_queue_arn']:
                    print(f"│  ├─ 💀 Dead letter queue: ✅ Configured")
                    print(f"│  │  ├─ 🎯 Target: {queue['dead_letter_queue_arn']}")
                    print(f"│  │  └─ 🔢 Max receives: {queue['max_receive_count']}")
                else:
                    print(f"│  ├─ 💀 Dead letter queue: ❌ None")
                
                if queue['kms_master_key_id']:
                    print(f"│  ├─ 🔐 Encryption: ✅ KMS ({queue['kms_master_key_id']})")
                else:
                    print(f"│  ├─ 🔐 Encryption: ❌ None")
                
                if queue['tags']:
                    print(f"│  ├─ 🏷️  Tags: {len(queue['tags'])}")
                    for key, value in list(queue['tags'].items())[:3]:
                        print(f"│  │  ├─ {key}: {value}")
                    if len(queue['tags']) > 3:
                        print(f"│  │  └─ ... and {len(queue['tags']) - 3} more")
                
                print(f"│  └─ 💰 Estimated cost: {self._estimate_monthly_cost()}/month")
            print(f"╰─")
        
        # Show queues to keep
        if to_keep:
            print(f"╭─ 🔄 Queues to KEEP: {len(to_keep)}")
            for queue in to_keep:
                print(f"├─ ✅ {queue.get('name', 'Unknown')}")
                print(f"│  ├─ 🆔 Queue URL: {queue.get('url', 'Unknown')}")
                print(f"│  ├─ 🏷️  Type: {queue.get('type', 'Unknown')}")
                print(f"│  └─ 📊 Messages: {queue.get('messages_available', 'Unknown')}")
            print(f"╰─")
        
        # Show messaging patterns and use cases
        print(f"\n📋 SQS Use Cases:")
        if to_create and to_create[0]['fifo_queue']:
            print(f"   ├─ 🔢 FIFO Queue: Order-critical applications")
            print(f"   ├─ 💳 Financial transactions, order processing")
            print(f"   └─ 📊 Deduplication prevents duplicate processing")
        else:
            print(f"   ├─ ⚡ Standard Queue: High-throughput applications")
            print(f"   ├─ 🌐 Microservices communication")
            print(f"   └─ 📈 Event-driven architectures")
    
    def _estimate_monthly_cost(self):
        """Estimate monthly costs for the SQS queue"""
        # SQS pricing (simplified estimates)
        if self.fifo_queue:
            # FIFO queues: $0.50 per million requests
            monthly_requests = 1000000  # 1M requests estimate
            cost_per_million = 0.50
        else:
            # Standard queues: $0.40 per million requests
            monthly_requests = 1000000  # 1M requests estimate
            cost_per_million = 0.40
        
        base_cost = (monthly_requests / 1000000) * cost_per_million
        
        # Add data transfer costs if applicable
        data_transfer_cost = 0.00  # First 1GB free
        
        total_cost = base_cost + data_transfer_cost
        return f"${total_cost:.2f}"
    
    def create(self) -> Dict[str, Any]:
        """Create/update SQS queue"""
        self._ensure_authenticated()
        
        desired_queue_name = self.queue_name or self.name
        if self.fifo_queue and not desired_queue_name.endswith('.fifo'):
            desired_queue_name = f"{desired_queue_name}.fifo"
        
        queue_url = f"https://sqs.us-east-1.amazonaws.com/123456789/{desired_queue_name}"
        queue_arn = f"arn:aws:sqs:us-east-1:123456789:{desired_queue_name}"
        
        print(f"\n📬 Creating SQS Queue: {desired_queue_name}")
        print(f"   🏷️  Type: {self.queue_type or 'standard'}")
        if self.fifo_queue:
            print(f"   🔢 FIFO: ✅ Enabled")
        
        try:
            # Mock creation for now - in real implementation this would use AWS SDK
            result = {
                'queue_name': desired_queue_name,
                'queue_url': queue_url,
                'queue_arn': queue_arn,
                'queue_type': self.queue_type or 'standard',
                'fifo_queue': self.fifo_queue,
                'visibility_timeout': self.visibility_timeout_seconds or 30,
                'message_retention_period': self.message_retention_period or (4 * 24 * 60 * 60),
                'maximum_message_size': self.maximum_message_size or (256 * 1024),
                'delay_seconds': self.delay_seconds or 0,
                'receive_message_wait_time': self.receive_message_wait_time or 0,
                'dead_letter_queue_arn': self.dead_letter_queue_arn,
                'max_receive_count': self.max_receive_count,
                'content_based_deduplication': self.content_based_deduplication if self.fifo_queue else None,
                'kms_master_key_id': getattr(self, 'kms_master_key_id', None),
                'tags': self.tags,
                'status': 'Available'
            }
            
            # Update instance attributes
            self.queue_url = result['queue_url']
            self.queue_arn = result['queue_arn']
            self.queue_exists = True
            
            self._display_creation_success(result)
            return result
            
        except Exception as e:
            print(f"❌ Failed to create SQS Queue: {str(e)}")
            raise
    
    def _display_creation_success(self, result: Dict[str, Any]):
        """Display creation success information"""
        print(f"✅ SQS Queue created successfully")
        print(f"   📋 Queue Name: {result['queue_name']}")
        print(f"   🔗 Queue URL: {result['queue_url']}")
        print(f"   🆔 Queue ARN: {result['queue_arn']}")
        print(f"   🏷️  Type: {result['queue_type'].upper()}")
        if result['fifo_queue']:
            print(f"   🔢 FIFO: ✅ Enabled")
        print(f"   ⏱️  Visibility timeout: {result['visibility_timeout']}s")
        print(f"   📅 Message retention: {result['message_retention_period'] // (24 * 60 * 60)} days")
        if result['dead_letter_queue_arn']:
            print(f"   💀 Dead letter queue: ✅ Configured")
        if result['kms_master_key_id']:
            print(f"   🔐 Encryption: ✅ Enabled")
        if result['tags']:
            print(f"   🏷️  Tags: {len(result['tags'])}")
        print(f"   📊 Status: {result['status']}")
    
    def destroy(self) -> Dict[str, Any]:
        """Destroy the SQS queue"""
        self._ensure_authenticated()
        
        queue_name = self.queue_name or self.name
        print(f"🗑️ Destroying SQS Queue: {queue_name}")
        
        try:
            # Mock destruction for now - in real implementation this would use AWS SDK
            result = {
                'queue_name': queue_name,
                'queue_url': self.queue_url,
                'queue_arn': self.queue_arn,
                'status': 'Deleted',
                'deleted': True
            }
            
            # Reset instance attributes
            self.queue_url = None
            self.queue_arn = None
            self.queue_exists = False
            
            print(f"✅ SQS Queue destruction completed")
            print(f"   📋 Queue Name: {result['queue_name']}")
            print(f"   📊 Status: {result['status']}")
            print(f"   ⚠️  Note: Messages in the queue are permanently lost")
            
            return result
            
        except Exception as e:
            print(f"❌ Failed to destroy SQS Queue: {str(e)}")
            raise 