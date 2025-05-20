from rest_framework import serializers
from .models import Document, ProcessedDocument
from document_processor_app.utils import enqueue_document

class DocumentSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Document
        fields = '__all__'


class DocumentUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def create(self, validated_data):
        uploaded_file = validated_data['file']
        result = enqueue_document(uploaded_file)
        return result  # Returns dict with hash and task_id
    

class ProcessedDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessedDocument
        fields = '__all__'