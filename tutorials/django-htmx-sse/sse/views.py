from django.template.response import TemplateResponse
from .models import Task


# Create your views here.
def index(request, *args, **kwargs):
    return TemplateResponse(
        request, "sse/index.html", {"tasks": Task.objects.all()}
    )
