
# This is a component of the MMVB for the "Symptom assessment" sub-group
# (of the the International Telecommunication Union focus group
# "Artificial Intelligence for Health".
# For copyright and licence, see the parent directory. 

import connexion
from flask_restful import Resource, Api
from flask_cors import CORS

import sys
sys.path.append("..")
from config import CONFIG_DEFAULT_HOST


def create_app():
    connexion_app = connexion.App(
        __name__,
        specification_dir='../swagger/',
        debug=True,
    )
    connexion_app.add_api(
        'metric-calculator.yaml',
        strict_validation=True,
    )
    app = connexion_app.app

    # for debugging only, not for production use
    CORS(app)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(port=5004, host=CONFIG_DEFAULT_HOST)
