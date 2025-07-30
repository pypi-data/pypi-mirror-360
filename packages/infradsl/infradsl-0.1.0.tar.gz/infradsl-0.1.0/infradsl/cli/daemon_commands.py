"""
InfraDSL Daemon CLI Commands

CLI interface for managing the autonomous monitoring daemon.
"""

import os
import sys
import time
import click
import json
from pathlib import Path
from typing import Dict, Any

from ..daemon.monitor import InfraDSLDaemon, start_daemon, stop_daemon, get_daemon_status
from ..daemon.config import DaemonConfig, create_example_config


@click.group(name='daemon')
def daemon_cli():
    """Autonomous infrastructure monitoring daemon commands"""
    pass


@daemon_cli.command('start')
@click.option('--config', '-c', default='.infradsl_daemon.yml', 
              help='Configuration file path')
@click.option('--background', '-b', is_flag=True, 
              help='Run daemon in background mode')
@click.option('--foreground', '-f', is_flag=True, 
              help='Run daemon in foreground mode (default)')
def start_daemon_cmd(config: str, background: bool, foreground: bool):
    """Start the InfraDSL monitoring daemon"""
    
    # Check if daemon is already running
    current_status = get_daemon_status()
    if current_status.get('running'):
        click.echo(f"⚠️  Daemon is already running (PID: {current_status.get('pid')})")
        return
    
    # Create default config if it doesn't exist
    if not os.path.exists(config):
        click.echo(f"📋 Configuration file {config} not found")
        if click.confirm("Create a default configuration file?"):
            example_content = create_example_config()
            with open(config, 'w') as f:
                f.write(example_content)
            click.echo(f"✅ Created {config}")
            click.echo(f"💡 Edit {config} to customize your monitoring settings")
        else:
            click.echo("❌ Cannot start daemon without configuration")
            return
    
    try:
        click.echo(f"🚀 Starting InfraDSL monitoring daemon...")
        click.echo(f"📋 Configuration: {config}")
        
        if background:
            # Start in background mode
            daemon = InfraDSLDaemon(config)
            daemon.start(background=True)
            
            # Give it a moment to start
            time.sleep(2)
            
            # Check if it actually started
            status = get_daemon_status()
            if status.get('running'):
                click.echo(f"✅ Daemon started successfully in background mode")
                click.echo(f"📊 PID: {status.get('pid')}")
                click.echo(f"💡 Use 'infra daemon status' to check daemon health")
                click.echo(f"💡 Use 'infra daemon logs' to view monitoring activity")
            else:
                click.echo(f"❌ Failed to start daemon in background mode")
        else:
            # Start in foreground mode (default)
            click.echo(f"✅ Starting daemon in foreground mode")
            click.echo(f"💡 Press Ctrl+C to stop the daemon")
            
            daemon = InfraDSLDaemon(config)
            try:
                daemon.start(background=False)
            except KeyboardInterrupt:
                click.echo(f"\n🛑 Stopping daemon...")
                daemon.stop()
                click.echo(f"✅ Daemon stopped")
    
    except Exception as e:
        click.echo(f"❌ Failed to start daemon: {e}")
        sys.exit(1)


@daemon_cli.command('stop')
@click.option('--pid-file', default='/tmp/infradsl-daemon.pid',
              help='PID file path')
def stop_daemon_cmd(pid_file: str):
    """Stop the InfraDSL monitoring daemon"""
    
    status = get_daemon_status(pid_file)
    
    if not status.get('running'):
        click.echo(f"⚠️  Daemon is not running")
        return
    
    click.echo(f"🛑 Stopping InfraDSL daemon (PID: {status.get('pid')})...")
    
    if stop_daemon(pid_file):
        # Wait a moment and check if it actually stopped
        time.sleep(2)
        final_status = get_daemon_status(pid_file)
        
        if not final_status.get('running'):
            click.echo(f"✅ Daemon stopped successfully")
        else:
            click.echo(f"⚠️  Daemon may still be running")
    else:
        click.echo(f"❌ Failed to stop daemon")


@daemon_cli.command('restart')
@click.option('--config', '-c', default='.infradsl_daemon.yml',
              help='Configuration file path')
@click.option('--background', '-b', is_flag=True, default=True,
              help='Run daemon in background mode after restart')
def restart_daemon_cmd(config: str, background: bool):
    """Restart the InfraDSL monitoring daemon"""
    
    click.echo(f"🔄 Restarting InfraDSL daemon...")
    
    # Stop daemon if running
    status = get_daemon_status()
    if status.get('running'):
        click.echo(f"🛑 Stopping current daemon...")
        stop_daemon()
        time.sleep(3)  # Give it time to stop
    
    # Start daemon
    click.echo(f"🚀 Starting daemon...")
    try:
        daemon = InfraDSLDaemon(config)
        daemon.start(background=background)
        
        if background:
            time.sleep(2)
            new_status = get_daemon_status()
            if new_status.get('running'):
                click.echo(f"✅ Daemon restarted successfully (PID: {new_status.get('pid')})")
            else:
                click.echo(f"❌ Failed to restart daemon")
        else:
            click.echo(f"✅ Daemon restarted in foreground mode")
    
    except Exception as e:
        click.echo(f"❌ Failed to restart daemon: {e}")


@daemon_cli.command('status')
@click.option('--json', 'output_json', is_flag=True,
              help='Output status in JSON format')
@click.option('--pid-file', default='/tmp/infradsl-daemon.pid',
              help='PID file path')
def status_daemon_cmd(output_json: bool, pid_file: str):
    """Show daemon status and statistics"""
    
    try:
        status = get_daemon_status(pid_file)
        
        if output_json:
            click.echo(json.dumps(status, indent=2))
            return
        
        # Human-readable output
        click.echo(f"📊 InfraDSL Daemon Status")
        click.echo(f"=" * 30)
        
        if status.get('running'):
            click.echo(f"✅ Status: Running")
            click.echo(f"📍 PID: {status.get('pid')}")
            click.echo(f"📁 PID File: {status.get('pid_file')}")
        else:
            click.echo(f"❌ Status: Not Running")
            if 'error' in status:
                click.echo(f"❗ Error: {status['error']}")
            elif 'status' in status:
                click.echo(f"💡 Note: {status['status']}")
        
        # Try to get detailed stats if daemon is accessible
        if status.get('running'):
            try:
                # This would require the daemon to expose a status endpoint
                # For now, just show basic process info
                click.echo(f"\n📈 Basic Process Info:")
                click.echo(f"   Process ID: {status.get('pid')}")
                click.echo(f"   PID File: {status.get('pid_file')}")
                click.echo(f"\n💡 Use 'infra daemon logs' to view monitoring activity")
            except Exception:
                pass
    
    except Exception as e:
        click.echo(f"❌ Failed to get daemon status: {e}")


@daemon_cli.command('logs')
@click.option('--follow', '-f', is_flag=True,
              help='Follow log output (like tail -f)')
@click.option('--tail', '-n', default=50, type=int,
              help='Number of recent lines to show')
@click.option('--config', '-c', default='.infradsl_daemon.yml',
              help='Configuration file to get log settings')
def logs_daemon_cmd(follow: bool, tail: int, config: str):
    """View daemon logs"""
    
    try:
        # For now, we'll show a simulation of logs since our daemon logs to console
        # In a production version, this would read from actual log files
        
        click.echo(f"📋 InfraDSL Daemon Logs (simulated)")
        click.echo(f"=" * 40)
        
        # Check if daemon is running
        status = get_daemon_status()
        if not status.get('running'):
            click.echo(f"⚠️  Daemon is not running")
            click.echo(f"💡 Start the daemon with: infra daemon start")
            return
        
        # Simulate log viewing
        click.echo(f"✅ Daemon is running (PID: {status.get('pid')})")
        click.echo(f"📊 Monitoring logs are displayed in the daemon console output")
        click.echo(f"\n💡 To see real-time logs:")
        click.echo(f"   1. Stop current daemon: infra daemon stop")
        click.echo(f"   2. Start in foreground: infra daemon start --foreground")
        click.echo(f"\n📁 Log file integration coming in next version...")
        
        if follow:
            click.echo(f"\n🔄 Following logs... (Press Ctrl+C to stop)")
            try:
                while True:
                    time.sleep(1)
                    # In real implementation, this would tail actual log files
            except KeyboardInterrupt:
                click.echo(f"\n✅ Stopped following logs")
    
    except Exception as e:
        click.echo(f"❌ Failed to view logs: {e}")


@daemon_cli.command('config')
@click.option('--show', '-s', is_flag=True,
              help='Show current configuration')
@click.option('--create', '-c', is_flag=True,
              help='Create example configuration')
@click.option('--edit', '-e', is_flag=True,
              help='Edit configuration file')
@click.option('--validate', '-v', is_flag=True,
              help='Validate configuration file')
@click.argument('config_file', default='.infradsl_daemon.yml')
def config_daemon_cmd(show: bool, create: bool, edit: bool, validate: bool, config_file: str):
    """Manage daemon configuration"""
    
    if create:
        # Create example configuration
        if os.path.exists(config_file):
            if not click.confirm(f"Configuration file {config_file} already exists. Overwrite?"):
                return
        
        example_content = create_example_config()
        with open(config_file, 'w') as f:
            f.write(example_content)
        
        click.echo(f"✅ Created example configuration: {config_file}")
        click.echo(f"💡 Edit the file to customize your monitoring settings")
        return
    
    if not os.path.exists(config_file):
        click.echo(f"❌ Configuration file not found: {config_file}")
        click.echo(f"💡 Create one with: infra daemon config --create")
        return
    
    if show:
        # Show current configuration
        try:
            with open(config_file, 'r') as f:
                content = f.read()
            click.echo(f"📋 Configuration: {config_file}")
            click.echo(f"=" * 40)
            click.echo(content)
        except Exception as e:
            click.echo(f"❌ Failed to read configuration: {e}")
    
    elif validate:
        # Validate configuration
        try:
            config = DaemonConfig.load(config_file)
            click.echo(f"✅ Configuration is valid: {config_file}")
            click.echo(f"📊 Settings:")
            click.echo(f"   Check interval: {config.check_interval}")
            click.echo(f"   Log level: {config.log_level}")
            click.echo(f"   Policies: {len(config.policies)}")
            click.echo(f"   Alerts: {len(config.alerts)}")
            click.echo(f"   Resources: {len(config.resources)}")
        except Exception as e:
            click.echo(f"❌ Configuration validation failed: {e}")
    
    elif edit:
        # Edit configuration
        editor = os.environ.get('EDITOR', 'nano')
        try:
            os.system(f"{editor} {config_file}")
            click.echo(f"📝 Configuration editing completed")
            click.echo(f"💡 Restart daemon to apply changes: infra daemon restart")
        except Exception as e:
            click.echo(f"❌ Failed to open editor: {e}")
    
    else:
        # Default: show brief config info
        try:
            config = DaemonConfig.load(config_file)
            click.echo(f"📋 Configuration Summary: {config_file}")
            click.echo(f"=" * 40)
            click.echo(f"Check interval: {config.check_interval}")
            click.echo(f"Log level: {config.log_level}")
            click.echo(f"Auto discovery: {config.auto_discovery}")
            click.echo(f"Cache directory: {config.cache_dir}")
            click.echo(f"Policies: {len(config.policies)}")
            click.echo(f"Alerts configured: {len(config.alerts)}")
            click.echo(f"Resource overrides: {len(config.resources)}")
            click.echo(f"\n💡 Use --show to see full configuration")
            click.echo(f"💡 Use --edit to modify configuration")
        except Exception as e:
            click.echo(f"❌ Failed to load configuration: {e}")


@daemon_cli.command('test')
@click.option('--config', '-c', default='.infradsl_daemon.yml',
              help='Configuration file path')
@click.option('--duration', '-d', default=60, type=int,
              help='Test duration in seconds')
def test_daemon_cmd(config: str, duration: int):
    """Test daemon functionality (for development)"""
    
    click.echo(f"🧪 Testing InfraDSL Daemon")
    click.echo(f"=" * 30)
    
    # Check for cached resources
    cache_dir = ".infradsl_cache"
    if not os.path.exists(cache_dir) or not any(os.listdir(cache_dir)):
        click.echo(f"📭 No cached resources found in {cache_dir}")
        click.echo(f"💡 Create some resources first:")
        click.echo(f"   cd googlecloud/vms && python simple-vm.infra.py")
        return
    
    try:
        # Initialize daemon
        daemon = InfraDSLDaemon(config)
        
        # Show discovered resources
        cached_resources = daemon.discovery.discover_cached_resources()
        click.echo(f"📊 Found {len(cached_resources)} cached resources:")
        for resource in cached_resources:
            click.echo(f"   • {resource.provider}:{resource.resource_name} ({resource.resource_type})")
        
        # Start daemon in background for testing
        click.echo(f"\n🚀 Starting daemon for {duration} seconds...")
        daemon.start(background=True)
        
        # Monitor for specified duration
        start_time = time.time()
        while time.time() - start_time < duration:
            status = daemon.get_status()
            elapsed = time.time() - start_time
            
            click.echo(f"\r📊 Elapsed: {elapsed:.0f}s | Checks: {status['stats']['checks_performed']} | Drift: {status['stats']['drift_detected']}", nl=False)
            time.sleep(5)
        
        click.echo(f"\n")
        
        # Stop daemon and show final stats
        daemon.stop()
        final_status = daemon.get_status()
        stats = final_status['stats']
        
        click.echo(f"✅ Test completed!")
        click.echo(f"📊 Final Statistics:")
        click.echo(f"   Resources monitored: {stats['resources_monitored']}")
        click.echo(f"   Total checks: {stats['checks_performed']}")
        click.echo(f"   Drift detected: {stats['drift_detected']}")
        click.echo(f"   Auto-remediations: {stats['auto_remediations']}")
        click.echo(f"   Failed checks: {stats['failed_checks']}")
    
    except Exception as e:
        click.echo(f"❌ Test failed: {e}")


# Add the daemon commands to the main CLI
def register_daemon_commands(cli_group):
    """Register daemon commands with the main CLI"""
    cli_group.add_command(daemon_cli)