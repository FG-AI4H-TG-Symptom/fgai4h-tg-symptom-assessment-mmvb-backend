# This is a component of the MMVB for the "Symptom assessment" sub-group
# (of the the International Telecommunication Union focus group
# "Artificial Intelligence for Health".
# For copyright and licence, see the parent directory.

import sys

import connexion
from flask_cors import CORS

sys.path.append("../..")  # isort:skip
from config import CONFIG_DEFAULT_HOST  # isort:skip  # NOQA: E402


def create_app():
    connexion_app = connexion.App(
        __name__, specification_dir="../../swagger/", debug=True
    )
    # TODO: revisit CORS
    CORS(connexion_app.app)
    connexion_app.add_api("toy-ai.yaml", strict_validation=True)
    app = connexion_app.app

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(port=5006, host=CONFIG_DEFAULT_HOST)
