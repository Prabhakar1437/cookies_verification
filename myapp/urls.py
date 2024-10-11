# urls.py
from django.urls import path
from .views import UserDataView, UserDataListView, UserDataEditView

urlpatterns = [
    path('', UserDataListView.as_view(), name=''),
    path('dataform/', UserDataView.as_view(), name='dataform'),
    path('user_edit/<int:pk>/', UserDataEditView.as_view(), name='user_edit'),
]