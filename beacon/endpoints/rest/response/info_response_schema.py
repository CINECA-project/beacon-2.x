import logging

from .... import conf
from ..schemas import SUPPORTED_SCHEMAS, DEFAULT_SCHEMAS

LOG = logging.getLogger(__name__)


def build_beacon_response(data, qparams_converted, func_response_type, authorized_datasets=[]):
    """"
    Transform data into the Beacon response format.
    """

    beacon_response = {
        'meta': build_meta(qparams_converted, func_response_type),
        'response': build_response(data, qparams_converted, func_response_type, authorized_datasets)
    }
    return beacon_response


def build_meta(qparams, func_response_type):
    """"Builds the `meta` part of the response

    We assume that receivedRequest is the evaluated request (qparams) sent by the user.
    """

    meta = {
        'beaconId': conf.beacon_id,
        'apiVersion': conf.api_version,
        'receivedRequest': build_received_request(qparams),
        'returnedSchemas': build_returned_schemas(qparams, func_response_type)
    }
    return meta


def build_received_request(qparams):
    """"Fills the `receivedRequest` part with the request data"""

    request = {
        'meta': {
            'requestedSchemas' : build_requested_schemas(qparams),
            'apiVersion' : qparams.apiVersion,
        },
    }

    return request


def build_requested_schemas(qparams):
    """"
    Fills the `requestedSchemas` part with the request data
    It includes valid and invalid schemas requested by the user.
    """

    requested_schemas = {}

    if qparams.requestedSchemasServiceInfo[0] or qparams.requestedSchemasServiceInfo[1]:
        requested_schemas['ServiceInfo'] = [s for s, f in qparams.requestedSchemasServiceInfo[0]] + list(
            qparams.requestedSchemasServiceInfo[1])

    if qparams.requestedSchemasDataset[0] or qparams.requestedSchemasDataset[1]:
        requested_schemas['Dataset'] = [s for s, f in qparams.requestedSchemasDataset[0]] + list(
            qparams.requestedSchemasDataset[1])

    return requested_schemas


def build_returned_schemas(qparams, func_response_type):
    """"
    Fills the `returnedSchema` part with the actual schemas returned in the response.
    This is the default schema for each type and any valid schema requested by the user.
    """

    # LOG.debug('func_response_type= %s', func_response_type.__name__)

    returned_schemas_by_response_type = {
        'build_service_info_response': {
            'ServiceInfo': [DEFAULT_SCHEMAS['ServiceInfo']] if not qparams.requestedSchemasServiceInfo[0] else []
                           + [s for s, f in qparams.requestedSchemasServiceInfo[0]],
        },
        'build_dataset_info_response': {
            'Dataset': [DEFAULT_SCHEMAS['Dataset']] if not qparams.requestedSchemasDataset[0] else []
                       + [s for s, f in qparams.requestedSchemasDataset[0]],
        },
    }

    return returned_schemas_by_response_type[func_response_type.__name__] # We let it throw a KeyError


def build_error(qparams):
    """"
    Fills the `error` part in the response.
    This error only applies to partial errors which do not prevent the Beacon from answering.
    """

    if not qparams.requestedSchemasServiceInfo[1] and not qparams.requestedSchemasDataset[1]:
         # Do nothing
         return

    message = 'Some requested schemas are not supported.'

    if len(qparams.requestedSchemasServiceInfo[1]) > 0:
        message += f' ServiceInfo: {qparams.requestedSchemasServiceInfo[1]}'

    if len(qparams.requestedSchemasDataset[1]) > 0:
        message += f' Dataset: {qparams.requestedSchemasDataset[1]}'

    return {
        'error': {
            'errorCode': 206,
            'errorMessage': message
        }
    }


def build_response(data, qparams, func, authorized_datasets=[]):
    """"Fills the `response` part with the correct format in `results`"""

    response = {
            'results': func(data, qparams, authorized_datasets),
            'info': None,
            # 'resultsHandover': None, # build_results_handover
            # 'beaconHandover': None, # build_beacon_handover
        }

    error = build_error(qparams)
    if error is not None:
        response['error'] = error

    return response


def build_service_info_response(datasets, qparams, authorized_datasets=[]):
    """"Fills the `results` part with the format for ServiceInfo"""

    schemas = qparams.requestedSchemasServiceInfo[0]

    if not (schemas or []):
        default_schema = DEFAULT_SCHEMAS['ServiceInfo'] # We let it throw a KeyError
        schemas = [(default_schema, SUPPORTED_SCHEMAS[default_schema])]

    schema, func = schemas.pop()
    return func(datasets, authorized_datasets)


def build_dataset_info_response(data, qparams, authorized_datasets=[]):
    """"Fills the `results` part with the format for ServiceInfo"""

    dataset_info_requested_schemas = qparams.requestedSchemasDataset[0]
    return get_formatted_content(data, 'Dataset', (dataset_info_requested_schemas or []), authorized_datasets)


def get_formatted_content(data, field_name, schemas, authorized_datasets=[]):
    """
    Formats the data according to the first requested schema
    It also passes the authorized datasets to the function.
    """
    # LOG.debug('schemas: %s', schemas)

    if not schemas:
        default_schema = DEFAULT_SCHEMAS[field_name] # We let it throw a KeyError
        schemas = [(default_schema, SUPPORTED_SCHEMAS[default_schema])]

    schema, func = schemas.pop()
    return [func(row, authorized_datasets) for row in data]
