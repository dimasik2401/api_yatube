from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.exceptions import APIException

from posts.models import Group, Post
from .serializers import CommentSerializer, GroupSerializer, PostSerializer


class CustomPermissionError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Недостаточно прав для выполнения операции.'
    default_code = 'custom_permission_error'


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для работы с объектами модели Group."""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class PostViewSet(viewsets.ModelViewSet):
    """Представление для работы с объектами модели Post."""
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise CustomPermissionError()
        instance.delete()

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise CustomPermissionError()
        serializer.save()


class CommentViewSet(viewsets.ModelViewSet):
    """Представление для работы с объектами модели Comment."""
    serializer_class = CommentSerializer

    def get_post(self):
        return get_object_or_404(Post, id=self.kwargs.get('post_id'))

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,
                        post=self.get_post())

    def get_queryset(self):
        return self.get_post().comments.all()

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise CustomPermissionError()
        instance.delete()

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise CustomPermissionError()
        serializer.save()
