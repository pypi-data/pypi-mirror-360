"""
Java Dockerfile Generator

This module provides specialized Dockerfile generation for Java applications,
with support for Maven and Gradle build tools.
"""

from typing import Dict, Any
from .base import BaseDockerfileGenerator


class JavaDockerfileGenerator(BaseDockerfileGenerator):
    """
    Java Dockerfile Generator
    
    Supports:
    - Maven and Gradle build tools
    - Spring Boot framework optimization
    - Multi-stage builds for smaller production images
    - Security hardening with non-root users
    """
    
    def generate(self) -> str:
        """Generate optimized Java Dockerfile."""
        build_tool = self.project_info.get("build_tool", "maven")
        port = self.get_port()
        
        # Always use multi-stage build for Java
        self.add_comment("Multi-stage build for Java application")
        
        # Builder stage
        self._add_builder_stage(build_tool)
        self.add_blank_line()
        
        # Runtime stage
        self._add_runtime_stage(port)
        
        return self.get_content()
    
    def _add_builder_stage(self, build_tool: str):
        """Add the builder stage for compiling Java application."""
        self.add_from("openjdk:17-alpine", platform="linux/amd64")
        self.add_label("stage", "builder")
        self.add_blank_line()
        
        self.add_workdir("/app")
        self.add_blank_line()
        
        if build_tool == "maven":
            self._add_maven_build()
        else:  # gradle
            self._add_gradle_build()
    
    def _add_maven_build(self):
        """Add Maven-specific build instructions."""
        self.add_comment("Copy pom.xml and download dependencies")
        self.add_copy("pom.xml .")
        
        # Download dependencies for better caching
        self.add_run("mvn dependency:go-offline -B")
        self.add_blank_line()
        
        self.add_comment("Copy source and build")
        self.add_copy("src ./src")
        self.add_run("mvn clean package -DskipTests -B")
        self.add_blank_line()
        
        # Extract JAR layers for better caching (Spring Boot optimization)
        self.add_comment("Extract JAR layers for better Docker layer caching")
        self.add_run("java -Djarmode=layertools -jar target/*.jar extract")
    
    def _add_gradle_build(self):
        """Add Gradle-specific build instructions."""
        self.add_comment("Copy build files and download dependencies") 
        self.add_copy("build.gradle settings.gradle gradle.properties* ./")
        self.add_copy("gradle ./gradle")
        self.add_copy("gradlew .")
        
        # Make gradlew executable and download dependencies
        self.add_run("chmod +x gradlew")
        self.add_run("./gradlew dependencies --no-daemon")
        self.add_blank_line()
        
        self.add_comment("Copy source and build")
        self.add_copy("src ./src")
        self.add_run("./gradlew build -x test --no-daemon")
        self.add_blank_line()
        
        # Extract JAR layers for better caching (Spring Boot optimization)
        self.add_comment("Extract JAR layers for better Docker layer caching")
        self.add_run("java -Djarmode=layertools -jar build/libs/*.jar extract")
    
    def _add_runtime_stage(self, port: int):
        """Add the runtime stage for running the Java application."""
        self.add_comment("Runtime stage")
        self.add_from("openjdk:17-alpine")
        self.add_workdir("/app")
        self.add_blank_line()
        
        # Install runtime dependencies
        self.add_comment("Install runtime dependencies")
        self.add_run("apk add --no-cache curl dumb-init")
        self.add_blank_line()
        
        # Performance optimizations
        self.add_performance_optimizations()
        self.add_blank_line()
        
        # Security hardening
        self.add_security_hardening()
        
        # Copy JAR layers for optimal caching
        self.add_comment("Copy JAR layers from builder stage")
        self.add_copy("--from=builder --chown=appuser:appgroup /app/dependencies/ ./")
        self.add_copy("--from=builder --chown=appuser:appgroup /app/spring-boot-loader/ ./")
        self.add_copy("--from=builder --chown=appuser:appgroup /app/snapshot-dependencies/ ./")
        self.add_copy("--from=builder --chown=appuser:appgroup /app/application/ ./")
        self.add_blank_line()
        
        # Switch to non-root user
        self.add_user("appuser")
        self.add_blank_line()
        
        # Expose port
        self.add_expose(port)
        self.add_blank_line()
        
        # Add health check
        self._add_health_check(port)
        self.add_blank_line()
        
        # Add standard labels
        self.add_standard_labels()
        self.add_blank_line()
        
        # Start command with proper signal handling
        self.add_entrypoint('["dumb-init", "--"]')
        self.add_cmd('["java", "org.springframework.boot.loader.JarLauncher"]')
    
    def _add_health_check(self, port: int):
        """Add health check configuration."""
        health_test = f"curl --fail http://localhost:{port}/actuator/health || exit 1"
        self.add_healthcheck(health_test, interval="30s", timeout="10s", retries=3)
    
    def get_optimization_recommendations(self) -> Dict[str, Any]:
        """Get Java specific optimization recommendations."""
        build_tool = self.project_info.get("build_tool", "maven")
        
        recommendations = {
            "multi_stage_build": True,
            "jar_layering": True,
            "dependency_caching": True,
            "build_tool_optimizations": []
        }
        
        if build_tool == "maven":
            recommendations["build_tool_optimizations"].extend([
                "Use Maven dependency plugin for offline builds",
                "Enable Maven build caching",
                "Use Maven wrapper for consistent builds"
            ])
        else:  # gradle
            recommendations["build_tool_optimizations"].extend([
                "Enable Gradle build cache",
                "Use Gradle daemon for faster builds", 
                "Leverage Gradle's incremental compilation"
            ])
        
        recommendations["spring_boot_optimizations"] = [
            "Use JAR layering for better Docker layer caching",
            "Enable Spring Boot Actuator for health checks",
            "Configure JVM heap size based on container memory",
            "Use Spring Boot's built-in graceful shutdown"
        ]
        
        recommendations["jvm_optimizations"] = [
            "Use container-aware JVM flags",
            "Enable G1GC for better performance",
            "Set appropriate heap and metaspace sizes",
            "Use JVM flags for better container integration"
        ]
        
        return recommendations