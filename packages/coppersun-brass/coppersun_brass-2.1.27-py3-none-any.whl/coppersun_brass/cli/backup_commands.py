"""CLI commands for backup and restore operations."""

import click
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

from coppersun_brass.core.backup_manager import BackupManager
from coppersun_brass.core.config_loader import get_config


@click.group()
def backup():
    """Database backup and restore commands."""
    pass


@backup.command()
@click.option('--description', '-d', help='Description for the backup')
@click.option('--compress/--no-compress', default=True, help='Compress backup with gzip')
def create(description: Optional[str], compress: bool):
    """Create a new database backup."""
    config = get_config()
    
    # Initialize backup manager
    manager = BackupManager(
        db_path=config.storage.path,
        backup_dir=config.storage.backup_path,
        retention_days=config.storage.backup_retention_days,
        max_backups=config.storage.max_backups,
        compress=compress
    )
    
    try:
        # Create backup
        info = manager.create_backup(description or "manual")
        
        click.echo(f"✅ Backup created successfully")
        click.echo(f"   Path: {info.path}")
        click.echo(f"   Size: {info.size_mb:.1f} MB")
        click.echo(f"   Compressed: {'Yes' if info.compressed else 'No'}")
        
    except Exception as e:
        click.echo(f"❌ Backup failed: {e}", err=True)
        sys.exit(1)


@backup.command()
def list():
    """List all available backups."""
    config = get_config()
    
    # Initialize backup manager
    manager = BackupManager(
        db_path=config.storage.path,
        backup_dir=config.storage.backup_path,
        retention_days=config.storage.backup_retention_days,
        max_backups=config.storage.max_backups
    )
    
    backups = manager.list_backups()
    
    if not backups:
        click.echo("No backups found")
        return
        
    click.echo(f"Found {len(backups)} backups:")
    click.echo()
    
    # Table header
    click.echo(f"{'Filename':<50} {'Created':<20} {'Size':<10} {'Age':<10}")
    click.echo("-" * 90)
    
    for backup in backups:
        created = datetime.fromtimestamp(backup.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        age = f"{backup.age_days:.1f}d"
        size = f"{backup.size_mb:.1f}MB"
        
        click.echo(f"{backup.path.name:<50} {created:<20} {size:<10} {age:<10}")
        
    # Summary
    click.echo()
    summary = manager.get_backup_summary()
    click.echo(f"Total size: {summary['total_size_mb']:.1f} MB")
    click.echo(f"Average size: {summary['average_size_mb']:.1f} MB")


@backup.command()
@click.argument('backup_file')
@click.option('--verify/--no-verify', default=True, help='Verify backup before restore')
@click.option('--force', '-f', is_flag=True, help='Skip confirmation prompt')
def restore(backup_file: str, verify: bool, force: bool):
    """Restore database from a backup file."""
    config = get_config()
    
    # Find backup file
    backup_path = Path(backup_file)
    if not backup_path.is_absolute():
        # Check in backup directory
        backup_dir = Path(config.storage.backup_path)
        full_path = backup_dir / backup_file
        if full_path.exists():
            backup_path = full_path
            
    if not backup_path.exists():
        click.echo(f"❌ Backup file not found: {backup_file}", err=True)
        sys.exit(1)
        
    # Confirm restore
    if not force:
        click.echo(f"⚠️  This will replace the current database with backup: {backup_path.name}")
        if not click.confirm("Continue?"):
            click.echo("Restore cancelled")
            return
            
    # Initialize backup manager
    manager = BackupManager(
        db_path=config.storage.path,
        backup_dir=config.storage.backup_path,
        retention_days=config.storage.backup_retention_days,
        max_backups=config.storage.max_backups
    )
    
    try:
        # Restore backup
        manager.restore_backup(backup_path, verify=verify)
        
        click.echo(f"✅ Database restored from {backup_path.name}")
        
    except Exception as e:
        click.echo(f"❌ Restore failed: {e}", err=True)
        sys.exit(1)


@backup.command()
@click.option('--older-than', type=int, help='Remove backups older than N days')
@click.option('--keep-count', type=int, help='Keep only the N most recent backups')
@click.option('--dry-run', is_flag=True, help='Show what would be removed without removing')
def cleanup(older_than: Optional[int], keep_count: Optional[int], dry_run: bool):
    """Clean up old backups based on retention policy."""
    config = get_config()
    
    # Initialize backup manager
    manager = BackupManager(
        db_path=config.storage.path,
        backup_dir=config.storage.backup_path,
        retention_days=older_than or config.storage.backup_retention_days,
        max_backups=keep_count or config.storage.max_backups
    )
    
    backups = manager.list_backups()
    if not backups:
        click.echo("No backups to clean up")
        return
        
    # Determine what would be removed
    to_remove = []
    
    # By age
    if older_than:
        for backup in backups:
            if backup.age_days > older_than:
                to_remove.append(backup)
                
    # By count
    if keep_count and len(backups) > keep_count:
        to_remove.extend(backups[keep_count:])
        
    # Remove duplicates
    to_remove = list(set(to_remove))
    
    if not to_remove:
        click.echo("No backups match cleanup criteria")
        return
        
    click.echo(f"Would remove {len(to_remove)} backups:")
    for backup in to_remove:
        click.echo(f"  - {backup.path.name} ({backup.age_days:.1f} days old, {backup.size_mb:.1f} MB)")
        
    if dry_run:
        click.echo("\n(Dry run - no files removed)")
        return
        
    if click.confirm("\nRemove these backups?"):
        removed = 0
        for backup in to_remove:
            try:
                backup.path.unlink()
                removed += 1
            except Exception as e:
                click.echo(f"Failed to remove {backup.path.name}: {e}", err=True)
                
        click.echo(f"\n✅ Removed {removed} backups")


@backup.command()
@click.option('--interval', type=int, default=3600, help='Backup interval in seconds')
def auto(interval: int):
    """Start automatic backup service."""
    config = get_config()
    
    # Initialize backup manager
    manager = BackupManager(
        db_path=config.storage.path,
        backup_dir=config.storage.backup_path,
        retention_days=config.storage.backup_retention_days,
        max_backups=config.storage.max_backups
    )
    
    click.echo(f"Starting automatic backups every {interval} seconds...")
    click.echo("Press Ctrl+C to stop")
    
    try:
        manager.start_automatic_backups(interval)
        
        # Keep running until interrupted
        import signal
        signal.pause()
        
    except KeyboardInterrupt:
        click.echo("\nStopping automatic backups...")
        manager.stop_automatic_backups()
        click.echo("✅ Automatic backups stopped")


@backup.command()
def status():
    """Show backup system status."""
    config = get_config()
    
    # Initialize backup manager
    manager = BackupManager(
        db_path=config.storage.path,
        backup_dir=config.storage.backup_path,
        retention_days=config.storage.backup_retention_days,
        max_backups=config.storage.max_backups
    )
    
    summary = manager.get_backup_summary()
    
    click.echo("Backup System Status")
    click.echo("=" * 50)
    click.echo(f"Database: {config.storage.path}")
    click.echo(f"Backup directory: {config.storage.backup_path}")
    click.echo(f"Retention: {config.storage.backup_retention_days} days")
    click.echo(f"Max backups: {config.storage.max_backups}")
    click.echo()
    
    if summary['total_backups'] == 0:
        click.echo("No backups found")
    else:
        click.echo(f"Total backups: {summary['total_backups']}")
        click.echo(f"Total size: {summary['total_size_mb']:.1f} MB")
        click.echo(f"Average size: {summary['average_size_mb']:.1f} MB")
        click.echo()
        
        if summary['newest_backup']:
            click.echo(f"Newest backup: {summary['newest_backup']['name']}")
            click.echo(f"  Age: {summary['newest_backup']['age_days']:.1f} days")
            click.echo(f"  Size: {summary['newest_backup']['size_mb']:.1f} MB")
            
        if summary['oldest_backup']:
            click.echo()
            click.echo(f"Oldest backup: {summary['oldest_backup']['name']}")
            click.echo(f"  Age: {summary['oldest_backup']['age_days']:.1f} days")
            click.echo(f"  Size: {summary['oldest_backup']['size_mb']:.1f} MB")