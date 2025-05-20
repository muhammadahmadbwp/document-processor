from celery import shared_task
from .models import Document, ProcessedDocument
from .document_processing import pdf_to_markdown
from io import BytesIO
from .cache_utils import set_document_cache


@shared_task(bind=True, max_retries=3)
def process_document(self, file_content, file_name, file_hash):
    try:
        # Step 1: Check if document already exists
        if Document.objects.filter(content_hash=file_hash).exists():
            set_document_cache(file_hash, "processed")
            return file_hash

        # Create document instance
        document = Document.objects.create(
            file_name=file_name,
            file_content=file_content,
            content_hash=file_hash
        )

        # Create BytesIO object for PDF processing
        file_obj = BytesIO(file_content)
        
        # Extract information and convert to markdown
        basic_info, markdown_content = pdf_to_markdown(file_obj)

        # Create embeddings
        embeddings = None  # Implement embedding creation logic here
        
        ProcessedDocument.objects.create(
            document=document,
            markdown_content=markdown_content,
            embeddings=embeddings
        )
        
        document.status = 'completed'
        document.save()
        
        # Update cache with completed status
        set_document_cache(file_hash, "processed", self.request.id)
        return file_hash
    except Exception as e:
        document = Document.objects.get(content_hash=file_hash)
        document.status = 'failed'
        document.save()
        
        # Update cache with failed status
        set_document_cache(file_hash, "failed", self.request.id)
        raise self.retry(exc=e, countdown=60)  # Retry after 60 seconds
