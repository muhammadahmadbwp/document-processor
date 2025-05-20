# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import FormParser, MultiPartParser
from django.http import Http404
from .serializers import DocumentSerializer, DocumentUploadSerializer, ProcessedDocumentSerializer
from .models import Document, ProcessedDocument
from celery.result import AsyncResult
from .cache_utils import get_document_cache
from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'index.html'


class DocumentList(APIView):

    def get_queryset(self, request):
        queryset = Document.objects.all()
        order_by = request.query_params.get('order_by')
        if order_by == 'created_at':
            queryset = queryset.order_by('created_at')[:3]
        return queryset

    def get(self, request, format=None):
        queryset = self.get_queryset(request)
        serializer = DocumentSerializer(queryset, many=True)
        return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = DocumentUploadSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response({
                'status': 'success',
                'data': {
                    'document_hash': result['hash'],
                    'task_id': result['task_id']
                }
            }, status=status.HTTP_201_CREATED)
        return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)    


class DocumentDetail(APIView):

    def get_object(self, pk):
        try:
            return Document.objects.get(pk=pk)
        except Document.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        queryset = self.get_object(pk)
        serializer = DocumentSerializer(queryset)
        return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        queryset = self.get_object(pk)
        serializer = DocumentSerializer(queryset, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        queryset = self.get_object(pk)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProcessedDocumentList(APIView):
        
    def get_queryset(self, request):
        queryset = ProcessedDocument.objects.all()
        return queryset

    def get(self, request, format=None):
        queryset = self.get_queryset(request)
        serializer = ProcessedDocumentSerializer(queryset, many=True)
        return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
    

class ProcessedDocumentDetail(APIView):

    def get_object(self, pk):
        try:
            return ProcessedDocument.objects.get(pk=pk)
        except ProcessedDocument.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        queryset = self.get_object(pk)
        serializer = ProcessedDocumentSerializer(queryset)
        return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)


class TaskStatus(APIView):
    def get(self, request, task_id):
        task_result = AsyncResult(task_id)
        
        # Get document status from cache if task is successful
        document_status = None
        cache_data = None
        
        if task_result.successful():
            file_hash = task_result.result
            cache_data = get_document_cache(file_hash)
            
            if not cache_data:  # If not in cache, get from database
                try:
                    document = Document.objects.get(content_hash=file_hash)
                    document_status = document.status
                except Document.DoesNotExist:
                    pass
            else:
                document_status = cache_data.get('status')

        return Response({
            'status': 'success',
            'data': {
                'task_id': task_id,
                'task_status': task_result.status,
                'document_status': document_status,
                'cache_status': cache_data.get('status') if cache_data else None
            }
        }, status=status.HTTP_200_OK)