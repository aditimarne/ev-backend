from fastapi import APIRouter, HTTPException
from battery_app import dg2

router = APIRouter()

@router.post("/predict")
def revolt_predict(data: dict):
    try:
        soh, rul = dg2.predict_soh_rul(data)
        advice = dg2.evaluate_input(data)
        return {
            "soh": round(float(soh), 2),
            "rul": round(float(rul), 2),
            "recommendations": advice
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommendations")
def revolt_recommend(data: dict):
    try:
        advice = dg2.evaluate_input(data)
        return {"suggestions": advice}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


















# REVOLT_API.py (Django RESTful API for Revolt)
# import json
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from . import dg2  # Import Revolt logic

# @csrf_exempt
# def predict_revolt(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             predicted_soh, predicted_rul = dg2.predict_soh_rul(data)
#             advice = dg2.evaluate_input(data)

#             return JsonResponse({
#                 'soh': round(float(predicted_soh), 2),
#                 'rul': round(float(predicted_rul), 2),
#                 'recommendations': advice
#             })
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
#     return JsonResponse({'error': 'Only POST method allowed'}, status=405)


# @csrf_exempt
# def recommend_revolt(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             recommendations = dg2.evaluate_input(data)
#             return JsonResponse({
#                 'title': "Revolt Battery Suggestions",
#                 'suggestions': recommendations
#             })
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
#     return JsonResponse({'error': 'Only POST method allowed'}, status=405)
