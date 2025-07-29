from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin, ListModelMixin,
                                   UpdateModelMixin)
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from . import models, permissions, serializer, services
from .permissions import HasCreateProjectConsentTokenPermission
from huscy.projects.models import Project
from huscy.projects.permissions import IsProjectCoordinator, IsProjectMember


class ProjectConsentCategoryViewSet(CreateModelMixin, DestroyModelMixin, ListModelMixin,
                                    UpdateModelMixin, GenericViewSet):
    http_method_names = 'get', 'post', 'put', 'delete', 'head', 'options', 'trace'
    permission_classes = DjangoModelPermissions,
    queryset = models.ProjectConsentCategory.objects.all()
    serializer_class = serializer.ProjectConsentCategorySerializer


class ProjectConsentViewSet(ModelViewSet):
    permission_classes = IsAuthenticated, (DjangoModelPermissions | IsProjectCoordinator)
    serializer_class = serializer.ProjectConsentSerializer

    def initial(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        super().initial(request, *args, **kwargs)

    def get_queryset(self):
        return models.ProjectConsent.objects.filter(project=self.project)

    def perform_create(self, serializer):
        serializer.save(project=self.project)

    @action(detail=True, methods=['POST'],
            permission_classes=(IsAuthenticated,
                                HasCreateProjectConsentTokenPermission | IsProjectMember))
    def token(self, request, pk, project_pk):
        project = get_object_or_404(Project, pk=project_pk)
        context = self.get_serializer_context()
        token_serializer = serializer.ProjectConsentTokenSerializer(data=request.data,
                                                                    context=context)
        token_serializer.is_valid(raise_exception=True)
        token_serializer.save(project=project)
        return Response(token_serializer.data, status=HTTP_201_CREATED)


class ProjectIntermediaryViewSet(CreateModelMixin, DestroyModelMixin, ListModelMixin,
                                 UpdateModelMixin, GenericViewSet):
    permission_classes = IsAuthenticated, permissions.HasChangeProjectPermission
    serializer_class = serializer.ProjectIntermediarySerializer

    def initial(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        return super().initial(request, *args, **kwargs)

    def get_queryset(self):
        return models.ProjectIntermediary.objects.filter(project_membership__project=self.project)

    def perform_destroy(self, project_intermediary):
        services.delete_project_intermediary(project_intermediary)
