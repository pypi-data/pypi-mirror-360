"""
AWS RDS Manager

Manages AWS RDS database operations with Rails-like conventions.
Provides high-level abstractions for database instance management.
"""

from typing import Dict, Any, List, Optional
import boto3
from botocore.exceptions import ClientError
from ..aws_client import AwsClient


class RDSManager:
    """Manages AWS RDS database instances with Rails conventions"""

    def __init__(self, aws_client: Optional[AwsClient] = None):
        """
        Initialize RDS Manager.

        Args:
            aws_client: AWS client for authentication
        """
        self.aws_client = aws_client or AwsClient()

    def _ensure_authenticated(self):
        """Ensure AWS authentication"""
        if not self.aws_client.is_authenticated:
            self.aws_client.authenticate(silent=True)

    def get_client(self, region: Optional[str] = None):
        """Get RDS client"""
        self._ensure_authenticated()
        return self.aws_client.get_client('rds', region)

    def create_database(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new RDS database instance.

        Args:
            config: Database configuration parameters

        Returns:
            Dict containing database instance information
        """
        try:
            client = self.get_client()

            # Remove None values from config
            create_params = {k: v for k, v in config.items() if v is not None}

            # Create the database instance
            response = client.create_db_instance(**create_params)

            db_instance = response['DBInstance']

            return {
                'db_instance_identifier': db_instance['DBInstanceIdentifier'],
                'engine': db_instance['Engine'],
                'engine_version': db_instance['EngineVersion'],
                'instance_class': db_instance['DBInstanceClass'],
                'allocated_storage': db_instance['AllocatedStorage'],
                'storage_encrypted': db_instance.get('StorageEncrypted', False),
                'master_username': db_instance['MasterUsername'],
                'database_name': db_instance.get('DBName'),
                'port': db_instance.get('DbInstancePort', db_instance.get('Port')),
                'endpoint_address': db_instance.get('Endpoint', {}).get('Address'),
                'endpoint_port': db_instance.get('Endpoint', {}).get('Port'),
                'availability_zone': db_instance.get('AvailabilityZone'),
                'multi_az': db_instance.get('MultiAZ', False),
                'publicly_accessible': db_instance.get('PubliclyAccessible', False),
                'status': db_instance['DBInstanceStatus'],
                'backup_retention_period': db_instance.get('BackupRetentionPeriod', 0),
                'deletion_protection': db_instance.get('DeletionProtection', False),
                'created': True
            }

        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']

            if error_code == 'DBInstanceAlreadyExists':
                print(f"⚠️  Database instance already exists: {config['DBInstanceIdentifier']}")
                return self.get_database_info(config['DBInstanceIdentifier'])
            else:
                print(f"❌ Failed to create database: {error_message}")
                raise
        except Exception as e:
            print(f"❌ Unexpected error creating database: {str(e)}")
            raise

    def get_database_info(self, db_instance_identifier: str) -> Dict[str, Any]:
        """
        Get information about an existing database instance.

        Args:
            db_instance_identifier: Database instance identifier

        Returns:
            Dict containing database instance information
        """
        try:
            client = self.get_client()

            response = client.describe_db_instances(
                DBInstanceIdentifier=db_instance_identifier
            )

            if not response['DBInstances']:
                return {}

            db_instance = response['DBInstances'][0]

            return {
                'db_instance_identifier': db_instance['DBInstanceIdentifier'],
                'engine': db_instance['Engine'],
                'engine_version': db_instance['EngineVersion'],
                'instance_class': db_instance['DBInstanceClass'],
                'allocated_storage': db_instance['AllocatedStorage'],
                'storage_encrypted': db_instance.get('StorageEncrypted', False),
                'master_username': db_instance['MasterUsername'],
                'database_name': db_instance.get('DBName'),
                'port': db_instance.get('DbInstancePort', db_instance.get('Port')),
                'endpoint_address': db_instance.get('Endpoint', {}).get('Address'),
                'endpoint_port': db_instance.get('Endpoint', {}).get('Port'),
                'availability_zone': db_instance.get('AvailabilityZone'),
                'multi_az': db_instance.get('MultiAZ', False),
                'publicly_accessible': db_instance.get('PubliclyAccessible', False),
                'status': db_instance['DBInstanceStatus'],
                'backup_retention_period': db_instance.get('BackupRetentionPeriod', 0),
                'deletion_protection': db_instance.get('DeletionProtection', False),
                'exists': True
            }

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'DBInstanceNotFoundFault':
                return {'exists': False}
            else:
                print(f"❌ Error getting database info: {e.response['Error']['Message']}")
                raise
        except Exception as e:
            print(f"❌ Unexpected error getting database info: {str(e)}")
            raise

    def delete_database(self, db_instance_identifier: str, skip_final_snapshot: bool = True,
                       final_db_snapshot_identifier: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete a database instance.

        Args:
            db_instance_identifier: Database instance identifier
            skip_final_snapshot: Whether to skip final snapshot
            final_db_snapshot_identifier: Final snapshot identifier if not skipping

        Returns:
            Dict containing deletion result
        """
        try:
            client = self.get_client()

            delete_params = {
                'DBInstanceIdentifier': db_instance_identifier,
                'SkipFinalSnapshot': skip_final_snapshot
            }

            if not skip_final_snapshot and final_db_snapshot_identifier:
                delete_params['FinalDBSnapshotIdentifier'] = final_db_snapshot_identifier

            response = client.delete_db_instance(**delete_params)

            return {
                'db_instance_identifier': db_instance_identifier,
                'status': 'deleting',
                'deleted': True
            }

        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']

            if error_code == 'DBInstanceNotFoundFault':
                print(f"⚠️  Database instance not found: {db_instance_identifier}")
                return {'db_instance_identifier': db_instance_identifier, 'deleted': False}
            elif error_code == 'InvalidDBInstanceState':
                print(f"⚠️  Database instance in invalid state for deletion: {error_message}")
                return {'db_instance_identifier': db_instance_identifier, 'deleted': False}
            else:
                print(f"❌ Failed to delete database: {error_message}")
                raise
        except Exception as e:
            print(f"❌ Unexpected error deleting database: {str(e)}")
            raise

    def wait_for_database_available(self, db_instance_identifier: str, timeout: int = 1200) -> bool:
        """
        Wait for database to become available.

        Args:
            db_instance_identifier: Database instance identifier
            timeout: Maximum wait time in seconds

        Returns:
            True if database becomes available, False if timeout
        """
        try:
            client = self.get_client()

            waiter = client.get_waiter('db_instance_available')
            waiter.wait(
                DBInstanceIdentifier=db_instance_identifier,
                WaiterConfig={
                    'Delay': 30,
                    'MaxAttempts': timeout // 30
                }
            )
            return True

        except Exception as e:
            print(f"❌ Error waiting for database to become available: {str(e)}")
            return False

    def get_database_status(self, db_instance_identifier: str) -> str:
        """
        Get the current status of a database instance.

        Args:
            db_instance_identifier: Database instance identifier

        Returns:
            Current database status
        """
        try:
            db_info = self.get_database_info(db_instance_identifier)
            return db_info.get('status', 'unknown')
        except Exception:
            return 'unknown'

    def list_databases(self, max_records: int = 100) -> List[Dict[str, Any]]:
        """
        List all database instances.

        Args:
            max_records: Maximum number of records to return

        Returns:
            List of database instance information
        """
        try:
            client = self.get_client()

            response = client.describe_db_instances(MaxRecords=max_records)

            databases = []
            for db_instance in response['DBInstances']:
                databases.append({
                    'db_instance_identifier': db_instance['DBInstanceIdentifier'],
                    'engine': db_instance['Engine'],
                    'engine_version': db_instance['EngineVersion'],
                    'instance_class': db_instance['DBInstanceClass'],
                    'status': db_instance['DBInstanceStatus'],
                    'endpoint_address': db_instance.get('Endpoint', {}).get('Address'),
                    'port': db_instance.get('Endpoint', {}).get('Port'),
                    'multi_az': db_instance.get('MultiAZ', False),
                    'publicly_accessible': db_instance.get('PubliclyAccessible', False)
                })

            return databases

        except Exception as e:
            print(f"❌ Error listing databases: {str(e)}")
            return []

    def create_snapshot(self, db_instance_identifier: str,
                       snapshot_identifier: str) -> Dict[str, Any]:
        """
        Create a snapshot of a database instance.

        Args:
            db_instance_identifier: Database instance identifier
            snapshot_identifier: Snapshot identifier

        Returns:
            Dict containing snapshot information
        """
        try:
            client = self.get_client()

            response = client.create_db_snapshot(
                DBSnapshotIdentifier=snapshot_identifier,
                DBInstanceIdentifier=db_instance_identifier
            )

            snapshot = response['DBSnapshot']

            return {
                'snapshot_identifier': snapshot['DBSnapshotIdentifier'],
                'db_instance_identifier': snapshot['DBInstanceIdentifier'],
                'status': snapshot['Status'],
                'created': True
            }

        except ClientError as e:
            print(f"❌ Failed to create snapshot: {e.response['Error']['Message']}")
            raise
        except Exception as e:
            print(f"❌ Unexpected error creating snapshot: {str(e)}")
            raise
