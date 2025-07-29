from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views


# Define a list of URL patterns to be imported by NetBox. Each pattern maps a URL to
# a specific view so that it can be accessed by users.
urlpatterns = (
    path('', csrf_exempt(views.PostXMLView.as_view()), name='post_xml'),
    path('/', csrf_exempt(views.PostXMLView.as_view()), name='post_xml'),
)

