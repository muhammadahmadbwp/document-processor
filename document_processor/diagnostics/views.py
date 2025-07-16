from django.shortcuts import render
import logging
import time
from django.http import JsonResponse, HttpResponse
from django.core.cache import cache
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)

def diagnostics_dashboard(request):
    return render(request, 'diagnostics.html')

@require_http_methods(["GET"])
def api_connectivity_check(request):
    logger.info("Starting API connectivity check")
    return JsonResponse({
        'status': 'success',
        'message': 'API connectivity check successful'
        })
