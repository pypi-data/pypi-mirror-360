"""
Cloudflare Pages Resource

Rails-like interface for managing Cloudflare Pages static site hosting.
Provides chainable methods for easy deployment and configuration.
"""

from typing import Dict, Any, Optional, List
from .base_resource import BaseCloudflareResource
from ..cloudflare_managers.pages_manager import PagesManager


class Pages(BaseCloudflareResource):
    """
    Cloudflare Pages resource with Rails-like simplicity.

    Examples:
        # GitHub integration
        site = (Cloudflare.Pages("my-website")
                .github_repo("myorg/website")
                .build_command("npm run build")
                .output_dir("dist")
                .create())

        # Direct upload
        upload = (Cloudflare.Pages("portfolio")
                  .upload_directory("./build")
                  .custom_domain("portfolio.myapp.com")
                  .create())

        # Framework-specific deployment
        nextjs = (Cloudflare.Pages("nextjs-app")
                  .nextjs_app("myorg/nextjs-app")
                  .create())
    """

    def __init__(self, project_name: str):
        """
        Initialize Pages resource for a project

        Args:
            project_name: The name of the Pages project
        """
        super().__init__(project_name)
        self.project_name = project_name
        self._deployment_type = "github"  # Default deployment type
        self._repo_url = None
        self._branch = "main"
        self._build_command = None
        self._output_dir = None
        self._root_dir = None
        self._environment_variables = {}
        self._custom_domains = []
        self._redirect_rules = []
        self._header_rules = []
        self._framework = None

    def _initialize_managers(self):
        """Initialize Pages-specific managers"""
        self.pages_manager = None  # Will be initialized after authentication

    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        self.pages_manager = PagesManager()

    def github_repo(self, repo_url: str, branch: str = "main") -> 'Pages':
        """
        Configure GitHub repository deployment

        Args:
            repo_url: GitHub repository URL (e.g., "owner/repo")
            branch: Branch to deploy from

        Returns:
            Pages: Self for method chaining
        """
        self._deployment_type = "github"
        self._repo_url = repo_url
        self._branch = branch
        return self

    def gitlab_repo(self, repo_url: str, branch: str = "main") -> 'Pages':
        """
        Configure GitLab repository deployment

        Args:
            repo_url: GitLab repository URL
            branch: Branch to deploy from

        Returns:
            Pages: Self for method chaining
        """
        self._deployment_type = "gitlab"
        self._repo_url = repo_url
        self._branch = branch
        return self

    def upload_directory(self, directory: str) -> 'Pages':
        """
        Configure direct directory upload

        Args:
            directory: Local directory to upload

        Returns:
            Pages: Self for method chaining
        """
        self._deployment_type = "upload"
        self._upload_directory = directory
        return self

    def build_command(self, command: str) -> 'Pages':
        """
        Set build command for the project

        Args:
            command: Build command to execute

        Returns:
            Pages: Self for method chaining
        """
        self._build_command = command
        return self

    def output_dir(self, directory: str) -> 'Pages':
        """
        Set output directory for built files

        Args:
            directory: Output directory path

        Returns:
            Pages: Self for method chaining
        """
        self._output_dir = directory
        return self

    def root_dir(self, directory: str) -> 'Pages':
        """
        Set root directory for the project

        Args:
            directory: Root directory path

        Returns:
            Pages: Self for method chaining
        """
        self._root_dir = directory
        return self

    def environment_variable(self, key: str, value: str) -> 'Pages':
        """
        Add environment variable for build process

        Args:
            key: Environment variable name
            value: Environment variable value

        Returns:
            Pages: Self for method chaining
        """
        self._environment_variables[key] = value
        return self

    def environment_variables(self, variables: Dict[str, str]) -> 'Pages':
        """
        Set multiple environment variables

        Args:
            variables: Dictionary of environment variables

        Returns:
            Pages: Self for method chaining
        """
        self._environment_variables.update(variables)
        return self

    def custom_domain(self, domain: str) -> 'Pages':
        """
        Add custom domain for the site

        Args:
            domain: Custom domain name

        Returns:
            Pages: Self for method chaining
        """
        self._custom_domains.append(domain)
        return self

    def redirect_rule(self, from_path: str, to_path: str, status_code: int = 301) -> 'Pages':
        """
        Add redirect rule

        Args:
            from_path: Source path
            to_path: Destination path
            status_code: HTTP status code

        Returns:
            Pages: Self for method chaining
        """
        self._redirect_rules.append({
            "from": from_path,
            "to": to_path,
            "status": status_code
        })
        return self

    def header_rule(self, path: str, headers: Dict[str, str]) -> 'Pages':
        """
        Add custom header rule

        Args:
            path: Path pattern
            headers: Headers to add

        Returns:
            Pages: Self for method chaining
        """
        self._header_rules.append({
            "path": path,
            "headers": headers
        })
        return self

    def security_headers(self) -> 'Pages':
        """
        Add common security headers

        Returns:
            Pages: Self for method chaining
        """
        security_headers = {
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        }
        return self.header_rule("/*", security_headers)

    # Framework-specific convenience methods
    def react_app(self, repo_url: str, branch: str = "main") -> 'Pages':
        """
        Configure React application deployment

        Args:
            repo_url: GitHub repository URL
            branch: Branch to deploy from

        Returns:
            Pages: Self for method chaining
        """
        self._framework = "react"
        return (self.github_repo(repo_url, branch)
                .build_command("npm run build")
                .output_dir("build")
                .environment_variable("CI", "false"))

    def nextjs_app(self, repo_url: str, branch: str = "main") -> 'Pages':
        """
        Configure Next.js application deployment

        Args:
            repo_url: GitHub repository URL
            branch: Branch to deploy from

        Returns:
            Pages: Self for method chaining
        """
        self._framework = "nextjs"
        return (self.github_repo(repo_url, branch)
                .build_command("npm run build")
                .output_dir("out")
                .environment_variable("NODE_ENV", "production"))

    def vue_app(self, repo_url: str, branch: str = "main") -> 'Pages':
        """
        Configure Vue.js application deployment

        Args:
            repo_url: GitHub repository URL
            branch: Branch to deploy from

        Returns:
            Pages: Self for method chaining
        """
        self._framework = "vue"
        return (self.github_repo(repo_url, branch)
                .build_command("npm run build")
                .output_dir("dist"))

    def angular_app(self, repo_url: str, branch: str = "main") -> 'Pages':
        """
        Configure Angular application deployment

        Args:
            repo_url: GitHub repository URL
            branch: Branch to deploy from

        Returns:
            Pages: Self for method chaining
        """
        self._framework = "angular"
        return (self.github_repo(repo_url, branch)
                .build_command("ng build")
                .output_dir("dist"))

    def static_site(self, repo_url: str, branch: str = "main") -> 'Pages':
        """
        Configure static site deployment

        Args:
            repo_url: GitHub repository URL
            branch: Branch to deploy from

        Returns:
            Pages: Self for method chaining
        """
        self._framework = "static"
        return self.github_repo(repo_url, branch)

    def hugo_site(self, repo_url: str, branch: str = "main") -> 'Pages':
        """
        Configure Hugo site deployment

        Args:
            repo_url: GitHub repository URL
            branch: Branch to deploy from

        Returns:
            Pages: Self for method chaining
        """
        self._framework = "hugo"
        return (self.github_repo(repo_url, branch)
                .build_command("hugo")
                .output_dir("public"))

    def jekyll_site(self, repo_url: str, branch: str = "main") -> 'Pages':
        """
        Configure Jekyll site deployment

        Args:
            repo_url: GitHub repository URL
            branch: Branch to deploy from

        Returns:
            Pages: Self for method chaining
        """
        self._framework = "jekyll"
        return (self.github_repo(repo_url, branch)
                .build_command("bundle exec jekyll build")
                .output_dir("_site"))

    def gatsby_site(self, repo_url: str, branch: str = "main") -> 'Pages':
        """
        Configure Gatsby site deployment

        Args:
            repo_url: GitHub repository URL
            branch: Branch to deploy from

        Returns:
            Pages: Self for method chaining
        """
        self._framework = "gatsby"
        return (self.github_repo(repo_url, branch)
                .build_command("gatsby build")
                .output_dir("public"))

    def preview(self) -> Dict[str, Any]:
        """Preview Pages configuration"""
        self._ensure_authenticated()
        
        preview_data = {
            "project_name": self.project_name,
            "deployment_type": self._deployment_type,
            "framework": self._framework,
            "branch": self._branch
        }

        if self._repo_url:
            preview_data["repository"] = self._repo_url
        if self._build_command:
            preview_data["build_command"] = self._build_command
        if self._output_dir:
            preview_data["output_directory"] = self._output_dir
        if self._root_dir:
            preview_data["root_directory"] = self._root_dir
        if self._environment_variables:
            preview_data["environment_variables"] = self._environment_variables
        if self._custom_domains:
            preview_data["custom_domains"] = self._custom_domains
        if self._redirect_rules:
            preview_data["redirect_rules"] = self._redirect_rules
        if self._header_rules:
            preview_data["header_rules"] = self._header_rules

        return self._format_response("preview", preview_data)

    def create(self) -> Dict[str, Any]:
        """Create Pages project"""
        self._ensure_authenticated()
        
        try:
            result = self.pages_manager.create_pages_project(
                project_name=self.project_name,
                deployment_type=self._deployment_type,
                repo_url=self._repo_url,
                branch=self._branch,
                build_command=self._build_command,
                output_dir=self._output_dir,
                root_dir=self._root_dir,
                environment_variables=self._environment_variables,
                custom_domains=self._custom_domains,
                redirect_rules=self._redirect_rules,
                header_rules=self._header_rules,
                upload_directory=getattr(self, '_upload_directory', None)
            )
            
            return self._format_response("create", result)
        except Exception as e:
            return self._format_error_response("create", str(e))

    def delete(self) -> Dict[str, Any]:
        """Delete Pages project"""
        self._ensure_authenticated()
        
        try:
            result = self.pages_manager.delete_pages_project(self.project_name)
            return self._format_response("delete", result)
        except Exception as e:
            return self._format_error_response("delete", str(e))

    def status(self) -> Dict[str, Any]:
        """Get Pages project status"""
        self._ensure_authenticated()
        
        try:
            result = self.pages_manager.get_pages_status(self.project_name)
            return self._format_response("status", result)
        except Exception as e:
            return self._format_error_response("status", str(e))

    def deploy(self) -> Dict[str, Any]:
        """Trigger new deployment"""
        self._ensure_authenticated()
        
        try:
            result = self.pages_manager.trigger_deployment(self.project_name)
            return self._format_response("deploy", result)
        except Exception as e:
            return self._format_error_response("deploy", str(e))

    def help(self) -> str:
        """Return help information for Pages resource"""
        return f"""
Pages Resource Help
===================

Project: {self.project_name}
Provider: Cloudflare

Deployment Types:
- github_repo(repo, branch): Deploy from GitHub repository
- gitlab_repo(repo, branch): Deploy from GitLab repository
- upload_directory(dir): Upload local directory

Build Configuration:
- build_command(cmd): Set build command
- output_dir(dir): Set output directory
- root_dir(dir): Set root directory
- environment_variable(key, value): Add environment variable
- environment_variables(dict): Set multiple environment variables

Domain Configuration:
- custom_domain(domain): Add custom domain
- redirect_rule(from, to, status): Add redirect rule
- header_rule(path, headers): Add custom headers
- security_headers(): Add common security headers

Framework-Specific Methods:
- react_app(repo): Deploy React application
- nextjs_app(repo): Deploy Next.js application
- vue_app(repo): Deploy Vue.js application
- angular_app(repo): Deploy Angular application
- static_site(repo): Deploy static site
- hugo_site(repo): Deploy Hugo site
- jekyll_site(repo): Deploy Jekyll site
- gatsby_site(repo): Deploy Gatsby site

Methods:
- preview(): Preview Pages configuration
- create(): Create Pages project
- delete(): Delete Pages project
- status(): Get project status
- deploy(): Trigger new deployment
        """ 