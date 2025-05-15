from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrProfessional(BasePermission):
    """
    Permite que usuários acessem seus próprios agendamentos.
    Profissionais podem ver todos.
    """

    def has_object_permission(self, request, view, obj):
        return (
            obj.user == request.user or
            (hasattr(request.user, 'role') and request.user.role == 'professional')
        )
