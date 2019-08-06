
# This is a component of the MMVB for the "Symptom assessment" sub-group
# (of the the International Telecommunication Union focus group
# "Artificial Intelligence for Health".
# For copyright and licence, see the parent directory. 

import connexion
from flask_restful import Resource, Api

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
        'toy-ai.yaml',
        strict_validation=True,
    )
    app = connexion_app.app

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(port=5002, host=CONFIG_DEFAULT_HOST)
