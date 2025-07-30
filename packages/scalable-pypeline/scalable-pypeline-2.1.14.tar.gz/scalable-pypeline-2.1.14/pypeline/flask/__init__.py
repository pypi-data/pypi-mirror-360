""" Sermos' Flask Implementation and Tooling. Convenience imports here.
"""
import logging

logger = logging.getLogger(__name__)

try:
    from flask_smorest import Blueprint, Api
    from flask import abort
except Exception as e:
    logger.error("Unable to import Web services (Blueprint, API, abort)" f" ... {e}")

try:
    from pypeline.flask.flask_pypeline import FlaskPypeline
except Exception as e:
    logger.exception("Unable to import Sermos services (FlaskPypeline)" f" ... {e}")
