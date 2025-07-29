

"""
To use this you need to instantiate a blueprint with the
path to the directory of tarballs...

    import aguirre.integrations.flask as aguirre_flask
    APP.register_blueprint(aguirre_flask.create_blueprint("packages"),
                           url_prefix="/vendor")

Repeat if necessary for multiple directories.
"""


import flask
from flask.typing import ResponseReturnValue as Rsp

from aguirre.util import load_from_package, guess_mime_type


def view(basedir: str, package: str, version: str, resourcepath: str) -> Rsp:
    content = load_from_package(basedir, package, version, resourcepath)
    if content is None:
        return flask.abort(404)
    response = flask.make_response(content)
    response.mimetype = guess_mime_type(resourcepath)
    return response


def create_blueprint(basedir: str) -> flask.Blueprint:
    blueprint = flask.Blueprint("aguirre", "aguirre")
    blueprint.add_url_rule(
        "/<package>@<version>/<path:resourcepath>",
        view_func=view,
        defaults={"basedir": basedir},
    )
    return blueprint
