from rest_framework.permissions import BasePermission

class AllowReadAndAdd(BasePermission):
	anon_safe_methods = ['GET', 'POST']

	def has_permission(self, request, view):
		if request.method in self.anon_safe_methods:
			return True
		else:
			return False

