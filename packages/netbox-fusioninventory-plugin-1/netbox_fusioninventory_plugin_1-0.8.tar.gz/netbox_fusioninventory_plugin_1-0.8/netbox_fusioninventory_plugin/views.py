from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from . import utils

import zlib
import bs4


class PostXMLView(View):

    def post(self, request):
        User = get_user_model()
        request.user = User.objects.get_or_create(username="FusionInventory")[0]
        decompressed = zlib.decompress(request.body)
        if len(decompressed) > 200:
            xml_soup = bs4.BeautifulSoup(decompressed,features = "lxml")
            parsed_device,items = utils.soup_to_dict(xml_soup)
            utils.created_or_update_device(parsed_device,items)
            return HttpResponse()
        else:
            return HttpResponse('<?xml version="1.0" encoding="UTF-8"?>\n<REPLY>\n  <OPTION>\n <NAME>DOWNLOAD</NAME>\n<PARAM FORCE="1" UPDATE="1" />\n </OPTION>\n<RESPONSE>SEND</RESPONSE>\n <PROLOG_FREQ>1</PROLOG_FREQ>\n</REPLY>\n')

