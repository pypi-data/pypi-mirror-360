"""
Cloudflare DNS Manager

Handles DNS operations via Cloudflare API with error handling and validation.
"""

import json
from typing import Dict, Any, List, Optional
from ..cloudflare_resources.auth_service import CloudflareAuthenticationService


class DNSManager:
    """Manager for Cloudflare DNS operations"""

    def __init__(self):
        self.auth_service = CloudflareAuthenticationService

    def _get_zone_id(self, domain: str) -> str:
        """
        Get zone ID for a domain

        Args:
            domain: Domain name

        Returns:
            str: Zone ID

        Raises:
            ValueError: If zone not found
        """
        # First check if zone ID is provided in environment
        credentials = self.auth_service.get_credentials()
        if credentials.zone_id:
            return credentials.zone_id

        # Otherwise, look up the zone
        response = self.auth_service.make_request(
            'GET',
            f'zones?name={domain}'
        )

        if not response.ok:
            raise ValueError(f"Failed to find zone for domain {domain}: {response.text}")

        data = response.json()
        if not data.get('success') or not data.get('result'):
            raise ValueError(f"Zone not found for domain {domain}")

        return data['result'][0]['id']

    def create_record(self, domain: str, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a DNS record

        Args:
            domain: Domain name
            record: Record configuration

        Returns:
            Dict containing the created record info
        """
        zone_id = self._get_zone_id(domain)

        # Prepare record data for Cloudflare API
        record_data = {
            'type': record['type'],
            'name': record['name'],
            'content': record['content'],
            'ttl': record.get('ttl', 3600)
        }

        # Add proxied setting for applicable record types
        if record['type'] in ['A', 'AAAA', 'CNAME']:
            record_data['proxied'] = record.get('proxied', False)

        # Handle special record types
        if record['type'] == 'MX':
            record_data['priority'] = record.get('priority', 10)
        elif record['type'] == 'SRV':
            record_data['data'] = {
                'service': record['name'].split('.')[0] if '.' in record['name'] else record['name'],
                'proto': record['name'].split('.')[1] if '.' in record['name'] else '_tcp',
                'name': record['name'],
                'priority': record.get('priority', 0),
                'weight': record.get('weight', 5),
                'port': record['port'],
                'target': record['content']
            }
        elif record['type'] == 'CAA':
            record_data['data'] = {
                'flags': record.get('flags', 0),
                'tag': record.get('tag', 'issue'),
                'value': record.get('value', record['content'])
            }

        response = self.auth_service.make_request(
            'POST',
            f'zones/{zone_id}/dns_records',
            json=record_data
        )

        if not response.ok:
            raise Exception(f"Failed to create DNS record: {response.text}")

        result = response.json()
        if not result.get('success'):
            errors = result.get('errors', [])
            error_msg = ', '.join([error.get('message', 'Unknown error') for error in errors])
            raise Exception(f"DNS record creation failed: {error_msg}")

        return {
            'record_id': result['result']['id'],
            'type': result['result']['type'],
            'name': result['result']['name'],
            'content': result['result']['content'],
            'ttl': result['result']['ttl'],
            'proxied': result['result'].get('proxied', False),
            'created_on': result['result']['created_on']
        }

    def delete_record(self, domain: str, record_id: str) -> Dict[str, Any]:
        """
        Delete a DNS record

        Args:
            domain: Domain name
            record_id: Record ID to delete

        Returns:
            Dict containing deletion result
        """
        zone_id = self._get_zone_id(domain)

        response = self.auth_service.make_request(
            'DELETE',
            f'zones/{zone_id}/dns_records/{record_id}'
        )

        if not response.ok:
            raise Exception(f"Failed to delete DNS record: {response.text}")

        result = response.json()
        if not result.get('success'):
            errors = result.get('errors', [])
            error_msg = ', '.join([error.get('message', 'Unknown error') for error in errors])
            raise Exception(f"DNS record deletion failed: {error_msg}")

        return {
            'record_id': record_id,
            'deleted': True
        }

    def delete_domain_records(self, domain: str) -> Dict[str, Any]:
        """
        Delete all DNS records for a domain (except NS and SOA)

        Args:
            domain: Domain name

        Returns:
            Dict containing deletion results
        """
        zone_id = self._get_zone_id(domain)

        # First, list all records
        response = self.auth_service.make_request(
            'GET',
            f'zones/{zone_id}/dns_records'
        )

        if not response.ok:
            raise Exception(f"Failed to list DNS records: {response.text}")

        result = response.json()
        if not result.get('success'):
            raise Exception("Failed to list DNS records")

        # Filter out NS and SOA records (these are managed by Cloudflare)
        deletable_records = [
            record for record in result['result']
            if record['type'] not in ['NS', 'SOA']
        ]

        deleted_count = 0
        errors = []

        for record in deletable_records:
            try:
                self.delete_record(domain, record['id'])
                deleted_count += 1
            except Exception as e:
                errors.append(f"Failed to delete {record['name']} ({record['type']}): {str(e)}")

        return {
            'domain': domain,
            'total_records': len(deletable_records),
            'deleted_count': deleted_count,
            'errors': errors
        }

    def list_records(self, domain: str) -> List[Dict[str, Any]]:
        """
        List all DNS records for a domain

        Args:
            domain: Domain name

        Returns:
            List of DNS records
        """
        zone_id = self._get_zone_id(domain)

        response = self.auth_service.make_request(
            'GET',
            f'zones/{zone_id}/dns_records'
        )

        if not response.ok:
            raise Exception(f"Failed to list DNS records: {response.text}")

        result = response.json()
        if not result.get('success'):
            raise Exception("Failed to list DNS records")

        return [
            {
                'id': record['id'],
                'type': record['type'],
                'name': record['name'],
                'content': record['content'],
                'ttl': record['ttl'],
                'proxied': record.get('proxied', False),
                'created_on': record['created_on'],
                'modified_on': record['modified_on']
            }
            for record in result['result']
        ]

    def get_domain_status(self, domain: str) -> Dict[str, Any]:
        """
        Get status information for a domain

        Args:
            domain: Domain name

        Returns:
            Dict containing domain status
        """
        zone_id = self._get_zone_id(domain)

        # Get zone information
        response = self.auth_service.make_request(
            'GET',
            f'zones/{zone_id}'
        )

        if not response.ok:
            raise Exception(f"Failed to get zone status: {response.text}")

        result = response.json()
        if not result.get('success'):
            raise Exception("Failed to get zone status")

        zone_data = result['result']

        # Get DNS records count
        records = self.list_records(domain)

        return {
            'domain': domain,
            'zone_id': zone_id,
            'status': zone_data['status'],
            'name_servers': zone_data.get('name_servers', []),
            'records_count': len(records),
            'plan': zone_data.get('plan', {}).get('name', 'Unknown'),
            'created_on': zone_data['created_on'],
            'modified_on': zone_data['modified_on']
        }

    def update_record(self, domain: str, record_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a DNS record

        Args:
            domain: Domain name
            record_id: Record ID to update
            updates: Fields to update

        Returns:
            Dict containing updated record info
        """
        zone_id = self._get_zone_id(domain)

        response = self.auth_service.make_request(
            'PUT',
            f'zones/{zone_id}/dns_records/{record_id}',
            json=updates
        )

        if not response.ok:
            raise Exception(f"Failed to update DNS record: {response.text}")

        result = response.json()
        if not result.get('success'):
            errors = result.get('errors', [])
            error_msg = ', '.join([error.get('message', 'Unknown error') for error in errors])
            raise Exception(f"DNS record update failed: {error_msg}")

        return {
            'record_id': result['result']['id'],
            'type': result['result']['type'],
            'name': result['result']['name'],
            'content': result['result']['content'],
            'ttl': result['result']['ttl'],
            'proxied': result['result'].get('proxied', False),
            'modified_on': result['result']['modified_on']
        }
