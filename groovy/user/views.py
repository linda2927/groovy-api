from rest_framework import mixins, generics
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response
from user.models import User, University, UserSuggestion
from user.serializers import UserSerializer, UniversitySerializer

# Create your views here.
"""
Two ways to wrap API views
1) @api_view decorator
2) APIView class
"""


class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UniversityList(generics.ListAPIView):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer


class UniversityDetail(generics.RetrieveAPIView):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
      'users': reverse('user-list', request=request, format=format),
      'university': reverse('university-list', request=request, format=format)
    })
