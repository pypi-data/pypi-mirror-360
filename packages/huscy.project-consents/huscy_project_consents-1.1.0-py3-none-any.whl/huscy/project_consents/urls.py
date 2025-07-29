from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views, viewsets
from huscy.projects.urls import project_router


router = DefaultRouter()
router.register(
    'projectconsentcategories',
    viewsets.ProjectConsentCategoryViewSet,
    basename='projectconsentcategory'
)

project_router.register(
    'consents',
    viewsets.ProjectConsentViewSet,
    basename='projectconsent'
)
project_router.register(
    'project_intermediaries',
    viewsets.ProjectIntermediaryViewSet,
    basename='projectintermediary',
)

urlpatterns = [
    path('api/', include(router.urls + project_router.urls)),

    path('project_consents/sign/<uuid:token>/', views.SignProjectConsentView.as_view(),
         name='sign-project-consent'),
]
