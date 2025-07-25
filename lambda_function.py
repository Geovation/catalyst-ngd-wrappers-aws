# Test for deployment 2
import json

from catalyst_ngd_wrappers.ngd_api_wrappers import items, items_limit, items_geom, \
    items_col, items_limit_geom, items_limit_col, items_geom_col, items_limit_geom_col

from utils import BaseSerialisedRequest, handle_error, construct_features_response, \
    construct_collections_response

from schemas import FeaturesBaseSchema, LimitSchema, GeomSchema, ColSchema, \
    LimitGeomSchema, LimitColSchema, GeomColSchema, LimitGeomColSchema

AWS_HEADERS = [
    'Accept',
    'Accept-Encoding',
    'Host',
    'User-Agent',
    'X-Amzn-Trace-Id',
    'X-Forwarded-For',
    'X-Forwarded-Port',
    'X-Forwarded-Proto'
]

class AWSSerialisedRequest(BaseSerialisedRequest):
    '''
    A class to represent an AWS HTTP request with its parameters and headers.
    '''

    def __init__(self, event: dict) -> None:
        method = event.get('httpMethod')
        headers = event.get('headers') or {}
        for header in AWS_HEADERS:
            headers.pop(header, None)  # Remove AWS specific headers
        url = f"https://{headers.get('Host','')}{event.get('path','')}"
        params = event.get('queryStringParameters') or {}
        route_params = event.get('pathParameters') or {}
        route_params.pop('function', None)
        super().__init__(method, url, params, route_params, headers)

def aws_serialise_response(data: dict) -> dict:
    '''
    Serialises the response data into a format suitable for AWS Lambda.
    '''

    code = data.pop('code', 200)
    response = {
        "isBase64Encoded": False,
        "statusCode": code,
        "headers": data.get('headers', {"Content-Type": "application/json"}),
        "body": json.dumps(data)
    }
    return response

def aws_process_request(
        event: dict,
        construct_response_func: callable = construct_features_response,
        **kwargs
    ) -> dict:
    '''Processes AWS HTTP requests, serialising the request and constructing a response.'''
    try:
        data = AWSSerialisedRequest(event)
        response = construct_response_func(data = data, **kwargs)
        serialised_response = aws_serialise_response(response)
        return serialised_response
    except Exception as e:
        bare_error = handle_error(error = e, code = 500)
        return aws_serialise_response(bare_error)


def aws_latest_collections(event: dict) -> dict:
    '''AWS Lambda function.
    Handles the processing of API requests to retrieve OS NGD collections, either all or a specific one.
    Handles parameter validation and telemetry tracking.'''
    response = aws_process_request(
        event = event,
        construct_response_func = construct_collections_response
    )
    return response


def aws_base(event: dict) -> dict:
    '''AWS Lambda function, OS NGD API - Features, No extensions applied.'''
    response = aws_process_request(
        event=event,
        schema_class=FeaturesBaseSchema,
        ngd_api_func=items
    )
    return response


def aws_limit(event: dict) -> dict:
    '''AWS Lambda function, OS NGD API - Features, Exensions applied:
        - Limit'''
    response = aws_process_request(
        event=event,
        schema_class=LimitSchema,
        ngd_api_func=items_limit
    )
    return response

def aws_geom(event: dict) -> dict:
    '''AWS Lambda function, OS NGD API - Features, Exensions applied:
        - Geom'''
    response = aws_process_request(
        event=event,
        schema_class=GeomSchema,
        ngd_api_func=items_geom
    )
    return response

def aws_col(event: dict) -> dict:
    '''AWS Lambda function, OS NGD API - Features, Exensions applied:
        - Col'''
    response = aws_process_request(
        event=event,
        schema_class=ColSchema,
        ngd_api_func=items_col
    )
    return response


def aws_limit_geom(event: dict) -> dict:
    '''AWS Lambda function, OS NGD API - Features, Exensions applied:
        - Limit
        - Geom'''
    response = aws_process_request(
        event=event,
        schema_class=LimitGeomSchema,
        ngd_api_func=items_limit_geom
    )
    return response


def aws_limit_col(event: dict) -> dict:
    '''AWS Lambda function, OS NGD API - Features, Exensions applied:
        - Limit
        - Col'''
    response = aws_process_request(
        event=event,
        schema_class=LimitColSchema,
        ngd_api_func=items_limit_col
    )
    return response


def aws_geom_col(event: dict) -> dict:
    '''AWS Lambda function, OS NGD API - Features, Exensions applied:
        - Geom
        - Col'''
    response = aws_process_request(
        event=event,
        schema_class=GeomColSchema,
        ngd_api_func=items_geom_col
    )
    return response


def aws_limit_geom_col(event: dict) -> dict:
    '''AWS Lambda function, OS NGD API - Features, Exensions applied:
        - Limit
        - Geom
        - Col'''
    response = aws_process_request(
        event=event,
        schema_class=LimitGeomColSchema,
        ngd_api_func=items_limit_geom_col
    )
    return response


def switch_route(route: str) -> callable:
    '''Returns the appropriate function based on the route.'''
    match route:
        case '/catalyst/features/{collection}/items':
            return aws_base
        case _:
            raise ValueError


def switch_resource(resource: str) -> callable or None:
    '''Matches the resource path to the appropriate function.'''
    match resource:
        case '/catalyst/latest-collections':
            return aws_latest_collections
        case '/catalyst/latest-collections/{collection}':
            return aws_latest_collections
        case '/catalyst/features/{collection}/items':
            return aws_base
        case '/catalyst/features/{collection}/items/{function}':
            return None
        case _:
            raise ValueError(f"Unknown resource: {resource}")

def switch_function(function: str) -> callable:
    '''Returns the appropriate function based on the function name.'''
    match function:
        case 'limit':
            return aws_limit
        case 'geom':
            return aws_geom
        case 'col':
            return aws_col
        case 'limit-geom':
            return aws_limit_geom
        case 'limit-col':
            return aws_limit_col
        case 'geom-col':
            return aws_geom_col
        case 'limit-geom-col':
            return aws_limit_geom_col
        case _:
            raise ValueError(f"Unknown function: {function}")

def lambda_handler(event: dict, context) -> dict:
    '''
    AWS Lambda handler function.
    Routes the request to the appropriate function based on the event data.
    '''

    resource = event['resource']
    function = (event.get('pathParameters') or {}).get('function', '')

    try:
        func = switch_resource(resource) or switch_function(function)
        response = func(event)
        return response
    except ValueError as e:
        return {
            "isBase64Encoded": False,
            "statusCode": 404,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({'error': 'Not Found', 'message': str(e)})
        }
