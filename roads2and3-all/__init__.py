import logging
import json

from esridump.dumper import EsriDumper
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    dump = EsriDumper('https://geoportal.rsd.cz/arcgis/rest/services/PlanovaneUzavirkyIIaIII/MapServer/1')
    return func.HttpResponse(json.dumps(list(dump)))
