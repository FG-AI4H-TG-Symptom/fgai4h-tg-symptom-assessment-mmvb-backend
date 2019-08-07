# This is a component of the MMVB for the "Symptom assessment" sub-group
# (of the the International Telecommunication Union focus group
# "Artificial Intelligence for Health".
# For copyright and licence, see the parent directory.

import os
import sys

import connexion

sys.path.append("..")  # isort:skip
from config import CONFIG_DEFAULT_HOST  # isort:skip  # NOQA: E402

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create_app():
    connexion_app = connexion.App(
        __name__, specification_dir=os.path.join(ROOT_DIR, "swagger"), debug=True
    )
    connexion_app.add_api("case-generator.yaml", strict_validation=True)
    app = connexion_app.app

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(port=5001, host=CONFIG_DEFAULT_HOST)
