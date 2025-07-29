

"""
To use this you need to instantiate a blueprint with the
path to the directory of tarballs...

    import aguirre.integrations.quart as aguirre_quart
    APP.register_blueprint(aguirre_quart.create_blueprint("packages"),
                           url_prefix="/vendor")

Repeat if necessary for multiple directories.
"""


import quart
from quart.typing import ResponseReturnValue as Rsp

from aguirre.util import load_from_package, guess_mime_type


async def view(basedir: str, package: str, version: str, resourcepath: str) -> Rsp:
    content = load_from_package(basedir, package, version, resourcepath)
    if content is None:
        return quart.abort(404)
    response = await quart.make_response(content)
    response.mimetype = guess_mime_type(resourcepath)
    return response


def create_blueprint(basedir: str) -> quart.Blueprint:
    blueprint = quart.Blueprint("aguirre", "aguirre")
    blueprint.add_url_rule(
        "/<package>@<version>/<path:resourcepath>",
        view_func=view,
        defaults={"basedir": basedir},
    )
    return blueprint
