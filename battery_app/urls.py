from django.urls import path
from .OLA_API import ola_predict , ola_recommendations  # ✅ make sure it's importing from OLA_API
from .REVOLT_API import predict_revolt, recommend_revolt

urlpatterns = [
    path('ola/predict/', ola_predict, name='ola_predict'),
    path('ola/recommendations/', ola_recommendations, name='ola_recommendations'),


    path('revolt/predict/', predict_revolt, name='predict_revolt'),
    path('revolt/recommendations/', recommend_revolt, name='recommend_revolt'),
]


