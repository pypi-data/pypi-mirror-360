import json
import logging

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from transcribe.models import TranscribeUser

log = logging.getLogger(__name__)


class ActiveUsersOnlyMixin:
    """
    Mixin to prevent access to class-based views by users that are not active.
    """

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_active:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)


class AdminUsersOnlyMixin(ActiveUsersOnlyMixin):
    """
    Mixin to prevent access to class-based views by users taht are not active
    and in the Admin user group.
    """

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if (
            not user.is_active
            and not user.groups.filter(name='Admin').exists()
        ):
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)


class AjaxableResponseMixin:
    """
    Mixin to add AJAX support to a form view.

    Must be used with an object based FormView (e.g. CreateView)
    """

    def render_to_json_response(self, context, **response_kwargs):
        """Returns json response."""
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def form_invalid(self, form):
        """Returns json response on ajax requests."""
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        context = form.errors
        context['status'] = 'error'
        if self.request.is_ajax():
            return self.render_to_json_response(context, status=400)
        else:
            return response

    def form_valid(self, form):
        """Returns json response on ajax requests."""
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {'status': 'success'}
            return self.render_to_json_response(data)
        else:
            return response


class TranscribeUserContextMixin:
    """
    Mixin to make sure the current transcribe user is attached to the template
    context.
    """

    def get_context_data(self, **kwargs):
        context = {}
        if hasattr(super(), 'get_context_data'):
            context = super().get_context_data(**kwargs)
        context['transcribe_user'] = TranscribeUser.objects.get(
            user=self.request.user
        )
        return context
