# This is a component of the MMVB for the "Symptom assessment" sub-group
# (of the the International Telecommunication Union focus group
# "Artificial Intelligence for Health".
# For copyright and licence, see the parent directory.

import sys

from flask import Flask
from flask_restful import Api

sys.path.append("..")  # isort:skip
from config import CONFIG_DEFAULT_HOST  # isort:skip  # NOQA: E402

app = Flask(__name__, static_folder="files/", static_url_path="")
api = Api(app)


def run_app(port, host):
    # https://vilimpoc.org/blog/2012/11/21/serving-static-files-from-root-and-not-static-using-flask/
    @app.route("/")
    def root():
        return app.send_static_file("index.html")

    app.run(port=port, host=host)


if __name__ == "__main__":
    run_app(port=5005, host=CONFIG_DEFAULT_HOST)
