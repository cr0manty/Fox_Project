from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import UserSerializer

User = get_user_model()


class UserRegistration(APIView):
    def post(self, request):
        fields = [f.name for f in User._meta.fields]
        serialized = UserSerializer(data=request.data)
        if serialized.is_valid():
            user_data = {field: data for (field, data) in request.data.items() if field in fields}
            user_data.update({'dump_password': user_data.get('password')})
            user = User.objects.create_user(
                **user_data
            )
            return Response(UserSerializer(instance=user).data, status=201)
        else:
            return Response(serialized._errors, status=404)
