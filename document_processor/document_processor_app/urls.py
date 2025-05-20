# urls.py
from django.urls import path
from document_processor_app.views import (
    DocumentList, DocumentDetail,
    ProcessedDocumentList, ProcessedDocumentDetail,
    TaskStatus, IndexView
)

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('document/', DocumentList.as_view()),
    path('document/<int:id>/', DocumentDetail.as_view()),
    path('processed_documents/list/', ProcessedDocumentList.as_view()),
    path('processed_documents/<int:id>/', ProcessedDocumentDetail.as_view()),
    path('task/<str:task_id>/', TaskStatus.as_view(), name='task_status'),
]
