import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import redis

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../app'))

import indexer
import common

class TestIndexer(unittest.TestCase):
    
    @patch('indexer.r')
    def test_create_index_recreates_on_dim_mismatch(self, mock_redis):
        # Setup: FT.INFO returns structure with DIM 384 (mismatch with 768)
        # Structure is roughly what execute_command returns (nested lists)
        # [..., 'attributes', [..., 'DIM', 384, ...], ...]
        # We simulate finding 'DIM', 384
        
        # Mock execute_command
        def side_effect(*args, **kwargs):
            cmd = args[0]
            if cmd == "FT.INFO":
                # Return list with DIM 384
                return [b'attributes', [b'type', b'VECTOR', b'DIM', 384]]
            elif cmd == "FT.DROPINDEX":
                return "OK"
            elif cmd == "FT.CREATE":
                return "OK"
            return None
            
        mock_redis.execute_command.side_effect = side_effect
        
        # We also need to mock common.EMBEDDING_DIM if it was imported differently,
        # but here we rely on common.EMBEDDING_DIM being 768 (which we verified in test_common).
        # indexer imports EMBEDDING_DIM from common.
        
        indexer.create_index()
        
        # Verify FT.DROPINDEX was called
        mock_redis.execute_command.assert_any_call("FT.DROPINDEX", indexer.INDEX_NAME)
        
        # Verify FT.CREATE was called with DIM 768
        # We need to find the call
        create_calls = [call for call in mock_redis.execute_command.call_args_list if call[0][0] == "FT.CREATE"]
        self.assertTrue(len(create_calls) > 0)
        args = create_calls[0][0]
        self.assertIn(str(common.EMBEDDING_DIM), args) # "768"

    @patch('indexer.r')
    def test_create_index_skips_if_dim_match(self, mock_redis):
        # Setup: FT.INFO returns DIM 768
        def side_effect(*args, **kwargs):
            cmd = args[0]
            if cmd == "FT.INFO":
                return [b'attributes', [b'DIM', 768]]
            return None
            
        mock_redis.execute_command.side_effect = side_effect
        
        indexer.create_index()
        
        # Verify FT.DROPINDEX NOT called
        drop_calls = [call for call in mock_redis.execute_command.call_args_list if call[0][0] == "FT.DROPINDEX"]
        self.assertEqual(len(drop_calls), 0)
        
        # Verify FT.CREATE NOT called
        create_calls = [call for call in mock_redis.execute_command.call_args_list if call[0][0] == "FT.CREATE"]
        self.assertEqual(len(create_calls), 0)

if __name__ == '__main__':
    unittest.main()
