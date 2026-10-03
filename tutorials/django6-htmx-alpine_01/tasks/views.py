from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Task


# Create your views here.
def task_list(request):
    tasks = Task.objects.all().order_by("-id")
    return render(request, "tasks/index.html", {"tasks": tasks})


def task_create(request):
    title = request.POST.get("title", "").strip()
    if title:
        task = Task.objects.create(title=title)
        return render(request, "tasks/index.html#task-item", {"task": task})
    return HttpResponse(status=400)


def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    submitted_title = request.POST.get("title", "").strip()

    if not submitted_title:
        return render(
            request,
            "tasks/index.html#task-item", {
                "task": task,
                "error": "Title cannot be empty!",
                "submitted_title": submitted_title
            }
        )

    task.title = submitted_title
    task.save()
    return render(request, "tasks/index.html#task-item", {"task": task})


def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    return HttpResponse("")
