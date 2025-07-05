"""
Comprehensive tests for AI integration signals targeting 90%+ branch coverage
Uses unittest.TestCase to avoid database dependencies
"""
import os
import sys
import django
from django.conf import settings

# Configure Django settings if not already configured
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.admin',
            'django.contrib.staticfiles',
            'family',
            'ai_integration',
        ],
        STATIC_URL='/static/',
        SECRET_KEY='test-secret-key',
        USE_TZ=True,
    )
    django.setup()

import unittest
from unittest.mock import Mock, patch, MagicMock
import logging

from ai_integration.signals import (
    update_story_embedding, update_event_embedding,
    update_heritage_embedding, update_health_embedding
)


class TestSignals(unittest.TestCase):
    """Comprehensive tests for signal handlers"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Disable logging during tests
        logging.disable(logging.CRITICAL)
        
    def tearDown(self):
        """Clean up after tests"""
        logging.disable(logging.NOTSET)
        
    def test_update_story_embedding_created_success(self):
        """Test update_story_embedding when story is created successfully"""
        mock_instance = Mock()
        mock_instance.id = 1
        
        with patch('ai_integration.signals.embedding_service') as mock_service:
            mock_service.update_model_embedding.return_value = True
            
            # Call signal handler
            update_story_embedding(sender=Mock(), instance=mock_instance, created=True)
            
            # Verify update_model_embedding was called with force_update=True
            mock_service.update_model_embedding.assert_called_once_with(
                mock_instance, force_update=True
            )
            
    def test_update_story_embedding_updated_success(self):
        """Test update_story_embedding when story is updated successfully"""
        mock_instance = Mock()
        mock_instance.id = 2
        
        with patch('ai_integration.signals.embedding_service') as mock_service:
            mock_service.update_model_embedding.return_value = True
            
            # Call signal handler
            update_story_embedding(sender=Mock(), instance=mock_instance, created=False)
            
            # Verify update_model_embedding was called with force_update=False
            mock_service.update_model_embedding.assert_called_once_with(
                mock_instance, force_update=False
            )
            
    def test_update_story_embedding_exception(self):
        """Test update_story_embedding when exception occurs"""
        mock_instance = Mock()
        mock_instance.id = 3
        
        with patch('ai_integration.signals.embedding_service') as mock_service:
            mock_service.update_model_embedding.side_effect = Exception("Service error")
            
            with patch('ai_integration.signals.logger') as mock_logger:
                # Call signal handler - should not raise exception
                update_story_embedding(sender=Mock(), instance=mock_instance, created=True)
                
                # Verify error was logged
                mock_logger.error.assert_called_once()
                error_msg = mock_logger.error.call_args[0][0]
                self.assertIn("Failed to update Story embedding", error_msg)
                
    def test_update_event_embedding_created_success(self):
        """Test update_event_embedding when event is created successfully"""
        mock_instance = Mock()
        mock_instance.id = 10
        
        with patch('ai_integration.signals.embedding_service') as mock_service:
            mock_service.update_model_embedding.return_value = True
            
            # Call signal handler
            update_event_embedding(sender=Mock(), instance=mock_instance, created=True)
            
            # Verify update_model_embedding was called with force_update=True
            mock_service.update_model_embedding.assert_called_once_with(
                mock_instance, force_update=True
            )
            
    def test_update_event_embedding_updated_success(self):
        """Test update_event_embedding when event is updated successfully"""
        mock_instance = Mock()
        mock_instance.id = 11
        
        with patch('ai_integration.signals.embedding_service') as mock_service:
            mock_service.update_model_embedding.return_value = True
            
            # Call signal handler
            update_event_embedding(sender=Mock(), instance=mock_instance, created=False)
            
            # Verify update_model_embedding was called with force_update=False
            mock_service.update_model_embedding.assert_called_once_with(
                mock_instance, force_update=False
            )
            
    def test_update_event_embedding_exception(self):
        """Test update_event_embedding when exception occurs"""
        mock_instance = Mock()
        mock_instance.id = 12
        
        with patch('ai_integration.signals.embedding_service') as mock_service:
            mock_service.update_model_embedding.side_effect = Exception("API error")
            
            with patch('ai_integration.signals.logger') as mock_logger:
                # Call signal handler - should not raise exception
                update_event_embedding(sender=Mock(), instance=mock_instance, created=True)
                
                # Verify error was logged
                mock_logger.error.assert_called_once()
                error_msg = mock_logger.error.call_args[0][0]
                self.assertIn("Failed to update Event embedding", error_msg)
                
    def test_update_heritage_embedding_created_success(self):
        """Test update_heritage_embedding when heritage is created successfully"""
        mock_instance = Mock()
        mock_instance.id = 20
        
        with patch('ai_integration.signals.embedding_service') as mock_service:
            mock_service.update_model_embedding.return_value = True
            
            # Call signal handler
            update_heritage_embedding(sender=Mock(), instance=mock_instance, created=True)
            
            # Verify update_model_embedding was called with force_update=True
            mock_service.update_model_embedding.assert_called_once_with(
                mock_instance, force_update=True
            )
            
    def test_update_heritage_embedding_updated_success(self):
        """Test update_heritage_embedding when heritage is updated successfully"""
        mock_instance = Mock()
        mock_instance.id = 21
        
        with patch('ai_integration.signals.embedding_service') as mock_service:
            mock_service.update_model_embedding.return_value = True
            
            # Call signal handler
            update_heritage_embedding(sender=Mock(), instance=mock_instance, created=False)
            
            # Verify update_model_embedding was called with force_update=False
            mock_service.update_model_embedding.assert_called_once_with(
                mock_instance, force_update=False
            )
            
    def test_update_heritage_embedding_exception(self):
        """Test update_heritage_embedding when exception occurs"""
        mock_instance = Mock()
        mock_instance.id = 22
        
        with patch('ai_integration.signals.embedding_service') as mock_service:
            mock_service.update_model_embedding.side_effect = Exception("Network error")
            
            with patch('ai_integration.signals.logger') as mock_logger:
                # Call signal handler - should not raise exception
                update_heritage_embedding(sender=Mock(), instance=mock_instance, created=True)
                
                # Verify error was logged
                mock_logger.error.assert_called_once()
                error_msg = mock_logger.error.call_args[0][0]
                self.assertIn("Failed to update Heritage embedding", error_msg)
                
    def test_update_health_embedding_created_success(self):
        """Test update_health_embedding when health record is created successfully"""
        mock_instance = Mock()
        mock_instance.id = 30
        
        with patch('ai_integration.signals.embedding_service') as mock_service:
            mock_service.update_model_embedding.return_value = True
            
            # Call signal handler
            update_health_embedding(sender=Mock(), instance=mock_instance, created=True)
            
            # Verify update_model_embedding was called with force_update=True
            mock_service.update_model_embedding.assert_called_once_with(
                mock_instance, force_update=True
            )
            
    def test_update_health_embedding_updated_success(self):
        """Test update_health_embedding when health record is updated successfully"""
        mock_instance = Mock()
        mock_instance.id = 31
        
        with patch('ai_integration.signals.embedding_service') as mock_service:
            mock_service.update_model_embedding.return_value = True
            
            # Call signal handler
            update_health_embedding(sender=Mock(), instance=mock_instance, created=False)
            
            # Verify update_model_embedding was called with force_update=False
            mock_service.update_model_embedding.assert_called_once_with(
                mock_instance, force_update=False
            )
            
    def test_update_health_embedding_exception(self):
        """Test update_health_embedding when exception occurs"""
        mock_instance = Mock()
        mock_instance.id = 32
        
        with patch('ai_integration.signals.embedding_service') as mock_service:
            mock_service.update_model_embedding.side_effect = Exception("Database error")
            
            with patch('ai_integration.signals.logger') as mock_logger:
                # Call signal handler - should not raise exception
                update_health_embedding(sender=Mock(), instance=mock_instance, created=True)
                
                # Verify error was logged
                mock_logger.error.assert_called_once()
                error_msg = mock_logger.error.call_args[0][0]
                self.assertIn("Failed to update Health embedding", error_msg)
                
    def test_signal_kwargs_handling(self):
        """Test that signal handlers properly handle extra kwargs"""
        mock_instance = Mock()
        mock_instance.id = 40
        
        with patch('ai_integration.signals.embedding_service') as mock_service:
            mock_service.update_model_embedding.return_value = True
            
            # Call with extra kwargs that Django might pass
            update_story_embedding(
                sender=Mock(), 
                instance=mock_instance, 
                created=True,
                update_fields=['title', 'content'],
                raw=False,
                using='default'
            )
            
            # Should still work correctly
            mock_service.update_model_embedding.assert_called_once_with(
                mock_instance, force_update=True
            )
            
    def test_logging_info_messages(self):
        """Test that info messages are logged on success"""
        mock_instance = Mock()
        mock_instance.id = 50
        
        with patch('ai_integration.signals.embedding_service') as mock_service:
            mock_service.update_model_embedding.return_value = True
            
            with patch('ai_integration.signals.logger') as mock_logger:
                # Call each signal handler
                update_story_embedding(sender=Mock(), instance=mock_instance, created=True)
                mock_logger.info.assert_called_with("Updated embedding for Story:50")
                
                mock_logger.reset_mock()
                update_event_embedding(sender=Mock(), instance=mock_instance, created=True)
                mock_logger.info.assert_called_with("Updated embedding for Event:50")
                
                mock_logger.reset_mock()
                update_heritage_embedding(sender=Mock(), instance=mock_instance, created=True)
                mock_logger.info.assert_called_with("Updated embedding for Heritage:50")
                
                mock_logger.reset_mock()
                update_health_embedding(sender=Mock(), instance=mock_instance, created=True)
                mock_logger.info.assert_called_with("Updated embedding for Health:50")


if __name__ == '__main__':
    unittest.main()