"""
Migration utilities for Copper Sun Brass security enhancements.

Handles migration from legacy configuration storage to new secure encrypted storage.
Supports backward compatibility and graceful upgrades.
"""

import os
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

from .pure_python_security import PurePythonEncryption

logger = logging.getLogger(__name__)


class ConfigMigration:
    """Handles migration of configurations to new secure storage format."""
    
    def __init__(self):
        self.encryption = PurePythonEncryption()
        self.legacy_global_dir = Path.home() / ".brass"
        self.new_global_dir = Path.home() / ".config" / "coppersun-brass"
        self.migration_log = []
    
    def detect_migration_needed(self) -> Dict[str, Any]:
        """
        Detect if migration is needed and what needs to be migrated.
        
        Returns:
            Dictionary with migration status and recommendations
        """
        status = {
            'migration_needed': False,
            'legacy_configs_found': [],
            'security_issues': [],
            'recommendations': [],
            'priority': 'none'  # none, low, medium, high, critical
        }
        
        # Check for legacy global config
        legacy_config_file = self.legacy_global_dir / "config.json"
        if legacy_config_file.exists():
            try:
                with open(legacy_config_file, 'r') as f:
                    legacy_config = json.load(f)
                
                has_api_keys = self._has_sensitive_data(legacy_config)
                status['legacy_configs_found'].append({
                    'location': str(legacy_config_file),
                    'type': 'global_legacy',
                    'has_api_keys': has_api_keys,
                    'encrypted': legacy_config.get('_encrypted', False)
                })
                
                if has_api_keys and not legacy_config.get('_encrypted', False):
                    status['security_issues'].append("Unencrypted API keys in legacy global config")
                    status['priority'] = 'high'
                    status['migration_needed'] = True
                    
            except Exception as e:
                status['security_issues'].append(f"Cannot read legacy config: {e}")
        
        # Check for legacy .env files with API keys
        env_locations = [
            Path(".env"),
            Path("../.env"),
            Path("../../.env")
        ]
        
        for env_path in env_locations:
            if env_path.exists():
                try:
                    with open(env_path, 'r') as f:
                        content = f.read()
                    
                    if 'ANTHROPIC_API_KEY' in content or 'LEMONSQUEEZY_API_KEY' in content:
                        status['legacy_configs_found'].append({
                            'location': str(env_path),
                            'type': 'env_file',
                            'has_api_keys': True,
                            'encrypted': False
                        })
                        status['security_issues'].append(f"API keys in plain text .env file: {env_path}")
                        if status['priority'] != 'high':
                            status['priority'] = 'medium'
                        status['migration_needed'] = True
                        
                except Exception:
                    pass
        
        # Check if new global config already exists
        new_config_file = self.new_global_dir / "config.json"
        if new_config_file.exists():
            status['recommendations'].append("New secure global config already exists")
        else:
            if status['legacy_configs_found']:
                status['recommendations'].append("Migrate to new secure global config location")
        
        # Generate recommendations based on findings
        if status['migration_needed']:
            if status['priority'] == 'high':
                status['recommendations'].insert(0, "URGENT: Migrate unencrypted API keys to secure storage")
            
            status['recommendations'].extend([
                "Run 'brass config audit' to see detailed security status",
                "Use 'brass migrate' command to safely migrate configurations",
                "Consider using environment variables for production environments"
            ])
        
        return status
    
    def _has_sensitive_data(self, config: Dict[str, Any]) -> bool:
        """Check if config contains sensitive data that should be encrypted."""
        if 'user_preferences' not in config:
            return False
        
        prefs = config['user_preferences']
        for key in ['claude_api_key', 'lemonsqueezy_api_key']:
            if prefs.get(key) and prefs[key] not in [None, '', '[ENCRYPTED]']:
                return True
        
        return False
    
    def migrate_configurations(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Migrate configurations to new secure format.
        
        Args:
            dry_run: If True, show what would be done without making changes
            
        Returns:
            Migration results and status
        """
        results = {
            'success': True,
            'actions_taken': [],
            'errors': [],
            'security_improvements': [],
            'backed_up_files': []
        }
        
        if dry_run:
            results['actions_taken'].append("DRY RUN MODE - No actual changes made")
        
        try:
            # Step 1: Create new global config directory
            if not self.new_global_dir.exists():
                if not dry_run:
                    self.new_global_dir.mkdir(parents=True, exist_ok=True)
                    # Set secure permissions
                    import stat
                    self.new_global_dir.chmod(stat.S_IRWXU)  # 700
                
                results['actions_taken'].append(f"Created secure global config directory: {self.new_global_dir}")
            
            # Step 2: Migrate legacy global config if exists
            legacy_config_file = self.legacy_global_dir / "config.json"
            new_config_file = self.new_global_dir / "config.json"
            
            if legacy_config_file.exists():
                if not dry_run:
                    # Backup original
                    backup_file = legacy_config_file.with_suffix('.backup.json')
                    shutil.copy2(legacy_config_file, backup_file)
                    results['backed_up_files'].append(str(backup_file))
                
                with open(legacy_config_file, 'r') as f:
                    legacy_config = json.load(f)
                
                # Check if migration needed
                if self._has_sensitive_data(legacy_config):
                    if not legacy_config.get('_encrypted', False):
                        # Encrypt the config
                        encrypted_config = self.encryption.encrypt_config(legacy_config)
                        
                        if not dry_run:
                            with open(new_config_file, 'w') as f:
                                json.dump(encrypted_config, f, indent=2)
                            
                            # Set secure permissions
                            import stat
                            new_config_file.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 600
                        
                        results['actions_taken'].append(f"Migrated and encrypted config: {legacy_config_file} -> {new_config_file}")
                        results['security_improvements'].append("API keys now encrypted with machine-specific keys")
                    else:
                        # Already encrypted, just move
                        if not dry_run:
                            shutil.copy2(legacy_config_file, new_config_file)
                        
                        results['actions_taken'].append(f"Moved encrypted config: {legacy_config_file} -> {new_config_file}")
                else:
                    # No sensitive data, just copy
                    if not dry_run:
                        shutil.copy2(legacy_config_file, new_config_file)
                    
                    results['actions_taken'].append(f"Moved config (no encryption needed): {legacy_config_file} -> {new_config_file}")
            
            # Step 3: Handle .env files (offer to migrate, don't auto-migrate)
            env_files_with_keys = []
            env_locations = [Path(".env"), Path("../.env"), Path("../../.env")]
            
            for env_path in env_locations:
                if env_path.exists():
                    try:
                        with open(env_path, 'r') as f:
                            content = f.read()
                        
                        if 'ANTHROPIC_API_KEY' in content or 'LEMONSQUEEZY_API_KEY' in content:
                            env_files_with_keys.append(env_path)
                    except Exception:
                        pass
            
            if env_files_with_keys:
                results['actions_taken'].append(f"Found {len(env_files_with_keys)} .env files with API keys")
                results['actions_taken'].append("MANUAL ACTION REQUIRED: Consider migrating .env API keys to global config")
                results['security_improvements'].append("Consolidate API keys in secure global config instead of .env files")
            
            # Step 4: Summary
            if results['security_improvements']:
                results['actions_taken'].append("Security migration completed successfully")
            else:
                results['actions_taken'].append("No security migration needed - configurations already secure")
                
        except Exception as e:
            results['success'] = False
            results['errors'].append(f"Migration failed: {str(e)}")
            logger.error(f"Migration failed: {e}")
        
        return results
    
    def create_migration_script(self) -> str:
        """
        Create a migration script for complex scenarios.
        
        Returns:
            Script content as string
        """
        script = '''#!/usr/bin/env python3
"""
Copper Sun Brass Configuration Migration Script

This script helps migrate from legacy configuration storage to new secure storage.
Generated automatically based on your current configuration.
"""

import os
import sys
from pathlib import Path

# Add brass to path
sys.path.insert(0, 'src')

try:
    from coppersun_brass.cli.migration_utils import ConfigMigration
    from coppersun_brass.cli.brass_cli import BrassCLI
    
    print("🔧 Copper Sun Brass Configuration Migration")
    print("=" * 50)
    
    # Step 1: Check current status
    migration = ConfigMigration()
    status = migration.detect_migration_needed()
    
    print(f"Migration needed: {status['migration_needed']}")
    print(f"Priority: {status['priority']}")
    print(f"Configs found: {len(status['legacy_configs_found'])}")
    print(f"Security issues: {len(status['security_issues'])}")
    
    if status['migration_needed']:
        print("\\n🚨 Issues found:")
        for issue in status['security_issues']:
            print(f"  • {issue}")
        
        print("\\n💡 Recommendations:")
        for rec in status['recommendations']:
            print(f"  • {rec}")
        
        # Ask user for confirmation
        print("\\n" + "=" * 50)
        confirm = input("Proceed with migration? (y/N): ").strip().lower()
        
        if confirm == 'y':
            print("\\n🔄 Starting migration...")
            results = migration.migrate_configurations(dry_run=False)
            
            if results['success']:
                print("\\n✅ Migration completed successfully!")
                for action in results['actions_taken']:
                    print(f"  • {action}")
                    
                if results['security_improvements']:
                    print("\\n🛡️ Security improvements:")
                    for improvement in results['security_improvements']:
                        print(f"  • {improvement}")
            else:
                print("\\n❌ Migration failed:")
                for error in results['errors']:
                    print(f"  • {error}")
        else:
            print("\\nMigration cancelled.")
    else:
        print("\\n✅ No migration needed - your configuration is already secure!")
    
    print("\\n💡 Run 'brass config audit' to verify your security status.")
    
except ImportError as e:
    print(f"Error: Could not import brass modules: {e}")
    print("Make sure you're running this from the brass project directory.")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)
'''
        return script


def get_migration_status() -> Dict[str, Any]:
    """Quick function to get migration status."""
    migration = ConfigMigration()
    return migration.detect_migration_needed()


def suggest_migration_actions(status: Dict[str, Any]) -> List[str]:
    """Generate user-friendly migration suggestions based on status."""
    suggestions = []
    
    if not status['migration_needed']:
        suggestions.append("✅ Your configuration is already secure!")
        suggestions.append("💡 Run 'brass config audit' to verify security status")
        return suggestions
    
    priority = status['priority']
    if priority == 'high':
        suggestions.append("🚨 URGENT: You have unencrypted API keys!")
        suggestions.append("🔧 Run 'brass migrate' to secure your configuration")
    elif priority == 'medium':
        suggestions.append("⚠️  Security improvement recommended")
        suggestions.append("🔧 Run 'brass migrate' to consolidate API key storage")
    
    # Specific suggestions based on findings
    legacy_configs = status.get('legacy_configs_found', [])
    for config in legacy_configs:
        if config['type'] == 'global_legacy' and config['has_api_keys'] and not config['encrypted']:
            suggestions.append(f"📁 Encrypt legacy config: {config['location']}")
        elif config['type'] == 'env_file':
            suggestions.append(f"📄 Consolidate .env keys: {config['location']}")
    
    suggestions.append("💡 Use 'brass config show' to see configuration hierarchy")
    suggestions.append("🛡️  Use 'brass config audit' for detailed security analysis")
    
    return suggestions