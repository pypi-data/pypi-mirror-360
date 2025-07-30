from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import QueryDict

from src.valar.core.response import ValarResponse


def save_file(request, db, entity):
    params: QueryDict = request.POST.dict()
    _id, prop, field = (params.get(key) for key in ['id', 'prop', 'field'])
    file: InMemoryUploadedFile = request.FILES['file']

    return  ValarResponse(True)