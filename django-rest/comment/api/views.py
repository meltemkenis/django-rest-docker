from rest_framework.generics import (CreateAPIView,
                                     ListAPIView,
                                     RetrieveUpdateAPIView,
                                     UpdateAPIView,
                                     )
from rest_framework.mixins import DestroyModelMixin
from rest_framework.permissions import IsAuthenticated

from comment.api.permissions import IsOwner
from comment.api.serializers import (CommentCreateSerializer,
                                     CommentListSerializer,
                                     CommentUpdateDeleteSerializer,
                                     )
from comment.models import Comment
from comment.api.paginations import CommentPagination


class CommentCreateAPIView(CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentListAPIView(ListAPIView):
    serializer_class = CommentListSerializer
    pagination_class = CommentPagination

    def get_queryset(self):
        queryset = Comment.objects.filter(parent=None)
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(post=query)
        return queryset


class CommentUpdateAPIView(UpdateAPIView, RetrieveUpdateAPIView, DestroyModelMixin):
    queryset = Comment.objects.all()
    serializer_class = CommentUpdateDeleteSerializer
    lookup_field = 'pk'
    permission_classes = [IsOwner]

    def delete(self, request, *args, **kwargs):
        return self.destroy(self, request, *args, **kwargs)
