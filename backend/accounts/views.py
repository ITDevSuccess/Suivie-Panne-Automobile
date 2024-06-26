from rest_framework import status, response, decorators, permissions
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from .models import CustomUser
from .serializers import UserSerializer


@decorators.api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@decorators.api_view(['POST'])
def update_user(request):
    print(request.data)
    try:
        user = CustomUser.objects.get(id=request.data['id'])
    except CustomUser.DoesNotExist:
        return response.Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        print("Save: ", serializer.data)
        return response.Response(serializer.data, status=status.HTTP_200_OK)
    return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@decorators.api_view(['POST'])
def login_user(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        user = None
        if '@' in username:
            try:
                user = CustomUser.objects.get(email=username)
            except ObjectDoesNotExist:
                pass

        if not user:
            user = authenticate(username=username, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return response.Response({'token': token.key, 'user': username}, status=status.HTTP_200_OK)
        else:
            return response.Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@decorators.api_view(['POST'])
def token_user(request):
    if request.method == 'POST':
        user_data = request.data.get('user')
        if user_data is not None:
            try:
                user = CustomUser.objects.get(username=user_data)
                token, created = Token.objects.get_or_create(user=user)
                return response.Response({'token': token.key, 'user': user.username}, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return response.Response({'error': 'Invalid user'}, status=status.HTTP_401_UNAUTHORIZED)
        return response.Response({'error': 'User data not provided'}, status=status.HTTP_400_BAD_REQUEST)
    return response.Response({'error': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@decorators.api_view(['POST'])
@decorators.permission_classes([permissions.IsAuthenticated])
def logout_user(request):
    if request.method == 'POST':
        try:
            request.user.auth_token.delete()
            return response.Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return response.Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@decorators.api_view(['GET'])
@decorators.permission_classes([permissions.IsAuthenticated])
def get_all_user(request):
    if request.method == 'GET':
        users = CustomUser.objects.all().order_by('username')
        serializer = UserSerializer(users, many=True)
        return response.Response({'users': serializer.data})
