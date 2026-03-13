from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.NewsList.as_view(), name='home'),
    path('<int:pk>/', views.NewsDetail.as_view(), name='detail'),
    path('comment/<int:pk>/edit/',
         views.CommentEdit.as_view(),
         name='edit'),
    path('comment/<int:pk>/delete/',
         views.CommentDelete.as_view(),
         name='delete'),
]
