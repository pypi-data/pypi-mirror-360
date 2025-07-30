import logging
import traceback

from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound, ErrorDetail


def custom_exception_handler(e, context):
    if isinstance(e, NotFound):
        return Response({'message': e.__str__()}, status=status.HTTP_404_NOT_FOUND)

    if isinstance(e, ValidationError):
        errors = [str(error) for error in e.detail]
        return Response({'message': 'Validation Failed', 'errors': errors, 'code': 0},
                        status=status.HTTP_412_PRECONDITION_FAILED)

    response = exception_handler(e, context)

    if response is not None:
        return response

    logging.getLogger('api').error(e)
    logging.getLogger('api').error(traceback.format_exc())
    return Response({'message': 'server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class S3Exception(Exception):
    def __init__(self, message):
        super().__init__(message)

