import unittest
from unittest.mock import patch, Mock
import numpy as np
import os
import sys

# Add app directory to path to import common
sys.path.append(os.path.join(os.path.dirname(__file__), '../app'))

import common

class TestCommon(unittest.TestCase):
    
    def test_embedding_dim_is_768(self):
        self.assertEqual(common.EMBEDDING_DIM, 768)

    @patch('common.requests.post')
    def test_embed_text_calls_ollama(self, mock_post):
        # Override the module-level variable
        with patch('common.OLLAMA_BASE_URL', "http://mock-ollama:11434"):
            # Setup mock response
            mock_response = Mock()
            # Ollama API response format for /api/embeddings
            # {"embedding": [0.1, 0.2, ...]}
            fake_embedding = [0.1] * 768
            mock_response.json.return_value = {"embedding": fake_embedding}
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            text = "Hello Ollama"
            # We expect embed_text to be the main function
            vector = common.embed_text(text)

            # Verify result
            self.assertIsInstance(vector, np.ndarray)
            self.assertEqual(vector.shape, (768,))
            self.assertEqual(vector.dtype, np.float32)
            
            # Verify call
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            self.assertTrue(args[0].startswith("http://mock-ollama:11434"))
            self.assertIn("nomic-embed-text", kwargs['json']['model'])
            self.assertEqual(kwargs['json']['prompt'], text)

if __name__ == '__main__':
    unittest.main()
