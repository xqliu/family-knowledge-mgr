from django.apps import AppConfig


class AiIntegrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_integration'
    verbose_name = 'AI Integration'
    
    def ready(self):
        import ai_integration.signals
