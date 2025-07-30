"""
Main CLI Entry Point
🧵 Synth: Terminal orchestration for the unified Nyro package

Provides command-line interface entry points for:
- Interactive mode (replacing all bash menu systems)
- Direct commands (replacing individual scripts)
- Profile management
- Musical ledger operations
"""

import sys
import argparse
from typing import Optional

from .interactive import InteractiveCLI
from ..core.client import RedisClient
from ..core.profiles import ProfileManager
from ..core.operations import RedisOperations
from ..musical.ledger import MusicalLedger


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        prog='nyro',
        description='♠️🌿🎸🧵 Nyro - Unified Redis Operations Package',
        epilog='Consolidates 13+ bash scripts into unified Python interface'
    )
    
    # Global options
    parser.add_argument('--profile', '-p', help='Redis profile to use')
    parser.add_argument('--musical', '-m', action='store_true', help='Enable musical ledger')
    parser.add_argument('--version', '-v', action='version', version='Nyro 0.1.0')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Interactive mode
    interactive_parser = subparsers.add_parser('interactive', aliases=['i'], help='Start interactive CLI')
    
    # Basic operations
    set_parser = subparsers.add_parser('set', help='Set Redis key')
    set_parser.add_argument('key', help='Key name')
    set_parser.add_argument('value', help='Key value')
    
    get_parser = subparsers.add_parser('get', help='Get Redis key')
    get_parser.add_argument('key', help='Key name')
    
    del_parser = subparsers.add_parser('del', help='Delete Redis key')
    del_parser.add_argument('key', help='Key name')
    
    # Scanning
    scan_parser = subparsers.add_parser('scan', help='Scan Redis keys')
    scan_parser.add_argument('pattern', nargs='?', default='*', help='Search pattern')
    scan_parser.add_argument('--garden', '-g', action='store_true', help='Garden scan with categories')
    
    # List operations
    list_parser = subparsers.add_parser('list', help='List operations')
    list_subparsers = list_parser.add_subparsers(dest='list_command')
    
    push_parser = list_subparsers.add_parser('push', help='Push to list')
    push_parser.add_argument('list_name', help='List name')
    push_parser.add_argument('element', help='Element to push')
    push_parser.add_argument('--right', '-r', action='store_true', help='Push to right (default left)')
    
    read_parser = list_subparsers.add_parser('read', help='Read from list')
    read_parser.add_argument('list_name', help='List name')
    read_parser.add_argument('--start', '-s', type=int, default=0, help='Start index')
    read_parser.add_argument('--stop', '-e', type=int, default=-1, help='Stop index')
    
    # Stream operations  
    stream_parser = subparsers.add_parser('stream', help='Stream operations')
    stream_subparsers = stream_parser.add_subparsers(dest='stream_command')
    
    diary_parser = stream_subparsers.add_parser('diary', help='Garden diary operations')
    diary_parser.add_argument('action', choices=['add', 'read'], help='Diary action')
    diary_parser.add_argument('--name', '-n', default='garden.diary', help='Diary name')
    diary_parser.add_argument('--event', '-e', help='Event description (for add)')
    diary_parser.add_argument('--mood', '-m', help='Mood (for add)')
    diary_parser.add_argument('--count', '-c', type=int, default=10, help='Entries to read')
    
    # Profile management
    profile_parser = subparsers.add_parser('profiles', help='Profile management')
    profile_parser.add_argument('action', choices=['list', 'switch', 'current'], help='Profile action')
    profile_parser.add_argument('name', nargs='?', help='Profile name (for switch)')
    
    # Musical ledger
    music_parser = subparsers.add_parser('music', help='Musical ledger operations')
    music_parser.add_argument('action', choices=['summary', 'export'], help='Music action')
    music_parser.add_argument('--session', '-s', help='Session ID')
    
    # Test connection
    test_parser = subparsers.add_parser('test', help='Test Redis connection')
    
    # Initialize environment
    init_parser = subparsers.add_parser('init', help='Initialize .env file and setup')
    init_parser.add_argument('--force', '-f', action='store_true', help='Overwrite existing .env file')
    
    return parser


def handle_basic_operations(args, client: RedisClient, musical_ledger: Optional[MusicalLedger]) -> None:
    """Handle basic Redis operations."""
    if args.command == 'set':
        success = client.set_key(args.key, args.value)
        if success:
            print(f"✅ Set {args.key} = {args.value}")
            if musical_ledger:
                musical_ledger.add_team_activity("🧵", "set_key", f"CLI set: {args.key}")
        else:
            print(f"❌ Failed to set {args.key}")
            sys.exit(1)
            
    elif args.command == 'get':
        value = client.get_key(args.key)
        if value is not None:
            print(value)
            if musical_ledger:
                musical_ledger.add_team_activity("🧵", "get_key", f"CLI get: {args.key}")
        else:
            print(f"❌ Key '{args.key}' not found", file=sys.stderr)
            sys.exit(1)
            
    elif args.command == 'del':
        success = client.delete_key(args.key)
        if success:
            print(f"🗑️ Deleted {args.key}")
            if musical_ledger:
                musical_ledger.add_team_activity("🧵", "delete_key", f"CLI delete: {args.key}")
        else:
            print(f"❌ Failed to delete {args.key}")
            sys.exit(1)


def handle_scanning(args, client: RedisClient, operations: RedisOperations, musical_ledger: Optional[MusicalLedger]) -> None:
    """Handle scanning operations."""
    if args.garden:
        result = operations.scan_garden(args.pattern)
        print(f"🌿 Garden Scan Results for '{args.pattern}':")
        print(f"Total keys: {result['total_keys']}")
        
        categories = result['categories']
        emojis = {'flowers': '🌸', 'trees': '🌳', 'streams': '🌊', 'lists': '📝', 'other': '🔧'}
        
        for category, keys in categories.items():
            if keys:
                print(f"\\n{emojis.get(category, '🔧')} {category.title()} ({len(keys)}):")
                for key in keys:
                    print(f"  - {key}")
                    
        if musical_ledger:
            musical_ledger.add_team_activity("♠️", "garden_scan", f"CLI garden scan: {args.pattern}")
    else:
        keys = client.scan_keys(args.pattern)
        print(f"🔑 Found {len(keys)} keys matching '{args.pattern}':")
        for key in keys:
            print(key)
            
        if musical_ledger:
            musical_ledger.add_team_activity("♠️", "scan_keys", f"CLI scan: {args.pattern}")


def handle_list_operations(args, operations: RedisOperations, musical_ledger: Optional[MusicalLedger]) -> None:
    """Handle list operations."""
    if args.list_command == 'push':
        direction = "right" if args.right else "left"
        success = operations.push_list(args.list_name, args.element, direction)
        if success:
            print(f"✅ Pushed '{args.element}' to {direction} of {args.list_name}")
            if musical_ledger:
                musical_ledger.add_team_activity("🧵", "push_list", f"CLI push: {args.list_name}")
        else:
            print(f"❌ Failed to push to {args.list_name}")
            sys.exit(1)
            
    elif args.list_command == 'read':
        elements = operations.read_list(args.list_name, args.start, args.stop)
        if elements:
            print(f"📋 List {args.list_name} [{args.start}:{args.stop}]:")
            for i, element in enumerate(elements):
                print(f"{args.start + i}: {element}")
            if musical_ledger:
                musical_ledger.add_team_activity("🧵", "read_list", f"CLI read: {args.list_name}")
        else:
            print(f"📭 List {args.list_name} is empty or doesn't exist")


def handle_stream_operations(args, operations: RedisOperations, musical_ledger: Optional[MusicalLedger]) -> None:
    """Handle stream operations.""" 
    if args.stream_command == 'diary':
        if args.action == 'add':
            if not args.event:
                print("❌ Event description required for diary add")
                sys.exit(1)
                
            stream_id = operations.add_diary_entry(
                diary_name=args.name,
                event=args.event,
                mood=args.mood or ""
            )
            if stream_id:
                print(f"📖 Added diary entry: {stream_id}")
                if musical_ledger:
                    musical_ledger.add_team_activity("🌿", "diary_add", f"CLI diary: {args.event[:30]}...")
            else:
                print("❌ Failed to add diary entry")
                sys.exit(1)
                
        elif args.action == 'read':
            entries = operations.read_diary(args.name, args.count)
            if entries:
                print(f"📚 {args.name} (last {len(entries)} entries):")
                for entry in entries:
                    fields = entry.get('fields', {})
                    print(f"\\n🕒 {entry.get('id', 'Unknown')}")
                    print(f"   📝 Event: {fields.get('event', 'No event')}")
                    if fields.get('mood'):
                        print(f"   😊 Mood: {fields.get('mood')}")
                if musical_ledger:
                    musical_ledger.add_team_activity("🌿", "diary_read", f"CLI read: {args.name}")
            else:
                print(f"📭 No entries found in {args.name}")


def handle_init_command(args) -> None:
    """Handle environment initialization."""
    import os
    from pathlib import Path
    
    env_file = Path(".env")
    
    # Check if .env already exists
    if env_file.exists() and not args.force:
        print("❌ .env file already exists. Use --force to overwrite.")
        sys.exit(1)
    
    print("🚀 Initializing Nyro environment...")
    
    # Create sample .env file
    env_content = """# Nyro Redis Configuration
# ♠️🌿🎸🧵 G.Music Assembly Environment Setup

# Default Redis Database
KV_REST_API_URL=https://your-redis-url.upstash.io
KV_REST_API_TOKEN=your_redis_token_here

# Alternative: Redis CLI URL (for direct redis-cli usage)
# REDIS_URL=redis://localhost:6379
# REDIS_URL=rediss://user:password@redis-host.com:6380

# Additional Profile Examples (optional)
# PROFILE_SECONDARY_URL=https://secondary-redis.upstash.io
# PROFILE_SECONDARY_TOKEN=secondary_token_here

# PROFILE_TESTING_URL=https://test-redis.upstash.io  
# PROFILE_TESTING_TOKEN=test_token_here

# Nyro Configuration
TEMP_DIR=/tmp/nyro-temp
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with sample configuration")
    print("📝 Please edit .env file with your actual Redis credentials:")
    print(f"   - URL: Your Upstash Redis REST API URL")
    print(f"   - TOKEN: Your Upstash Redis REST API token")
    print()
    print("🎯 Quick start:")
    print("   1. Edit .env with your credentials")
    print("   2. Run: nyro test")
    print("   3. Run: nyro interactive")
    print()
    print("🎼 Musical integration enabled by default!")
    

def handle_profile_management(args, profile_manager: ProfileManager, musical_ledger: Optional[MusicalLedger]) -> None:
    """Handle profile management."""
    if args.action == 'list':
        profiles = profile_manager.list_profiles()
        current = profile_manager.current_profile
        
        print("📋 Available Profiles:")
        for name, config in profiles.items():
            status = " ⭐ (current)" if name == current else ""
            print(f"  🔗 {name}{status}")
            print(f"     URL: {config.url}")
            
    elif args.action == 'switch':
        if not args.name:
            print("❌ Profile name required for switch")
            sys.exit(1)
            
        success = profile_manager.switch_profile(args.name)
        if success:
            print(f"✅ Switched to profile: {args.name}")
            if musical_ledger:
                musical_ledger.add_team_activity("🧵", "switch_profile", f"CLI switch: {args.name}")
        else:
            print(f"❌ Profile '{args.name}' not found")
            sys.exit(1)
            
    elif args.action == 'current':
        current = profile_manager.get_current_profile()
        if current:
            print(f"📊 Current Profile: {current.name}")
            print(f"  🔗 URL: {current.url}")
            print(f"  📝 Description: {current.description or 'No description'}")
        else:
            print("❌ No active profile")


def main():
    """Main entry point for Nyro CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle no command (show help)
    if not args.command:
        parser.print_help()
        return
    
    # Handle init command (no profile manager needed)
    if args.command == 'init':
        handle_init_command(args)
        return
    
    # Initialize components
    try:
        profile_manager = ProfileManager()
        
        # Switch profile if specified
        if args.profile:
            if not profile_manager.switch_profile(args.profile):
                print(f"❌ Profile '{args.profile}' not found")
                sys.exit(1)
        
        client = RedisClient(profile_manager)
        operations = RedisOperations(client)
        
        # Initialize musical ledger if requested
        musical_ledger = None
        if args.musical:
            musical_ledger = MusicalLedger()
            musical_ledger.start_session(f"♠️🌿🎸🧵 Nyro CLI Session")
            
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        sys.exit(1)
    
    # Route to appropriate handler
    try:
        if args.command in ['interactive', 'i']:
            cli = InteractiveCLI()
            cli.run()
            
        elif args.command in ['set', 'get', 'del']:
            handle_basic_operations(args, client, musical_ledger)
            
        elif args.command == 'scan':
            handle_scanning(args, client, operations, musical_ledger)
            
        elif args.command == 'list':
            handle_list_operations(args, operations, musical_ledger)
            
        elif args.command == 'stream':
            handle_stream_operations(args, operations, musical_ledger)
            
        elif args.command == 'profiles':
            handle_profile_management(args, profile_manager, musical_ledger)
            
        elif args.command == 'music':
            if not musical_ledger:
                musical_ledger = MusicalLedger()
                
            if args.action == 'summary':
                summary = musical_ledger.generate_session_summary(args.session)
                print(summary)
            elif args.action == 'export':
                abc_file = musical_ledger.export_abc_file(args.session)
                print(f"🎼 Exported to: {abc_file}")
                
        elif args.command == 'test':
            connection_ok = client.test_connection()
            if connection_ok:
                print("✅ Connection successful!")
                if musical_ledger:
                    musical_ledger.add_team_activity("🧵", "test_connection", "CLI test: OK")
            else:
                print("❌ Connection failed!")
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\\n🛑 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()