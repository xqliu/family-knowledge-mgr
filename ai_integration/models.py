from django.db import models
from django.contrib.auth.models import User
from pgvector.django import VectorField


class ChatSession(models.Model):
    """用户聊天会话记录"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    session_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = '聊天会话'
        verbose_name_plural = '聊天会话'
    
    def __str__(self):
        return f"{self.user.username} - {self.title or 'Chat Session'}"


class QueryLog(models.Model):
    """AI查询日志"""
    QUERY_TYPES = [
        ('memory_discovery', '记忆探索'),
        ('health_pattern', '健康模式'),
        ('event_planning', '事件规划'),
        ('cultural_heritage', '文化传承'),
        ('relationship_discovery', '关系发现'),
        ('general', '一般查询'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='queries')
    query_text = models.TextField()
    query_type = models.CharField(max_length=30, choices=QUERY_TYPES, default='general')
    response_text = models.TextField()
    sources_used = models.JSONField(default=list)  # 使用的数据源
    confidence_score = models.FloatField(null=True, blank=True)
    processing_time = models.FloatField(null=True, blank=True)  # 响应时间(秒)
    api_tokens_used = models.IntegerField(default=0)
    language = models.CharField(max_length=10, default='zh-CN')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '查询日志'
        verbose_name_plural = '查询日志'
    
    def __str__(self):
        return f"{self.query_text[:50]}..."


class EmbeddingCache(models.Model):
    """嵌入向量缓存"""
    content_hash = models.CharField(max_length=64, unique=True)  # 内容的SHA256哈希
    content_type = models.CharField(max_length=50)  # 'story', 'event', 'heritage' etc.
    content_id = models.PositiveIntegerField()
    embedding = VectorField(dimensions=1536)  # OpenAI text-embedding-3-small
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['content_type', 'content_id']),
            models.Index(fields=['content_hash']),
        ]
        verbose_name = '嵌入缓存'
        verbose_name_plural = '嵌入缓存'
    
    def __str__(self):
        return f"{self.content_type}:{self.content_id}"
