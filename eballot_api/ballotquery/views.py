from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import logging

from .eballot import eballot_manager

logger = logging.getLogger(__name__)

def index(request):
    return render(request, "ballotquery/index.html")

def upload_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']

        # Process CSV file using eballot_manager
        results = eballot_manager.process_csv(csv_file)

        logger.info('Response: %s', results)

        # Assuming eballot_manager returns results as a dictionary
        return JsonResponse({'results': results})

    return JsonResponse({'error': 'No file provided'}, status=400)