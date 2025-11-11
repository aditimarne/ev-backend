# REVOLT_API.py (Django RESTful API for Revolt)
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from . import dg2  # Import Revolt logic

@csrf_exempt
def predict_revolt(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            predicted_soh, predicted_rul = dg2.predict_soh_rul(data)
            advice = dg2.evaluate_input(data)

            return JsonResponse({
                'soh': round(float(predicted_soh), 2),
                'rul': round(float(predicted_rul), 2),
                'recommendations': advice
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Only POST method allowed'}, status=405)


@csrf_exempt
def recommend_revolt(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            recommendations = dg2.evaluate_input(data)
            return JsonResponse({
                'title': "Revolt Battery Suggestions",
                'suggestions': recommendations
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Only POST method allowed'}, status=405)
