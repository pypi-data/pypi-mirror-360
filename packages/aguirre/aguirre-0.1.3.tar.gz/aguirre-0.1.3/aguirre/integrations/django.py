

"""
To use this you need to specify where the packages are saved,
which probably wants to be in the `settings.py`:

    AGUIRRE_BASE_DIR = BASE_DIR / "packages"

Then add a pattern to your main `urls.py` file:

    from .settings import AGUIRRE_BASE_DIR
    import aguirre.integrations.django as aguirre_django
    urlpatterns = [
        ...
        path("vendor/<package>@<version>/<path:resourcepath>", aguirre_django.view,
             {"basedir": AGUIRRE_BASE_DIR}, name="aguirre"),
        ...
    ]

You can use the `url` tag in templates to reference resources:

    <link rel="stylesheet" href="{% url "aguirre" "leaflet" "1.7.1" "dist/leaflet.css" %} />

NOTE: This does not integrate with `collectstatic`!

"""


from django.http import HttpRequest as Req
from django.http import HttpResponse as Rsp
from django.http import Http404

from aguirre.util import load_from_package, guess_mime_type


def view(req: Req, package: str, version: str, resourcepath: str, basedir: str) -> Rsp:
    content = load_from_package(basedir, package, version, resourcepath)
    if content is None:
        raise Http404()
    mimetype = guess_mime_type(resourcepath)
    response = Rsp(content=content, content_type=mimetype)
    return response
