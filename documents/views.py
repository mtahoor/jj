from django.shortcuts import render, get_object_or_404
from .models import Document


def document_list(request):
    documents = Document.objects.filter(is_public=True)
    return render(request, "documents/list.html", {"documents": documents})


def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk, is_public=True)
    return render(request, "documents/detail.html", {"document": document})
