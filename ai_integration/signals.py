"""
Django signals for automatic embedding updates
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from family.models import Story, Event, Heritage, Health
from .services.embedding_service import embedding_service

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Story)
def update_story_embedding(sender, instance, created, **kwargs):
    """Update embedding when Story is saved"""
    try:
        embedding_service.update_model_embedding(instance, force_update=created)
        logger.info(f"Updated embedding for Story:{instance.id}")
    except Exception as e:
        logger.error(f"Failed to update Story embedding: {e}")


@receiver(post_save, sender=Event)
def update_event_embedding(sender, instance, created, **kwargs):
    """Update embedding when Event is saved"""
    try:
        embedding_service.update_model_embedding(instance, force_update=created)
        logger.info(f"Updated embedding for Event:{instance.id}")
    except Exception as e:
        logger.error(f"Failed to update Event embedding: {e}")


@receiver(post_save, sender=Heritage)
def update_heritage_embedding(sender, instance, created, **kwargs):
    """Update embedding when Heritage is saved"""
    try:
        embedding_service.update_model_embedding(instance, force_update=created)
        logger.info(f"Updated embedding for Heritage:{instance.id}")
    except Exception as e:
        logger.error(f"Failed to update Heritage embedding: {e}")


@receiver(post_save, sender=Health)
def update_health_embedding(sender, instance, created, **kwargs):
    """Update embedding when Health record is saved"""
    try:
        embedding_service.update_model_embedding(instance, force_update=created)
        logger.info(f"Updated embedding for Health:{instance.id}")
    except Exception as e:
        logger.error(f"Failed to update Health embedding: {e}")