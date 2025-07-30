from typing import Dict, Any, List, Optional


class LambdaFunctionConfigurationMixin:
    def memory(self, memory_mb: int) -> 'Lambda':
        self.memory_size = memory_mb
        return self

    def timeout(self, timeout_seconds: int) -> 'Lambda':
        self.timeout_seconds = timeout_seconds
        return self

    def python_runtime(self, runtime: str) -> 'Lambda':
        self.runtime = runtime
        return self

    def set_handler(self, handler: str) -> 'Lambda':
        self.handler = handler
        return self

    def container(self, template_name: str, template_path: str, port: int = 8080) -> 'Lambda':
        self.deployment_package_type = "Image"
        self.container_template = template_path
        self.container_port = port
        return self

    def trigger(self, trigger_type: str, **kwargs) -> 'Lambda':
        if trigger_type == "api-gateway":
            self.api_gateway_integration = True
        elif trigger_type == "s3":
            self.trigger_configurations.append({
                'type': trigger_type,
                'bucket': kwargs.get('bucket'),
                'events': kwargs.get('events', ['s3:ObjectCreated:*'])
            })
        elif trigger_type == "sqs":
            self.trigger_configurations.append({
                'type': trigger_type,
                'queue_arn': kwargs.get('queue_arn'),
                'batch_size': kwargs.get('batch_size', 10)
            })
        elif trigger_type == "eventbridge":
            self.trigger_configurations.append({
                'type': trigger_type,
                'rule_name': kwargs.get('rule_name'),
                'event_pattern': kwargs.get('event_pattern')
            })
        elif trigger_type == "cloudwatch":
            self.trigger_configurations.append({
                'type': trigger_type,
                'rule_name': kwargs.get('rule_name'),
                'schedule_expression': kwargs.get('schedule_expression')
            })
        else:
            self.trigger_configurations.append({
                'type': trigger_type,
                **kwargs
            })
        return self

    def environment(self, variables: Dict[str, str]) -> 'Lambda':
        self.environment_variables.update(variables)
        return self

    def env(self, key: str, value: str) -> 'Lambda':
        self.environment_variables[key] = value
        return self

    def zip_file(self, zip_path: str) -> 'Lambda':
        self.deployment_package_type = "Zip"
        self.code_zip_file = zip_path
        return self

    def python311(self) -> 'Lambda':
        self.runtime = "python3.11"
        return self

    def python39(self) -> 'Lambda':
        self.runtime = "python3.9"
        return self

    def nodejs18(self, runtime: str = "nodejs18.x") -> 'Lambda':
        self.runtime = runtime
        return self

    def description(self, desc: str) -> 'Lambda':
        self.description = desc
        return self

    def tags(self, tags: Dict[str, str]) -> 'Lambda':
        self.tags.update(tags)
        return self

    def tag(self, key: str, value: str) -> 'Lambda':
        self.tags[key] = value
        return self
