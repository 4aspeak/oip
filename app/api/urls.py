from django.urls import include, path
from rest_framework.routers import DefaultRouter
from app.api.views import BrowseDocumentsViewSet

api_router = DefaultRouter()
api_router.register(
    "",
    BrowseDocumentsViewSet,
    basename="browse-documents",
)

urlpatterns = [
    path("", include(api_router.urls)),
]
