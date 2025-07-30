"""
Cloudflare CDN Manager

Handles CDN operations via Cloudflare API with error handling and validation.
"""

import json
from typing import Dict, Any, List, Optional
from ..cloudflare_resources.auth_service import CloudflareAuthenticationService


class CDNManager:
    """Manager for Cloudflare CDN operations"""

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

    def update_cache_settings(self, domain: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update cache settings for a domain

        Args:
            domain: Domain name
            settings: Cache settings to update

        Returns:
            Dict containing the updated settings
        """
        zone_id = self._get_zone_id(domain)
        results = {}

        # Map of setting names to Cloudflare API setting IDs
        setting_map = {
            'cache_level': 'cache_level',
            'browser_cache_ttl': 'browser_cache_ttl',
            'edge_cache_ttl': 'edge_cache_ttl',
            'development_mode': 'development_mode',
            'always_online': 'always_online'
        }

        for setting_name, value in settings.items():
            if setting_name in setting_map:
                cf_setting = setting_map[setting_name]

                response = self.auth_service.make_request(
                    'PATCH',
                    f'zones/{zone_id}/settings/{cf_setting}',
                    json={'value': value}
                )

                if not response.ok:
                    raise Exception(f"Failed to update {setting_name}: {response.text}")

                result = response.json()
                if not result.get('success'):
                    errors = result.get('errors', [])
                    error_msg = ', '.join([error.get('message', 'Unknown error') for error in errors])
                    raise Exception(f"Failed to update {setting_name}: {error_msg}")

                results[setting_name] = {
                    'setting': cf_setting,
                    'value': result['result']['value'],
                    'modified_on': result['result']['modified_on']
                }

        return results

    def create_page_rule(self, domain: str, url_pattern: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a page rule

        Args:
            domain: Domain name
            url_pattern: URL pattern for the rule
            settings: Page rule settings

        Returns:
            Dict containing the created page rule info
        """
        zone_id = self._get_zone_id(domain)

        # Convert settings to Cloudflare format
        actions = []
        for setting, value in settings.items():
            if setting == 'cache_level':
                actions.append({'id': 'cache_level', 'value': value})
            elif setting == 'edge_cache_ttl':
                actions.append({'id': 'edge_cache_ttl', 'value': value})
            elif setting == 'browser_cache_ttl':
                actions.append({'id': 'browser_cache_ttl', 'value': value})
            elif setting == 'security_level':
                actions.append({'id': 'security_level', 'value': value})
            elif setting == 'ssl':
                actions.append({'id': 'ssl', 'value': value})
            elif setting == 'rocket_loader':
                actions.append({'id': 'rocket_loader', 'value': value})
            elif setting == 'mirage':
                actions.append({'id': 'mirage', 'value': value})

        rule_data = {
            'targets': [
                {
                    'target': 'url',
                    'constraint': {
                        'operator': 'matches',
                        'value': url_pattern
                    }
                }
            ],
            'actions': actions,
            'priority': 1,
            'status': 'active'
        }

        response = self.auth_service.make_request(
            'POST',
            f'zones/{zone_id}/pagerules',
            json=rule_data
        )

        if not response.ok:
            raise Exception(f"Failed to create page rule: {response.text}")

        result = response.json()
        if not result.get('success'):
            errors = result.get('errors', [])
            error_msg = ', '.join([error.get('message', 'Unknown error') for error in errors])
            raise Exception(f"Page rule creation failed: {error_msg}")

        return {
            'rule_id': result['result']['id'],
            'url_pattern': url_pattern,
            'actions': actions,
            'status': result['result']['status'],
            'created_on': result['result']['created_on']
        }

    def update_minification_settings(self, domain: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update minification settings

        Args:
            domain: Domain name
            settings: Minification settings (css, js, html)

        Returns:
            Dict containing updated minification settings
        """
        zone_id = self._get_zone_id(domain)

        minify_value = {
            'css': settings.get('css', 'off'),
            'html': settings.get('html', 'off'),
            'js': settings.get('js', 'off')
        }

        response = self.auth_service.make_request(
            'PATCH',
            f'zones/{zone_id}/settings/minify',
            json={'value': minify_value}
        )

        if not response.ok:
            raise Exception(f"Failed to update minification settings: {response.text}")

        result = response.json()
        if not result.get('success'):
            errors = result.get('errors', [])
            error_msg = ', '.join([error.get('message', 'Unknown error') for error in errors])
            raise Exception(f"Minification update failed: {error_msg}")

        return {
            'minification': result['result']['value'],
            'modified_on': result['result']['modified_on']
        }

    def update_cache_key_settings(self, domain: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update cache key settings

        Args:
            domain: Domain name
            settings: Cache key settings

        Returns:
            Dict containing updated cache key settings
        """
        zone_id = self._get_zone_id(domain)
        results = {}

        # Handle cache key include fields
        if 'include' in settings:
            cache_key_data = {
                'include': settings['include']
            }

            if 'ignore_query_strings' in settings:
                cache_key_data['ignore_query_strings'] = settings['ignore_query_strings']

            # Note: This requires a Cloudflare Enterprise plan
            # For other plans, this will be stored but may not be applied
            response = self.auth_service.make_request(
                'PUT',
                f'zones/{zone_id}/cache/cache_key',
                json=cache_key_data
            )

            if response.ok:
                result = response.json()
                if result.get('success'):
                    results['cache_key'] = result['result']
                else:
                    # Store the attempted configuration even if it fails
                    results['cache_key'] = {
                        'attempted': cache_key_data,
                        'note': 'Cache key customization requires Enterprise plan'
                    }
            else:
                results['cache_key'] = {
                    'attempted': cache_key_data,
                    'error': response.text,
                    'note': 'Cache key customization may require Enterprise plan'
                }

        return results

    def update_ssl_settings(self, domain: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update SSL settings

        Args:
            domain: Domain name
            settings: SSL settings

        Returns:
            Dict containing updated SSL settings
        """
        zone_id = self._get_zone_id(domain)
        results = {}

        # Update SSL mode
        if 'mode' in settings:
            response = self.auth_service.make_request(
                'PATCH',
                f'zones/{zone_id}/settings/ssl',
                json={'value': settings['mode']}
            )

            if not response.ok:
                raise Exception(f"Failed to update SSL mode: {response.text}")

            result = response.json()
            if not result.get('success'):
                errors = result.get('errors', [])
                error_msg = ', '.join([error.get('message', 'Unknown error') for error in errors])
                raise Exception(f"SSL mode update failed: {error_msg}")

            results['ssl_mode'] = {
                'value': result['result']['value'],
                'modified_on': result['result']['modified_on']
            }

        # Update HSTS settings
        if 'hsts' in settings:
            hsts_config = settings['hsts']
            hsts_value = {
                'enabled': hsts_config.get('enabled', False),
                'max_age': hsts_config.get('max_age', 31536000),
                'include_subdomains': hsts_config.get('include_subdomains', False),
                'nosniff': True
            }

            response = self.auth_service.make_request(
                'PATCH',
                f'zones/{zone_id}/settings/security_header',
                json={'value': hsts_value}
            )

            if not response.ok:
                raise Exception(f"Failed to update HSTS settings: {response.text}")

            result = response.json()
            if not result.get('success'):
                errors = result.get('errors', [])
                error_msg = ', '.join([error.get('message', 'Unknown error') for error in errors])
                raise Exception(f"HSTS update failed: {error_msg}")

            results['hsts'] = {
                'value': result['result']['value'],
                'modified_on': result['result']['modified_on']
            }

        return results

    def reset_cdn_settings(self, domain: str) -> Dict[str, Any]:
        """
        Reset CDN settings to defaults

        Args:
            domain: Domain name

        Returns:
            Dict containing reset results
        """
        zone_id = self._get_zone_id(domain)

        # Default settings to reset to
        default_settings = {
            'cache_level': 'aggressive',
            'browser_cache_ttl': 14400,
            'development_mode': 'off',
            'always_online': 'on'
        }

        results = {}
        for setting, default_value in default_settings.items():
            try:
                response = self.auth_service.make_request(
                    'PATCH',
                    f'zones/{zone_id}/settings/{setting}',
                    json={'value': default_value}
                )

                if response.ok:
                    result = response.json()
                    if result.get('success'):
                        results[setting] = 'reset'
                    else:
                        results[setting] = 'failed'
                else:
                    results[setting] = 'failed'
            except Exception:
                results[setting] = 'failed'

        # Delete all page rules
        try:
            page_rules_response = self.auth_service.make_request(
                'GET',
                f'zones/{zone_id}/pagerules'
            )

            if page_rules_response.ok:
                page_rules_data = page_rules_response.json()
                if page_rules_data.get('success'):
                    deleted_rules = 0
                    for rule in page_rules_data.get('result', []):
                        delete_response = self.auth_service.make_request(
                            'DELETE',
                            f'zones/{zone_id}/pagerules/{rule["id"]}'
                        )
                        if delete_response.ok:
                            deleted_rules += 1

                    results['page_rules_deleted'] = deleted_rules
        except Exception:
            results['page_rules_deleted'] = 'failed'

        return {
            'domain': domain,
            'reset_results': results
        }

    def get_cdn_status(self, domain: str) -> Dict[str, Any]:
        """
        Get current CDN status and settings

        Args:
            domain: Domain name

        Returns:
            Dict containing CDN status
        """
        zone_id = self._get_zone_id(domain)

        # Get zone settings
        response = self.auth_service.make_request(
            'GET',
            f'zones/{zone_id}/settings'
        )

        if not response.ok:
            raise Exception(f"Failed to get zone settings: {response.text}")

        result = response.json()
        if not result.get('success'):
            raise Exception("Failed to get zone settings")

        settings = {}
        for setting in result['result']:
            settings[setting['id']] = {
                'value': setting['value'],
                'modified_on': setting.get('modified_on')
            }

        # Get page rules
        page_rules_response = self.auth_service.make_request(
            'GET',
            f'zones/{zone_id}/pagerules'
        )

        page_rules = []
        if page_rules_response.ok:
            page_rules_data = page_rules_response.json()
            if page_rules_data.get('success'):
                page_rules = [
                    {
                        'id': rule['id'],
                        'targets': rule['targets'],
                        'actions': rule['actions'],
                        'status': rule['status']
                    }
                    for rule in page_rules_data.get('result', [])
                ]

        return {
            'domain': domain,
            'zone_id': zone_id,
            'settings': settings,
            'page_rules': page_rules,
            'page_rules_count': len(page_rules)
        }

    def purge_cache(self, domain: str, files: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Purge cache for domain

        Args:
            domain: Domain name
            files: Optional list of specific files to purge

        Returns:
            Dict containing purge results
        """
        zone_id = self._get_zone_id(domain)

        if files:
            # Purge specific files
            purge_data = {'files': files}
        else:
            # Purge everything
            purge_data = {'purge_everything': True}

        response = self.auth_service.make_request(
            'POST',
            f'zones/{zone_id}/purge_cache',
            json=purge_data
        )

        if not response.ok:
            raise Exception(f"Failed to purge cache: {response.text}")

        result = response.json()
        if not result.get('success'):
            errors = result.get('errors', [])
            error_msg = ', '.join([error.get('message', 'Unknown error') for error in errors])
            raise Exception(f"Cache purge failed: {error_msg}")

        return {
            'domain': domain,
            'purge_type': 'specific_files' if files else 'everything',
            'files': files if files else 'all',
            'purge_id': result['result'].get('id')
        }

    def get_analytics(self, domain: str, days: int = 7) -> Dict[str, Any]:
        """
        Get analytics data for the domain

        Args:
            domain: Domain name
            days: Number of days of data

        Returns:
            Dict containing analytics data
        """
        zone_id = self._get_zone_id(domain)

        # Calculate date range
        from datetime import datetime, timedelta
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        params = {
            'since': start_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'until': end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        }

        response = self.auth_service.make_request(
            'GET',
            f'zones/{zone_id}/analytics/dashboard',
            params=params
        )

        if not response.ok:
            raise Exception(f"Failed to get analytics: {response.text}")

        result = response.json()
        if not result.get('success'):
            raise Exception("Failed to get analytics data")

        analytics_data = result['result']

        return {
            'domain': domain,
            'period_days': days,
            'requests': analytics_data.get('totals', {}).get('requests', {}).get('all', 0),
            'bandwidth': analytics_data.get('totals', {}).get('bandwidth', {}).get('all', 0),
            'cached_requests': analytics_data.get('totals', {}).get('requests', {}).get('cached', 0),
            'cache_hit_ratio': analytics_data.get('totals', {}).get('requests', {}).get('cache_hit_ratio', 0),
            'threats': analytics_data.get('totals', {}).get('threats', {}).get('all', 0),
            'uniques': analytics_data.get('uniques', {}).get('all', 0)
        }
