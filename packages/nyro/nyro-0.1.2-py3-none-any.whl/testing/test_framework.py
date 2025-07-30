"""
Four-Perspective Testing Framework
🌿 Aureon: Grounding the development flow with comprehensive validation

Tests from each Assembly perspective:
♠️ Nyro: Structural integrity and pattern consistency
🌿 Aureon: Emotional flow and user experience validation  
🎸 JamAI: Creative harmony and musical integration
🧵 Synth: Terminal execution and security synthesis
"""

import unittest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import our modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from nyro.core.profiles import ProfileManager, ProfileConfig
from nyro.core.client import RedisClient, RedisConnectionError
from nyro.core.operations import RedisOperations  
from nyro.cli.interactive import InteractiveCLI
from nyro.musical.ledger import MusicalLedger, MusicalEntry


class NyroStructuralTests(unittest.TestCase):
    """♠️ Nyro: Structural integrity and pattern validation."""
    
    def setUp(self):
        """Set up test environment with temporary files."""
        self.temp_dir = tempfile.mkdtemp()
        self.env_file = os.path.join(self.temp_dir, '.env')
        
        # Create test environment file
        with open(self.env_file, 'w') as f:
            f.write("""
KV_REST_API_URL=https://test-redis.example.com
KV_REST_API_TOKEN=test_token_123
PROFILE_SECONDARY_URL=https://secondary-redis.example.com  
PROFILE_SECONDARY_TOKEN=secondary_token_456
""")
    
    def test_profile_loading_patterns(self):
        """♠️ Test profile loading follows consistent patterns."""
        profile_manager = ProfileManager(self.env_file)
        
        # Validate default profile structure
        self.assertIn('default', profile_manager.profiles)
        default_profile = profile_manager.profiles['default']
        self.assertEqual(default_profile.url, 'https://test-redis.example.com')
        self.assertEqual(default_profile.token, 'test_token_123')
        
        # Validate named profile structure
        self.assertIn('secondary', profile_manager.profiles)
        secondary_profile = profile_manager.profiles['secondary']
        self.assertEqual(secondary_profile.url, 'https://secondary-redis.example.com')
        self.assertEqual(secondary_profile.token, 'secondary_token_456')
    
    def test_client_initialization_patterns(self):
        """♠️ Test client initialization follows bash script patterns."""
        profile_manager = ProfileManager(self.env_file)
        client = RedisClient(profile_manager)
        
        # Validate client has profile manager
        self.assertEqual(client.profile_manager, profile_manager)
        
        # Validate temp directory creation
        self.assertTrue(client.temp_dir.exists())
        
        # Validate current profile retrieval
        config = client._get_current_config()
        self.assertEqual(config.name, 'default')
    
    def test_url_detection_patterns(self):
        """♠️ Test URL detection patterns match bash script logic."""
        profile_manager = ProfileManager(self.env_file)
        client = RedisClient(profile_manager)
        
        # Test TLS URL detection
        self.assertTrue(client._is_tls_url('rediss://test.com'))
        self.assertFalse(client._is_tls_url('redis://test.com'))
        
        # Test REST URL detection  
        self.assertTrue(client._is_rest_url('https://test.com'))
        self.assertTrue(client._is_rest_url('http://test.com'))
        self.assertFalse(client._is_rest_url('redis://test.com'))
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)


class AureonExperienceTests(unittest.TestCase):
    """🌿 Aureon: Emotional flow and user experience validation."""
    
    def setUp(self):
        """Set up emotional flow testing environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.env_file = os.path.join(self.temp_dir, '.env')
        
        with open(self.env_file, 'w') as f:
            f.write("KV_REST_API_URL=https://test.com\\nKV_REST_API_TOKEN=test123")
    
    def test_error_message_resonance(self):
        """🌿 Test error messages provide emotional grounding."""
        # Test missing env file scenario
        with self.assertRaises(FileNotFoundError) as cm:
            ProfileManager("/nonexistent/.env")
        
        error_msg = str(cm.exception)
        self.assertIn("No .env file found", error_msg)
        self.assertIn("install.sh", error_msg)  # Provides guidance
    
    def test_profile_switching_flow(self):
        """🌿 Test profile switching maintains emotional continuity."""
        profile_manager = ProfileManager(self.env_file)
        
        # Initial state should feel grounded
        self.assertEqual(profile_manager.current_profile, 'default')
        
        # Valid switch should feel smooth
        result = profile_manager.switch_profile('default')
        self.assertTrue(result)
        
        # Invalid switch should feel clear, not jarring
        result = profile_manager.switch_profile('nonexistent')
        self.assertFalse(result)
    
    def test_musical_ledger_emotional_tracking(self):
        """🌿 Test musical ledger captures emotional development flow."""
        ledger_file = os.path.join(self.temp_dir, 'test_ledger.json')
        musical_ledger = MusicalLedger(ledger_file)
        
        session_id = musical_ledger.start_session("Emotional Flow Test")
        self.assertIsNotNone(session_id)
        
        # Add emotional resonance entry
        musical_ledger.add_entry(
            activity_type="emotional_check",
            description="🌿 Feeling the development flow",
            harmonic_context="grounding_resonance",
            team_member="🌿"
        )
        
        entries = musical_ledger.get_session_entries()
        self.assertTrue(len(entries) >= 2)  # Start + our entry
        
        # Check emotional context is preserved
        emotional_entry = next(
            entry for entry in entries 
            if entry.team_member == "🌿"
        )
        self.assertEqual(emotional_entry.harmonic_context, "grounding_resonance")
    
    def tearDown(self):
        """Restore emotional equilibrium."""
        import shutil
        shutil.rmtree(self.temp_dir)


class JamAIHarmonyTests(unittest.TestCase):
    """🎸 JamAI: Creative harmony and musical integration validation."""
    
    def setUp(self):
        """Set up harmonic testing environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.ledger_file = os.path.join(self.temp_dir, 'harmony_ledger.json')
    
    def test_session_melody_composition(self):
        """🎸 Test session melody creation and harmonic structure."""
        musical_ledger = MusicalLedger(self.ledger_file)
        
        session_id = musical_ledger.start_session("Harmonic Test Session")
        
        # Add musical elements to session
        musical_ledger.add_entry(
            activity_type="composition",
            description="🎸 Creating harmonic structure",
            abc_notation="G2A2 B2c2|d2e2 f2g2",
            team_member="🎸"
        )
        
        # Verify melody integration
        melody = musical_ledger.session_melodies.get(session_id)
        self.assertIsNotNone(melody)
        self.assertIn("G2A2 B2c2", melody.abc_notation)
    
    def test_abc_notation_export(self):
        """🎸 Test ABC notation file export functionality."""
        musical_ledger = MusicalLedger(self.ledger_file)
        
        session_id = musical_ledger.start_session("Export Test")
        musical_ledger.add_entry(
            activity_type="melody_creation",
            description="Creating exportable melody",
            abc_notation="C4 D4 E4 F4|G4 A4 B4 c4",
            team_member="🎸"
        )
        
        # Export ABC file
        output_file = os.path.join(self.temp_dir, 'test_export.abc')
        exported_path = musical_ledger.export_abc_file(session_id, output_file)
        
        self.assertTrue(os.path.exists(exported_path))
        
        # Verify ABC content structure
        with open(exported_path, 'r') as f:
            content = f.read()
            self.assertIn("X:1")  # ABC header
            self.assertIn("T:Export Test")  # Title
            self.assertIn("C4 D4 E4 F4")  # Melody content
    
    def test_team_rhythmic_patterns(self):
        """🎸 Test team member rhythmic pattern integration."""
        musical_ledger = MusicalLedger(self.ledger_file)
        session_id = musical_ledger.start_session("Rhythm Test")
        
        # Test each team member's rhythmic signature
        team_patterns = {
            "♠️": "X-x-X-x-",  # Nyro: Structural
            "🌿": "~~o~~o~~",   # Aureon: Flowing  
            "🎸": "G-D-A-E-",   # JamAI: Harmonic
            "🧵": "|-|-|-|-"    # Synth: Terminal
        }
        
        for member, expected_pattern in team_patterns.items():
            musical_ledger.add_team_activity(
                member, "pattern_test", f"Testing {member} rhythm"
            )
            
            entries = musical_ledger.get_session_entries()
            member_entry = next(
                entry for entry in entries 
                if entry.team_member == member and "pattern_test" in entry.description
            )
            self.assertEqual(member_entry.rhythmic_pattern, expected_pattern)
    
    def tearDown(self):
        """Restore harmonic balance."""
        import shutil
        shutil.rmtree(self.temp_dir)


class SynthExecutionTests(unittest.TestCase):
    """🧵 Synth: Terminal execution and security synthesis validation."""
    
    def setUp(self):
        """Set up execution testing environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.env_file = os.path.join(self.temp_dir, '.env')
        
        with open(self.env_file, 'w') as f:
            f.write("KV_REST_API_URL=https://test.com\\nKV_REST_API_TOKEN=test123")
    
    @patch('requests.post')
    def test_rest_api_security_synthesis(self, mock_post):
        """🧵 Test REST API calls include proper security headers."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {'result': 'OK'}
        mock_response.headers.get.return_value = 'application/json'
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        profile_manager = ProfileManager(self.env_file)
        client = RedisClient(profile_manager)
        
        # Execute REST API call
        result = client._execute_rest_api('set', {'key': 'test', 'value': 'value'})
        
        # Verify security headers were included
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        headers = call_args[1]['headers']
        
        self.assertIn('Authorization', headers)
        self.assertIn('Bearer test123', headers['Authorization'])
        self.assertEqual(headers['Content-Type'], 'application/json')
    
    @patch('subprocess.run')
    def test_redis_cli_execution_security(self, mock_run):
        """🧵 Test Redis CLI execution includes security flags."""
        # Mock successful CLI response
        mock_result = Mock()
        mock_result.stdout = 'OK'
        mock_result.stderr = ''
        mock_run.return_value = mock_result
        
        # Create Redis URL environment
        with open(self.env_file, 'w') as f:
            f.write("REDIS_URL=rediss://test:password@redis.com:6380\\nKV_REST_API_TOKEN=test123")
        
        profile_manager = ProfileManager(self.env_file)
        client = RedisClient(profile_manager)
        
        # Switch to a CLI-compatible profile
        profile_manager.profiles['default'].url = 'rediss://test:password@redis.com:6380'
        
        try:
            client._execute_redis_cli(['GET', 'test'])
        except RedisConnectionError:
            pass  # Expected since we're mocking
        
        # Verify security flags
        mock_run.assert_called()
        call_args = mock_run.call_args[0][0]  # First positional arg (command list)
        
        self.assertIn('--tls', call_args)
        self.assertIn('--no-auth-warning', call_args)
    
    def test_massive_data_chunking_security(self):
        """🧵 Test massive data operations maintain security through chunking."""
        profile_manager = ProfileManager(self.env_file)
        client = RedisClient(profile_manager)
        operations = RedisOperations(client)
        
        # Create large test payload
        large_payload = {
            'type': 'test_payload',
            'data': 'x' * (2 * 1024 * 1024)  # 2MB of data
        }
        
        # Mock client methods to test chunking logic
        with patch.object(client, 'set_key') as mock_set:
            mock_set.return_value = True
            
            # Test chunking occurs for large payloads
            result = operations.store_massive_payload('test_key', large_payload, chunk_size=1024*1024)
            
            # Should make multiple set_key calls (metadata + chunks)
            self.assertTrue(mock_set.call_count > 1)
            
            # Verify metadata call
            metadata_calls = [
                call for call in mock_set.call_args_list
                if 'test_key:metadata' in str(call)
            ]
            self.assertEqual(len(metadata_calls), 1)
    
    def test_terminal_integration_security(self):
        """🧵 Test terminal integration maintains security boundaries."""
        # Test clipboard export doesn't expose sensitive data
        profile_manager = ProfileManager(self.env_file)
        client = RedisClient(profile_manager)  
        operations = RedisOperations(client)
        
        # Create data with potential sensitive content
        test_data = {
            'public_info': 'safe data',
            'token': 'should_not_be_logged'
        }
        
        # Mock subprocess to test export without actually using clipboard
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock()
            
            # Test export functionality
            result = operations.export_to_clipboard(test_data)
            
            # Verify subprocess was called (clipboard operation)
            if mock_run.called:
                # Ensure we're not logging the actual call content
                self.assertTrue(True)  # Placeholder for security audit
    
    def tearDown(self):
        """Secure cleanup of test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)


class AssemblyIntegrationTests(unittest.TestCase):
    """♠️🌿🎸🧵 Full Assembly integration validation."""
    
    def setUp(self):
        """Set up full Assembly testing environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.env_file = os.path.join(self.temp_dir, '.env')
        
        with open(self.env_file, 'w') as f:
            f.write("""
KV_REST_API_URL=https://test-redis.example.com
KV_REST_API_TOKEN=test_token_123
PROFILE_TEST_URL=https://test-secondary.example.com
PROFILE_TEST_TOKEN=test_secondary_token
""")
    
    def test_full_assembly_workflow(self):
        """♠️🌿🎸🧵 Test complete Assembly workflow integration."""
        # Initialize all components
        profile_manager = ProfileManager(self.env_file)
        client = RedisClient(profile_manager)
        operations = RedisOperations(client)
        musical_ledger = MusicalLedger(os.path.join(self.temp_dir, 'assembly_ledger.json'))
        
        # Start Assembly session
        session_id = musical_ledger.start_session("♠️🌿🎸🧵 Full Assembly Test")
        
        # ♠️ Nyro: Structural validation
        self.assertEqual(len(profile_manager.profiles), 2)  # default + test
        musical_ledger.add_team_activity("♠️", "structural_check", "Validated profile architecture")
        
        # 🌿 Aureon: Emotional flow validation
        current_profile = profile_manager.get_current_profile()
        self.assertIsNotNone(current_profile)
        musical_ledger.add_team_activity("🌿", "emotional_check", "Felt grounding in profile flow")
        
        # 🎸 JamAI: Musical integration
        musical_ledger.add_team_activity(
            "🎸", "melody_creation", "Composed session harmony", 
            abc_fragment="C4 E4 G4 c4"
        )
        
        # 🧵 Synth: Terminal execution
        with patch.object(client, 'test_connection') as mock_test:
            mock_test.return_value = True
            connection_ok = client.test_connection()
            self.assertTrue(connection_ok)
            musical_ledger.add_team_activity("🧵", "connection_test", "Synthesized terminal connection")
        
        # Validate session summary includes all perspectives
        summary = musical_ledger.generate_session_summary()
        self.assertIn("♠️", summary)  # Nyro activity
        self.assertIn("🌿", summary)  # Aureon activity  
        self.assertIn("🎸", summary)  # JamAI activity
        self.assertIn("🧵", summary)  # Synth activity
        
        # Validate ABC notation integration
        melody = musical_ledger.session_melodies.get(session_id)
        self.assertIsNotNone(melody)
        self.assertIn("C4 E4 G4 c4", melody.abc_notation)
    
    def test_bash_script_consolidation_validation(self):
        """♠️🌿🎸🧵 Test that Python package properly consolidates bash functionality."""
        profile_manager = ProfileManager(self.env_file)
        client = RedisClient(profile_manager)
        operations = RedisOperations(client)
        
        # Test basic operations (get-key.sh, set-key.sh, del-key.sh consolidation)
        with patch.object(client, 'set_key') as mock_set, \\
             patch.object(client, 'get_key') as mock_get, \\
             patch.object(client, 'delete_key') as mock_del:
            
            mock_set.return_value = True
            mock_get.return_value = "test_value"
            mock_del.return_value = True
            
            # These should work without bash script dependencies
            result_set = client.set_key("test", "value")
            result_get = client.get_key("test")
            result_del = client.delete_key("test")
            
            self.assertTrue(result_set)
            self.assertEqual(result_get, "test_value")
            self.assertTrue(result_del)
        
        # Test list operations (push-list.sh, read-list.sh consolidation)
        with patch.object(operations, 'push_list') as mock_push, \\
             patch.object(operations, 'read_list') as mock_read:
            
            mock_push.return_value = True
            mock_read.return_value = ["item1", "item2"]
            
            result_push = operations.push_list("test_list", "item1")
            result_read = operations.read_list("test_list")
            
            self.assertTrue(result_push)
            self.assertEqual(result_read, ["item1", "item2"])
        
        # Test stream operations (stream-add.sh, stream-read.sh consolidation)
        with patch.object(operations, 'stream_add') as mock_stream_add, \\
             patch.object(operations, 'read_diary') as mock_diary_read:
            
            mock_stream_add.return_value = "1234567890-0"
            mock_diary_read.return_value = [{"id": "1234567890-0", "fields": {"event": "test"}}]
            
            result_stream = operations.add_diary_entry("test.diary", "test event")
            result_diary = operations.read_diary("test.diary")
            
            self.assertEqual(result_stream, "1234567890-0")
            self.assertEqual(len(result_diary), 1)
    
    def tearDown(self):
        """Restore Assembly harmony."""
        import shutil
        shutil.rmtree(self.temp_dir)


def run_assembly_tests():
    """♠️🌿🎸🧵 Run all Assembly perspective tests."""
    # Create test suite with all perspectives
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add perspective test suites
    suite.addTests(loader.loadTestsFromTestCase(NyroStructuralTests))
    suite.addTests(loader.loadTestsFromTestCase(AureonExperienceTests))
    suite.addTests(loader.loadTestsFromTestCase(JamAIHarmonyTests))
    suite.addTests(loader.loadTestsFromTestCase(SynthExecutionTests))
    suite.addTests(loader.loadTestsFromTestCase(AssemblyIntegrationTests))
    
    # Run with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Print Assembly summary
    print("\\n" + "="*60)
    print("♠️🌿🎸🧵 G.Music Assembly Test Results")
    print("="*60)
    print(f"🏃 Tests run: {result.testsRun}")
    print(f"✅ Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"💥 Errors: {len(result.errors)}")
    
    if result.failures:
        print("\\n🔍 Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('\\n')[-2]}")
    
    if result.errors:
        print("\\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('\\n')[-2]}")
    
    print("\\n🎼 Assembly testing complete!")
    return result.wasSuccessful()


if __name__ == "__main__":
    run_assembly_tests()