"""
Automated tests for AI integration API views
"""
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, Mock


class TestAIViews(TestCase):
    """Test AI integration API views"""
    
    def setUp(self):
        """Set up test client and data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # URLs
        self.chat_url = reverse('ai_integration:chat')
        self.search_url = reverse('ai_integration:search')
    
    def test_chat_endpoint_success(self):
        """Test successful chat endpoint request"""
        data = {
            'query': 'Tell me about family traditions'
        }
        
        response = self.client.post(
            self.chat_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        response_data = response.json()
        self.assertIn('query', response_data)
        self.assertIn('response', response_data)
        self.assertIn('sources', response_data)
        self.assertIn('metadata', response_data)
        
        self.assertEqual(response_data['query'], data['query'])
        self.assertIsInstance(response_data['sources'], list)
        self.assertIsInstance(response_data['metadata'], dict)
    
    def test_chat_endpoint_empty_query(self):
        """Test chat endpoint with empty query"""
        data = {
            'query': ''
        }
        
        response = self.client.post(
            self.chat_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['query'], '')
    
    def test_chat_endpoint_missing_query(self):
        """Test chat endpoint with missing query parameter"""
        data = {}
        
        response = self.client.post(
            self.chat_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['query'], '')
    
    def test_chat_endpoint_invalid_json(self):
        """Test chat endpoint with invalid JSON"""
        response = self.client.post(
            self.chat_url,
            data='invalid json{',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('error', response_data)
    
    def test_chat_endpoint_get_method(self):
        """Test chat endpoint with GET method (should fail)"""
        response = self.client.get(self.chat_url)
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
    
    def test_search_endpoint_success(self):
        """Test successful search endpoint request"""
        data = {
            'query': 'family recipes'
        }
        
        response = self.client.post(
            self.search_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        response_data = response.json()
        self.assertIn('query', response_data)
        self.assertIn('results', response_data)
        self.assertIn('count', response_data)
        
        self.assertEqual(response_data['query'], data['query'])
        self.assertIsInstance(response_data['results'], list)
        self.assertIsInstance(response_data['count'], int)
    
    def test_search_endpoint_empty_query(self):
        """Test search endpoint with empty query"""
        data = {
            'query': ''
        }
        
        response = self.client.post(
            self.search_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['query'], '')
        self.assertEqual(response_data['count'], 0)
    
    def test_search_endpoint_missing_query(self):
        """Test search endpoint with missing query parameter"""
        data = {}
        
        response = self.client.post(
            self.search_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['query'], '')
    
    def test_search_endpoint_invalid_json(self):
        """Test search endpoint with invalid JSON"""
        response = self.client.post(
            self.search_url,
            data='invalid json{',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('error', response_data)
    
    def test_search_endpoint_get_method(self):
        """Test search endpoint with GET method (should fail)"""
        response = self.client.get(self.search_url)
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
    
    def test_chat_endpoint_chinese_query(self):
        """Test chat endpoint with Chinese query"""
        data = {
            'query': '告诉我关于家庭传统的故事'
        }
        
        response = self.client.post(
            self.chat_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['query'], data['query'])
        self.assertIn('AI功能正在开发中', response_data['response'])
    
    def test_search_endpoint_chinese_query(self):
        """Test search endpoint with Chinese query"""
        data = {
            'query': '家庭食谱'
        }
        
        response = self.client.post(
            self.search_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['query'], data['query'])
    
    def test_endpoints_response_format(self):
        """Test that endpoints return proper response format"""
        # Test chat endpoint response format
        chat_data = {'query': 'test query'}
        chat_response = self.client.post(
            self.chat_url,
            data=json.dumps(chat_data),
            content_type='application/json'
        )
        
        chat_json = chat_response.json()
        required_chat_fields = ['query', 'response', 'sources', 'metadata']
        for field in required_chat_fields:
            self.assertIn(field, chat_json)
        
        # Test metadata structure
        metadata = chat_json['metadata']
        required_metadata_fields = ['query_type', 'confidence', 'language']
        for field in required_metadata_fields:
            self.assertIn(field, metadata)
        
        # Test search endpoint response format
        search_data = {'query': 'test search'}
        search_response = self.client.post(
            self.search_url,
            data=json.dumps(search_data),
            content_type='application/json'
        )
        
        search_json = search_response.json()
        required_search_fields = ['query', 'results', 'count']
        for field in required_search_fields:
            self.assertIn(field, search_json)
    
    def test_content_type_headers(self):
        """Test that endpoints return proper content type"""
        data = {'query': 'test'}
        
        # Test chat endpoint
        chat_response = self.client.post(
            self.chat_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(chat_response['Content-Type'], 'application/json')
        
        # Test search endpoint
        search_response = self.client.post(
            self.search_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(search_response['Content-Type'], 'application/json')
    
    def test_large_query_handling(self):
        """Test endpoints with very large queries"""
        large_query = "A" * 10000  # 10KB query
        data = {'query': large_query}
        
        # Test chat endpoint
        chat_response = self.client.post(
            self.chat_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(chat_response.status_code, 200)
        
        # Test search endpoint
        search_response = self.client.post(
            self.search_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(search_response.status_code, 200)
    
    def test_special_characters_in_query(self):
        """Test endpoints with special characters and emojis"""
        special_query = "家庭👨‍👩‍👧‍👦 recipes & traditions! @#$%^&*()_+{}|:<>?[];',./~`"
        data = {'query': special_query}
        
        # Test chat endpoint
        chat_response = self.client.post(
            self.chat_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(chat_response.status_code, 200)
        chat_json = chat_response.json()
        self.assertEqual(chat_json['query'], special_query)
        
        # Test search endpoint
        search_response = self.client.post(
            self.search_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(search_response.status_code, 200)
        search_json = search_response.json()
        self.assertEqual(search_json['query'], special_query)