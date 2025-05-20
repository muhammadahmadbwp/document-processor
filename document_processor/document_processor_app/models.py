from django.db import models

class Document(models.Model):
    # Define status choices as constants
    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
    ]
    
    file_name = models.CharField(max_length=255)
    file_content = models.BinaryField()
    content_hash = models.CharField(max_length=64, unique=True)  # SHA-256 = 64 chars
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Document'
    
    def get_status_display(self):
        """Override the default get_status_display to ensure it works in all contexts"""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

class ProcessedDocument(models.Model):
    document = models.OneToOneField(Document, on_delete=models.CASCADE)
    markdown_content = models.TextField()
    embeddings = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ProcessedDocument'
