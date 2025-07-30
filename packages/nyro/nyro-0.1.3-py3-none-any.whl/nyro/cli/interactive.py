"""
Interactive CLI Module
♠️ Nyro: Consolidating all interactive menu patterns

Unifies functionality from:
- menu.sh (basic Redis utilities menu)
- redis-mobile.sh (1000+ line enhanced menu system)
- Profile switching and garden metaphors
"""

import os
import sys
from typing import Optional, Dict, Any
import json
from pathlib import Path

from ..core.client import RedisClient  
from ..core.profiles import ProfileManager
from ..core.operations import RedisOperations
from ..musical.ledger import MusicalLedger


class InteractiveCLI:
    """Interactive CLI consolidating all bash script menu systems."""
    
    def __init__(self):
        """Initialize interactive CLI."""
        self.profile_manager = ProfileManager()
        self.client = RedisClient(self.profile_manager)
        self.operations = RedisOperations(self.client)
        self.musical_ledger = MusicalLedger()
        self.running = True
        
        # Start musical session
        self.session_id = self.musical_ledger.start_session("♠️🌿🎸🧵 Nyro Interactive Session")
    
    def display_header(self) -> None:
        """Display CLI header."""
        print("\\n" + "="*60)
        print("🌿 Nyro Redis Utilities - Unified Interactive CLI")
        print("♠️🌿🎸🧵 G.Music Assembly Consolidated Interface")
        print("="*60)
        
        current_profile = self.profile_manager.current_profile or "none"
        connection_status = "✅ Connected" if self.client.test_connection() else "❌ Disconnected"
        
        print(f"📊 Profile: {current_profile} | {connection_status}")
        print(f"🎼 Session: {self.session_id}")
        print("-" * 60)
    
    def display_main_menu(self) -> None:
        """Display main menu options."""
        print("\\n🎯 Main Menu:")
        print("1️⃣  Basic Operations")
        print("2️⃣  List Operations") 
        print("3️⃣  Stream Operations (Garden Diary)")
        print("4️⃣  Advanced Scanning")
        print("5️⃣  Massive Data Operations")
        print("6️⃣  Profile Management")
        print("7️⃣  Musical Ledger")
        print("8️⃣  Export Operations")
        print("9️⃣  Quick Scan & Test")
        print("🔧 setup - Environment Setup")
        print("❓ help - Show detailed help")
        print("🚪 quit - Exit")
        print()
    
    def handle_basic_operations(self) -> None:
        """Handle basic Redis operations (menu.sh patterns)."""
        while True:
            print("\\n🔧 Basic Operations:")
            print("1) Set a key")
            print("2) Get a key")  
            print("3) Delete a key")
            print("b) Back to main menu")
            
            choice = input("Choose option: ").strip()
            
            if choice == '1':
                key = input("Enter key: ").strip()
                value = input("Enter value: ").strip()
                if key and value:
                    success = self.client.set_key(key, value)
                    if success:
                        print(f"✅ Set {key} = {value}")
                        self.musical_ledger.add_team_activity("🧵", "set_key", f"Set key: {key}")
                    else:
                        print(f"❌ Failed to set {key}")
                        
            elif choice == '2':
                key = input("Enter key to get: ").strip()
                if key:
                    value = self.client.get_key(key)
                    if value is not None:
                        print(f"🔍 {key} = {value}")
                        self.musical_ledger.add_team_activity("🧵", "get_key", f"Retrieved key: {key}")
                    else:
                        print(f"❌ Key '{key}' not found")
                        
            elif choice == '3':
                key = input("Enter key to delete: ").strip()
                if key:
                    success = self.client.delete_key(key)
                    if success:
                        print(f"🗑️ Deleted key: {key}")
                        self.musical_ledger.add_team_activity("🧵", "delete_key", f"Deleted key: {key}")
                    else:
                        print(f"❌ Failed to delete {key}")
                        
            elif choice == 'b':
                break
            else:
                print("❌ Invalid option")
    
    def handle_list_operations(self) -> None:
        """Handle list operations (push-list.sh, read-list.sh patterns)."""
        while True:
            print("\\n📝 List Operations:")
            print("1) Push to list")
            print("2) Read from list")
            print("3) Get list length")
            print("b) Back to main menu")
            
            choice = input("Choose option: ").strip()
            
            if choice == '1':
                list_name = input("Enter list name: ").strip()
                element = input("Enter element: ").strip()
                direction = input("Push direction (left/right, default left): ").strip() or "left"
                
                if list_name and element:
                    success = self.operations.push_list(list_name, element, direction)
                    if success:
                        print(f"✅ Pushed '{element}' to {direction} of {list_name}")
                        self.musical_ledger.add_team_activity("🧵", "push_list", f"Pushed to list: {list_name}")
                    else:
                        print(f"❌ Failed to push to {list_name}")
                        
            elif choice == '2':
                list_name = input("Enter list name: ").strip()
                start = input("Start index (default 0): ").strip()
                stop = input("Stop index (default 10): ").strip()
                
                start_idx = int(start) if start else 0
                stop_idx = int(stop) if stop else 10
                
                if list_name:
                    elements = self.operations.read_list(list_name, start_idx, stop_idx)
                    if elements:
                        print(f"📋 List {list_name} [{start_idx}:{stop_idx}]:")
                        for i, element in enumerate(elements):
                            print(f"  {start_idx + i}: {element}")
                        self.musical_ledger.add_team_activity("🧵", "read_list", f"Read from list: {list_name}")
                    else:
                        print(f"📭 List {list_name} is empty or doesn't exist")
                        
            elif choice == '3':
                list_name = input("Enter list name: ").strip()
                if list_name:
                    length = self.operations.get_list_length(list_name)
                    print(f"📏 List {list_name} length: {length}")
                    
            elif choice == 'b':
                break
            else:
                print("❌ Invalid option")
    
    def handle_stream_operations(self) -> None:
        """Handle stream operations (stream-add.sh, stream-read.sh patterns)."""
        while True:
            print("\\n🌊 Stream Operations (Garden Diary):")
            print("1) Write in garden diary")
            print("2) Read garden diary")
            print("3) Add custom stream entry")
            print("4) Read custom stream")
            print("b) Back to main menu")
            
            choice = input("Choose option: ").strip()
            
            if choice == '1':
                diary_name = input("Enter diary name (default garden.diary): ").strip() or "garden.diary"
                event = input("Enter what happened: ").strip()
                mood = input("Enter mood (optional): ").strip()
                details = input("Enter extra details (optional): ").strip()
                
                if event:
                    stream_id = self.operations.add_diary_entry(
                        diary_name=diary_name,
                        event=event,
                        mood=mood,
                        details=details
                    )
                    if stream_id:
                        print(f"📖 Added diary entry: {stream_id}")
                        self.musical_ledger.add_team_activity("🌿", "diary_entry", f"Garden diary: {event[:30]}...")
                    else:
                        print("❌ Failed to add diary entry")
                        
            elif choice == '2':
                diary_name = input("Enter diary name (default garden.diary): ").strip() or "garden.diary"
                count = input("How many entries? (default 10): ").strip()
                count_num = int(count) if count else 10
                
                entries = self.operations.read_diary(diary_name, count_num)
                if entries:
                    print(f"\\n📚 {diary_name} (last {len(entries)} entries):")
                    for entry in entries:
                        fields = entry.get('fields', {})
                        print(f"  🕒 {entry.get('id', 'Unknown')}")
                        print(f"     📝 Event: {fields.get('event', 'No event')}")
                        if fields.get('mood'):
                            print(f"     😊 Mood: {fields.get('mood')}")
                        if fields.get('details'):
                            print(f"     ℹ️  Details: {fields.get('details')}")
                        print()
                    self.musical_ledger.add_team_activity("🌿", "read_diary", f"Read {diary_name}")
                else:
                    print(f"📭 No entries found in {diary_name}")
                    
            elif choice == '3':
                stream_name = input("Enter stream name: ").strip()
                if stream_name:
                    fields = {}
                    print("Enter fields (empty field name to finish):")
                    while True:
                        field_name = input("Field name: ").strip()
                        if not field_name:
                            break
                        field_value = input(f"Value for {field_name}: ").strip()
                        fields[field_name] = field_value
                    
                    if fields:
                        stream_id = self.operations.stream_add(stream_name, fields)
                        if stream_id:
                            print(f"✅ Added stream entry: {stream_id}")
                            self.musical_ledger.add_team_activity("🧵", "stream_add", f"Stream: {stream_name}")
                        else:
                            print("❌ Failed to add stream entry")
                            
            elif choice == '4':
                stream_name = input("Enter stream name: ").strip()
                count = input("How many entries? (default 10): ").strip()
                count_num = int(count) if count else 10
                
                if stream_name:
                    entries = self.operations.stream_read(stream_name, count_num)
                    if entries:
                        print(f"\\n🌊 Stream {stream_name}:")
                        for entry in entries:
                            print(f"  📋 {entry.get('id', 'Unknown')}")
                            fields = entry.get('fields', {})
                            for field, value in fields.items():
                                print(f"     {field}: {value}")
                            print()
                        self.musical_ledger.add_team_activity("🧵", "stream_read", f"Read stream: {stream_name}")
                    else:
                        print(f"📭 No entries found in {stream_name}")
                        
            elif choice == 'b':
                break
            else:
                print("❌ Invalid option")
    
    def handle_scanning(self) -> None:
        """Handle advanced scanning (scan-garden.sh patterns)."""
        while True:
            print("\\n🔍 Garden Scanning:")
            print("1) Simple key scan")
            print("2) Garden scan (categorized)")
            print("3) Pattern search")
            print("b) Back to main menu")
            
            choice = input("Choose option: ").strip()
            
            if choice == '1':
                pattern = input("Enter pattern (default *): ").strip() or "*"
                keys = self.client.scan_keys(pattern)
                print(f"\\n🔑 Found {len(keys)} keys matching '{pattern}':")
                for key in keys[:20]:  # Limit display
                    print(f"  - {key}")
                if len(keys) > 20:
                    print(f"  ... and {len(keys) - 20} more")
                self.musical_ledger.add_team_activity("♠️", "scan_keys", f"Scanned pattern: {pattern}")
                
            elif choice == '2':
                pattern = input("Enter pattern (default *): ").strip() or "*"
                garden_result = self.operations.scan_garden(pattern)
                
                print(f"\\n🌿 Garden Scan Results for '{pattern}':")
                print(f"🌸 Total keys found: {garden_result['total_keys']}")
                print()
                
                categories = garden_result['categories']
                for category, keys in categories.items():
                    if keys:
                        emoji = {'flowers': '🌸', 'trees': '🌳', 'streams': '🌊', 'lists': '📝', 'other': '🔧'}
                        print(f"{emoji.get(category, '🔧')} {category.title()}: {len(keys)} keys")
                        for key in keys[:5]:  # Show first 5
                            print(f"    - {key}")
                        if len(keys) > 5:
                            print(f"    ... and {len(keys) - 5} more")
                        print()
                
                self.musical_ledger.add_team_activity("♠️", "garden_scan", f"Garden scan: {pattern}")
                
            elif choice == '3':
                print("Pattern examples: user:*, *:config, temp:*")
                pattern = input("Enter search pattern: ").strip()
                if pattern:
                    keys = self.client.scan_keys(pattern)
                    print(f"\\n🎯 Pattern '{pattern}' matches {len(keys)} keys:")
                    for key in keys:
                        value_preview = ""
                        value = self.client.get_key(key)
                        if value and len(str(value)) > 50:
                            value_preview = f" = {str(value)[:50]}..."
                        elif value:
                            value_preview = f" = {value}"
                        print(f"  🔑 {key}{value_preview}")
                    
            elif choice == 'b':
                break
            else:
                print("❌ Invalid option")
    
    def handle_profile_management(self) -> None:
        """Handle profile management."""
        while True:
            print("\\n👤 Profile Management:")
            print("1) List profiles")
            print("2) Switch profile")
            print("3) Current profile info")
            print("4) Test connection")
            print("b) Back to main menu")
            
            choice = input("Choose option: ").strip()
            
            if choice == '1':
                profiles = self.profile_manager.list_profiles()
                current = self.profile_manager.current_profile
                
                print("\\n📋 Available Profiles:")
                for name, config in profiles.items():
                    status = " ⭐ (current)" if name == current else ""
                    print(f"  🔗 {name}{status}")
                    print(f"     URL: {config.url}")
                    print(f"     Description: {config.description or 'No description'}")
                    print()
                    
            elif choice == '2':
                profiles = self.profile_manager.list_profiles()
                print("\\n🔄 Available profiles:")
                for name in profiles.keys():
                    print(f"  - {name}")
                
                profile_name = input("Enter profile name: ").strip()
                if profile_name in profiles:
                    success = self.client.switch_profile(profile_name)
                    if success:
                        print(f"✅ Switched to profile: {profile_name}")
                        self.musical_ledger.add_team_activity("🧵", "switch_profile", f"Switched to: {profile_name}")
                    else:
                        print(f"❌ Failed to switch to {profile_name}")
                else:
                    print(f"❌ Profile '{profile_name}' not found")
                    
            elif choice == '3':
                current = self.profile_manager.get_current_profile()
                if current:
                    print(f"\\n📊 Current Profile: {current.name}")
                    print(f"  🔗 URL: {current.url}")
                    print(f"  🔑 Token: {'*' * 8}...{current.token[-4:] if len(current.token) > 4 else '****'}")
                    print(f"  📝 Description: {current.description or 'No description'}")
                else:
                    print("❌ No active profile")
                    
            elif choice == '4':
                connection_ok = self.client.test_connection()
                if connection_ok:
                    print("✅ Connection successful!")
                    self.musical_ledger.add_team_activity("🧵", "test_connection", "Connection test: OK")
                else:
                    print("❌ Connection failed!")
                    
            elif choice == 'b':
                break
            else:
                print("❌ Invalid option")
    
    def run(self) -> None:
        """Run the interactive CLI."""
        try:
            print("🎼 Starting ♠️🌿🎸🧵 Nyro Interactive Session...")
            self.musical_ledger.add_team_activity("🎸", "session_start", "Interactive CLI session started")
            
            while self.running:
                self.display_header()
                self.display_main_menu()
                
                choice = input("Choose option: ").strip().lower()
                
                if choice == '1':
                    self.handle_basic_operations()
                elif choice == '2':
                    self.handle_list_operations()
                elif choice == '3':
                    self.handle_stream_operations()
                elif choice == '4':
                    self.handle_scanning()
                elif choice == '5':
                    print("🚧 Massive data operations - Coming soon!")
                elif choice == '6':
                    self.handle_profile_management()
                elif choice == '7':
                    summary = self.musical_ledger.generate_session_summary()
                    print(summary)
                elif choice == '8':
                    print("🚧 Export operations - Coming soon!")
                elif choice == '9':
                    # Quick test
                    print("\\n🚀 Quick Connection Test...")
                    if self.client.test_connection():
                        keys = self.client.scan_keys("*", 5)
                        print(f"✅ Connected! Found {len(keys)} sample keys")
                        self.musical_ledger.add_team_activity("🧵", "quick_test", "Quick test successful")
                    else:
                        print("❌ Connection failed!")
                elif choice == 'setup':
                    print("🔧 Environment setup - Check .env file and run install.sh")
                elif choice == 'help':
                    print("\\n📖 Nyro Help - Consolidated Redis operations interface")
                    print("This CLI replaces 13+ bash scripts with unified Python interface")
                    print("\\n🤝 **Want to collaborate?**")
                    print("Create enhancement requests: https://github.com/gerico1007/nyro/issues/new")
                    print("See CONTRIBUTING.md for detailed collaboration guide")
                elif choice in ['quit', 'q', 'exit']:
                    self.running = False
                else:
                    print("❌ Invalid option. Type 'help' for assistance.")
                
                if self.running:
                    input("\\nPress Enter to continue...")
                    
        except KeyboardInterrupt:
            print("\\n\\n🛑 Session interrupted by user")
        finally:
            print("\\n🎼 Ending session...")
            self.musical_ledger.add_team_activity("🎸", "session_end", "Interactive CLI session ended")
            summary = self.musical_ledger.generate_session_summary()
            print("\\n" + summary)
            print("\\n🎵 Session complete! Musical ledger saved.")


def main():
    """Main entry point for interactive CLI."""
    cli = InteractiveCLI()
    cli.run()


if __name__ == "__main__":
    main()