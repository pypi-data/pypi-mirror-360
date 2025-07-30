import json

from django.contrib.auth.decorators import login_required
from django.apps import apps
from django.http import HttpResponse
from .filter import Filter


@login_required
def params(request, model: str):
    app_label, model_name = model.split('.')
    Model = apps.get_model(app_label, model_name)
    return HttpResponse(Filter(Model, request.GET).query_params())


@login_required
def set_filter_input(request, model: str):
    app_label, model_name = model.split('.')
    Model = apps.get_model(app_label, model_name)
    lookup = request.GET.get('lookup')
    return HttpResponse(Filter(Model, request.GET).query_input(lookup))


@login_required
def filter_add_query(request, model: str):
    app_label, model_name = model.split('.')
    Model = apps.get_model(app_label, model_name)
    query = json.loads(request.GET.get('q', '[]'))
    lookup = request.GET.get('filter_lookup')
    value = request.GET.get('filter_input')
    query.append({lookup: value})
    query = json.dumps(query)
    query_dict = request.GET.copy()
    query_dict.update(q=query)
    return HttpResponse(Filter(Model, query_dict).query_tags())
