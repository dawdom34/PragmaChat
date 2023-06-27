from django.shortcuts import render

from .serializers import ImagesSerializer
from.models import Images

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status


class ImageViewSet(APIView):
    #permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = {}
        serializer = ImagesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            data['image'] = serializer.data
            return Response(data=data, status=status.HTTP_201_CREATED)