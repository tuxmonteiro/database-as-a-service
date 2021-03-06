import logging

from django.contrib import messages
from django.template import RequestContext
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.datastructures import SortedDict

from physical.service.databaseinfra import DatabaseInfraService

LOG = logging.getLogger(__name__)

@login_required
def dashboard(request, *args, **kwargs):
    databaseinfra_service = DatabaseInfraService(request)
    databaseinfras = []
    
    for databaseinfra in databaseinfra_service.list():
        try:
            databaseinfra_status = databaseinfra_service.get_databaseinfra_status(databaseinfra)
        except AttributeError, e:
            response = HttpResponse(content='The follow driver error was find: ' + e.message, content_type='text/plain', status=500)
            return response
        data = SortedDict()
        data["name"] = databaseinfra.name
        data["engine"] = databaseinfra.engine.engine_type
        data["version"] = databaseinfra_status.version
        data["size"] = databaseinfra_status.used_size_in_bytes / 1024.0 / 1024
        data["databases"] = []
    
        for database_status in databaseinfra_status.databases_status.values():
            data["databases"].append({
                "name" : database_status.name,
                "size" : database_status.used_size_in_bytes / 1024.0 / 1024,
                "usage": round(100 * database_status.used_size_in_bytes / databaseinfra_status.used_size_in_bytes)
            })
        
        databaseinfras.append(data)
    return render_to_response("dashboard/dashboard.html", locals(), context_instance=RequestContext(request))
