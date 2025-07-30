"""
PHP Dockerfile Generator

This module provides specialized Dockerfile generation for PHP applications,
with support for various frameworks and web servers.
"""

from typing import Dict, Any
from .base import BaseDockerfileGenerator


class PHPDockerfileGenerator(BaseDockerfileGenerator):
    """
    PHP Dockerfile Generator
    
    Supports:
    - Laravel, Symfony, CodeIgniter frameworks
    - Apache and Nginx web servers
    - Composer dependency management
    - Security hardening and performance optimization
    """
    
    def generate(self) -> str:
        """Generate optimized PHP Dockerfile."""
        framework = self.get_framework()
        port = self.get_port()
        web_server = self._get_web_server()
        
        # Choose base image based on web server preference
        if web_server == "nginx":
            return self._generate_nginx_dockerfile(framework, port)
        else:
            return self._generate_apache_dockerfile(framework, port)
    
    def _generate_apache_dockerfile(self, framework: str, port: int) -> str:
        """Generate PHP Dockerfile with Apache."""
        self.add_comment("PHP application with Apache")
        self.add_from("php:8.2-apache")
        self.add_blank_line()
        
        # Install system dependencies
        self._add_system_dependencies()
        
        # Install PHP extensions
        self._add_php_extensions(framework)
        
        # Install Composer
        self._add_composer_installation()
        
        # Configure Apache
        self._configure_apache()
        
        # Set working directory
        self.add_workdir("/var/www/html")
        self.add_blank_line()
        
        # Install PHP dependencies
        self._add_dependency_installation()
        
        # Copy application code
        self.add_comment("Copy application code")
        self.add_copy(". .")
        self.add_blank_line()
        
        # Framework-specific setup
        self._add_framework_setup(framework)
        
        # Set permissions and security
        self._add_security_setup()
        
        # Expose port
        self.add_expose(port)
        self.add_blank_line()
        
        # Add health check
        self._add_health_check(port)
        self.add_blank_line()
        
        # Add standard labels
        self.add_standard_labels()
        self.add_blank_line()
        
        # Start command
        self.add_cmd('["apache2-foreground"]')
        
        return self.get_content()
    
    def _generate_nginx_dockerfile(self, framework: str, port: int) -> str:
        """Generate PHP Dockerfile with Nginx + PHP-FPM."""
        # Reset content for nginx build
        self.dockerfile_content = []
        
        self.add_comment("Multi-stage build for PHP application with Nginx")
        
        # PHP-FPM stage
        self.add_from("php:8.2-fpm-alpine", platform="linux/amd64")
        self.add_label("stage", "php")
        self.add_blank_line()
        
        # Install system dependencies for Alpine
        self._add_alpine_dependencies()
        
        # Install PHP extensions
        self._add_php_extensions(framework)
        
        # Install Composer
        self._add_composer_installation()
        
        self.add_workdir("/var/www/html")
        self.add_blank_line()
        
        # Install PHP dependencies
        self._add_dependency_installation()
        
        # Copy application code
        self.add_copy(". .")
        self.add_blank_line()
        
        # Framework setup
        self._add_framework_setup(framework)
        
        # Final stage with Nginx
        self.add_comment("Final stage with Nginx")
        self.add_from("nginx:alpine")
        self.add_blank_line()
        
        # Copy PHP-FPM from previous stage
        self.add_copy("--from=php /usr/local/etc/php-fpm.d/www.conf /usr/local/etc/php-fpm.d/www.conf")
        self.add_copy("--from=php /var/www/html /var/www/html")
        self.add_blank_line()
        
        # Configure Nginx
        self._configure_nginx()
        
        # Security setup
        self._add_security_setup()
        
        # Expose port
        self.add_expose(port)
        self.add_blank_line()
        
        # Health check
        self._add_health_check(port)
        self.add_blank_line()
        
        # Standard labels
        self.add_standard_labels()
        self.add_blank_line()
        
        # Start both services
        self.add_comment("Start both PHP-FPM and Nginx")
        self.add_cmd('["sh", "-c", "php-fpm -D && nginx -g \\"daemon off;\\""]')
        
        return self.get_content()
    
    def _add_system_dependencies(self):
        """Add system dependencies for Debian-based PHP image."""
        self.add_comment("Install system dependencies")
        deps = [
            "git", "curl", "libpng-dev", "libonig-dev", "libxml2-dev",
            "zip", "unzip", "libzip-dev", "libpq-dev", "default-mysql-client"
        ]
        self.add_run("apt-get update && apt-get install -y " + " ".join(deps))
        self.add_run("apt-get clean && rm -rf /var/lib/apt/lists/*")
        self.add_blank_line()
    
    def _add_alpine_dependencies(self):
        """Add system dependencies for Alpine-based PHP image."""
        self.add_comment("Install system dependencies")
        deps = [
            "git", "curl", "libpng-dev", "oniguruma-dev", "libxml2-dev",
            "zip", "unzip", "libzip-dev", "postgresql-dev", "mysql-client"
        ]
        self.add_run("apk add --no-cache " + " ".join(deps))
        self.add_blank_line()
    
    def _add_php_extensions(self, framework: str):
        """Add PHP extensions based on framework requirements."""
        self.add_comment("Install PHP extensions")
        
        # Common extensions
        common_extensions = ["pdo_mysql", "pdo_pgsql", "mbstring", "exif", "pcntl", "bcmath", "gd", "zip"]
        
        # Framework-specific extensions
        framework_extensions = {
            "laravel": ["redis", "tokenizer"],
            "symfony": ["intl", "opcache"],
            "codeigniter": ["mysqli", "curl"]
        }
        
        extensions = common_extensions[:]
        if framework in framework_extensions:
            extensions.extend(framework_extensions[framework])
        
        self.add_run(f"docker-php-ext-install {' '.join(extensions)}")
        
        # Install additional extensions via PECL if needed
        if framework == "laravel":
            self.add_run("pecl install redis && docker-php-ext-enable redis")
        
        self.add_blank_line()
    
    def _add_composer_installation(self):
        """Add Composer installation."""
        self.add_comment("Install Composer")
        self.add_copy("--from=composer:latest /usr/bin/composer /usr/bin/composer")
        self.add_blank_line()
    
    def _add_dependency_installation(self):
        """Add Composer dependency installation."""
        self.add_comment("Install Composer dependencies")
        self.add_copy("composer.json composer.lock* ./")
        self.add_run("composer install --no-scripts --no-autoloader --no-dev --prefer-dist")
        self.add_blank_line()
    
    def _add_framework_setup(self, framework: str):
        """Add framework-specific setup commands."""
        if framework == "laravel":
            self.add_comment("Laravel-specific setup")
            self.add_run("composer dump-autoload --optimize")
            self.add_run("php artisan config:cache || true")
            self.add_run("php artisan route:cache || true")
            self.add_run("php artisan view:cache || true")
        elif framework == "symfony":
            self.add_comment("Symfony-specific setup")
            self.add_run("composer dump-autoload --optimize")
            self.add_env("APP_ENV", "prod")
            self.add_run("php bin/console cache:clear --env=prod || true")
        else:
            self.add_comment("Generate optimized autoloader")
            self.add_run("composer dump-autoload --optimize")
        
        self.add_blank_line()
    
    def _configure_apache(self):
        """Configure Apache web server."""
        self.add_comment("Configure Apache")
        self.add_run("a2enmod rewrite")
        self.add_run("a2enmod headers")
        
        # Create custom Apache configuration
        apache_config = '''<VirtualHost *:80>
    DocumentRoot /var/www/html/public
    <Directory /var/www/html/public>
        AllowOverride All
        Require all granted
    </Directory>
    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>'''
        
        self.add_run(f'echo \'{apache_config}\' > /etc/apache2/sites-available/000-default.conf')
        self.add_blank_line()
    
    def _configure_nginx(self):
        """Configure Nginx web server."""
        self.add_comment("Configure Nginx")
        
        nginx_config = '''server {
    listen 80;
    server_name _;
    root /var/www/html/public;
    index index.php index.html index.htm;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \\.php$ {
        fastcgi_pass 127.0.0.1:9000;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }

    location ~ /\\.ht {
        deny all;
    }
}'''
        
        self.add_run(f'echo \'{nginx_config}\' > /etc/nginx/conf.d/default.conf')
        self.add_blank_line()
    
    def _add_security_setup(self):
        """Add security and permission setup."""
        self.add_comment("Set permissions and security")
        self.add_run("chown -R www-data:www-data /var/www/html")
        self.add_run("chmod -R 755 /var/www/html")
        self.add_blank_line()
        
        # Switch to www-data user for security
        self.add_user("www-data")
        self.add_blank_line()
    
    def _get_web_server(self) -> str:
        """Determine preferred web server."""
        # Default to Apache, but could be configurable
        return self.project_info.get("web_server", "apache")
    
    def _add_health_check(self, port: int):
        """Add health check configuration."""
        health_test = f"curl --fail http://localhost:{port}/ || exit 1"
        self.add_healthcheck(health_test, interval="30s", timeout="10s", retries=3)
    
    def get_optimization_recommendations(self) -> Dict[str, Any]:
        """Get PHP specific optimization recommendations."""
        framework = self.get_framework()
        
        recommendations = {
            "multi_stage_build": False,  # Usually not needed for PHP
            "web_server_optimization": True,
            "opcache_enabled": True,
            "composer_optimization": True,
            "framework_optimizations": []
        }
        
        if framework == "laravel":
            recommendations["framework_optimizations"].extend([
                "Use config caching for better performance",
                "Enable route caching in production",
                "Use view caching for compiled templates",
                "Configure Redis for session/cache storage"
            ])
        elif framework == "symfony":
            recommendations["framework_optimizations"].extend([
                "Use Symfony's built-in cache system",
                "Enable OPcache for better performance",
                "Use environment-specific configurations",
                "Optimize Doctrine ORM queries"
            ])
        
        recommendations["security_recommendations"] = [
            "Run as www-data user",
            "Disable unnecessary PHP modules",
            "Configure proper file permissions",
            "Use HTTPS in production",
            "Enable security headers"
        ]
        
        recommendations["performance_tips"] = [
            "Enable OPcache in production",
            "Use Composer's optimize-autoloader",
            "Configure proper memory limits",
            "Use APCu for user cache",
            "Enable gzip compression"
        ]
        
        recommendations["web_server_options"] = {
            "apache": {
                "pros": ["Easy configuration", "Wide compatibility", ".htaccess support"],
                "cons": ["Higher memory usage", "Less efficient than Nginx"]
            },
            "nginx": {
                "pros": ["Better performance", "Lower memory usage", "Better for static files"],
                "cons": ["More complex configuration", "Requires PHP-FPM"]
            }
        }
        
        return recommendations