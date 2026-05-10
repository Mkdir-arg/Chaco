from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.contrib.auth.models import User, Group
from ..models import Profile
from ..serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    GroupSerializer, ProfileSerializer, ChangePasswordSerializer
)


@extend_schema_view(
    list=extend_schema(description="Lista todos los usuarios"),
    create=extend_schema(description="Crea un nuevo usuario"),
    retrieve=extend_schema(description="Obtiene un usuario específico"),
    update=extend_schema(description="Actualiza un usuario"),
    partial_update=extend_schema(description="Actualiza parcialmente un usuario"),
    destroy=extend_schema(description="Elimina un usuario")
)
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar usuarios.
    
    Permite realizar operaciones CRUD sobre los usuarios del sistema.
    """
    queryset = User.objects.select_related('profile').prefetch_related('groups')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active', 'is_staff', 'groups']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['username']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    def get_permissions(self):
        """Solo administradores pueden crear, actualizar y eliminar usuarios"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @extend_schema(description="Obtiene el perfil del usuario actual")
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Obtiene el perfil del usuario actual"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        description="Cambia la contraseña del usuario actual",
        request=ChangePasswordSerializer
    )
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Cambia la contraseña del usuario actual"""
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'old_password': ['Contraseña actual incorrecta']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({'message': 'Contraseña cambiada exitosamente'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(description="Activa un usuario")
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def activate(self, request, pk=None):
        """Activa un usuario"""
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'status': 'Usuario activado'})

    @extend_schema(description="Desactiva un usuario")
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def deactivate(self, request, pk=None):
        """Desactiva un usuario"""
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'status': 'Usuario desactivado'})


@extend_schema_view(
    list=extend_schema(description="Lista todos los grupos"),
    create=extend_schema(description="Crea un nuevo grupo"),
    retrieve=extend_schema(description="Obtiene un grupo específico"),
    update=extend_schema(description="Actualiza un grupo"),
    partial_update=extend_schema(description="Actualiza parcialmente un grupo"),
    destroy=extend_schema(description="Elimina un grupo")
)
class GroupViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar grupos de usuarios.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name']
    ordering = ['name']

    def get_permissions(self):
        """Solo administradores pueden crear, actualizar y eliminar grupos"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @extend_schema(description="Obtiene los usuarios de un grupo")
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """Obtiene los usuarios de un grupo específico"""
        group = self.get_object()
        users = group.user_set.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(description="Lista todos los perfiles"),
    retrieve=extend_schema(description="Obtiene un perfil específico"),
    update=extend_schema(description="Actualiza un perfil"),
    partial_update=extend_schema(description="Actualiza parcialmente un perfil")
)
class ProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar perfiles de usuario.
    """
    queryset = Profile.objects.select_related('user')
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'put', 'patch']  # Solo lectura y actualización

    def get_queryset(self):
        """Los usuarios solo pueden ver su propio perfil, excepto administradores"""
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)
