from ast import Pass
import datetime
import json
import random
import time
import traceback
import requests
import jwt
from django.http import HttpResponse,HttpRequest
from django.http import JsonResponse
import rest_framework.response
from rest_framework import status as response_code_status
import pytz
import redis
import os

try:
    from lb_tech_handler.db_handler import execute_query_and_return_result
except:
    from db_handler import execute_query_and_return_result


REDIS_HOST = "server.learnbasics.fun"

REDIS_PORT = 6379

REDIS_PASSWORD = 'eYVX7EwVmmxKPCDmwMtyKVge8oLd2t81'

ALLOWED_DOMAINS = ['hub.learnbasics.fun' 'myanswers.learnbasics.fun']

TESTING_HOSTS = ['localhost','127.0.0.1','127.0.0.1:8000']

AUTH_HEADER_NAME = 'LB-Auth-Token'

DEFAULT_LOG_FILE_NAME = "api_calls.log"

DEFAULT_MINIMUM_API_WAIT_TIME_IN_SECONDS = 3

DEFAULT_MAXIMUM_API_WAIT_TIME_IN_SECONDS = 5


def create_redis_client():

    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD,decode_responses=True,retry_on_timeout=True)

    return redis_client


def set_lb_auth_user_token_to_redis(admin_name:str,token:str,token_expiry_time:datetime.datetime):

    redis_client = create_redis_client()

    remaining_time = token_expiry_time

    redis_client.set(name=f"lb_auth_accesstoken-{admin_name}",value=token,ex=remaining_time)


def get_user_token_from_redis(user_name:str):

    redis_client = create_redis_client()

    return redis_client.get(name=f"lb_auth_accesstoken-{user_name}")



def debug_api_response(api_response: requests.Response,application_id:int=0,user_id:int=0):
    """
    Debug an API response by collecting useful details and returning them as a structured dictionary.

    Args:
        api_response (requests.Response): The API response object to debug.

    Returns:
        dict: A dictionary containing API debugging information.
    """
    # Safely get Content-Type
    content_type = api_response.headers.get('Content-Type', 'Unknown')

    # Decode request payload if it exists
    payload = api_response.request.body
    if payload and isinstance(payload, bytes):
        payload = payload.decode("utf-8")

    # Determine response content type and handle appropriately
    if "application/json" in content_type.lower():
        try:
            response_content = json.dumps(api_response.json(),indent=4)  # Parse JSON
        except ValueError:
            response_content = "Invalid JSON content"
    elif "text" in content_type.lower():
        response_content = api_response.text  # Plain text
    else:
        try:
            response_content = api_response.content.decode("utf-8")
        except UnicodeDecodeError:
            response_content = "Unable to decode content"

    # Construct the API log data
    api_data = {
        "log_type": "api_log",
        "data": {
            "api_end_point": api_response.url,
            "request_method": api_response.request.method,
            "response_code": api_response.status_code,
            "response_content": response_content,  # Can be JSON, text, or "Binary"
            "response_headers": dict(api_response.headers),  # Converts headers to a dictionary
            "request_headers": dict(api_response.request.headers),
            "payload": payload,
        },
        "application_id": application_id,
        "user_id": user_id,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
    }


    return api_data




def debug_drf_response(drf_response: rest_framework.response.Response,request,application_id: int = 0,user_id: int = 0) -> dict:
    # """
    # Debug a Django REST Framework Response by collecting useful details and returning them as a structured dictionary.

    # Args:
    #     drf_response (Response): The DRF Response object to debug.
    #     request (HttpRequest): The original HttpRequest object.

    # Returns:
    #     dict: A dictionary containing DRF response debugging information.
    # """
    
    # Safely get content type
    content_type = drf_response.headers.get("Content-Type", "Unknown")

    # Decode request payload (if exists)
    payload = request.body
    if payload and isinstance(payload, bytes):
        payload = payload.decode("utf-8")

    # Determine response content type and handle appropriately
    if "application/json" in content_type.lower():
        try:
            response_content = json.dumps(drf_response.data, indent=4)  # Parse JSON
        except ValueError:
            response_content = "Invalid JSON content"
    elif "text" in content_type.lower():
        response_content = drf_response.rendered_content.decode("utf-8")  # Plain text
    else:
        response_content = "Binary"  # Assume binary content for other types

    # Construct the API log data
    api_data = {
        "log_type": "api_log",
        "data": {
            "api_end_point": request.path,  # Request URL path
            "request_method": request.method,
            "response_code": drf_response.status_code,
            "response_content": response_content,  # Can be JSON, text, or "Binary"
            "response_headers": dict(drf_response.headers),
            "request_headers": dict(request.headers),
            "payload": payload,
        },
        "application_id": application_id,
        "user_id": user_id,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f"),
    }

    return api_data


def log_api_request(api_response: requests.Response,log_file_name:str=DEFAULT_LOG_FILE_NAME,log_to_database:bool=False,log_to_file:bool=True,application_id:int=0,user_id:int=0) -> int:
    # """_summary_

    # Example:
    #     api_response = requests.get("https://api.learnbasics.fun/testing?name=test")
    #     api_log_id = log_api_request(api_response=api_response,log_file_name=log_file_name,log_to_database=True,log_to_file=True)

    # Args:
    #     api_response (requests.Response): _description_
    #     log_file_name (str, optional): _description_. Defaults to DEFAULT_LOG_FILE_NAME.
    #     log_to_database (bool, optional): _description_. Defaults to False.
    #     log_to_file (bool, optional): _description_. Defaults to True.
    #     application_id (int, optional): _description_. Defaults to 0.
    #     user_id (int, optional): _description_. Defaults to 0.

    # Returns:
    #     int: Returns the api log id , returns 0 if not logged
    # """

    
    api_data = debug_api_response(api_response=api_response,application_id=application_id,user_id=user_id)

    if log_to_file and log_file_name:
        try:
            with open(log_file_name, "a") as log_file:
                # Append JSON-formatted log with a newline for each log entry
                log_file.write(json.dumps(api_data, indent=4) + "\n")
            print(f"Logged API request to file: {log_file_name}")
        except Exception as e:
            print(f"Error writing to log file: {e}")
    
    if log_to_database:

        api_log_query = """
        INSERT INTO tech.api_call_log(
         application_id, request_triggered_by_user_id,api_end_point, api_call_method, response_code, response_headers, response_content, request_headers, request_payload, created_at, created_by, updated_at, updated_by)
        VALUES (%(application_id)s, %(user_id)s,%(api_end_point)s, %(request_method)s, %(response_code)s, %(response_headers)s, %(response_content)s, %(request_headers)s, %(payload)s, %(created_at)s, %(created_by)s, %(updated_at)s, %(updated_by)s)
        RETURNING api_log_id;
        """

        args = {
            "application_id": application_id,
            "user_id": user_id,
            "request_method": api_data["data"]["request_method"],
            "response_code": api_data["data"]["response_code"],
            "response_headers": json.dumps(api_data["data"]["response_headers"]),
            "response_content": api_data["data"]["response_content"],
            "request_headers": json.dumps(api_data["data"]["request_headers"]),
            "payload": api_data["data"]["payload"],
            "created_at": "now()",
            "created_by": user_id,
            "updated_at": "now()",
            "updated_by": user_id,
            "api_end_point": api_data["data"]["api_end_point"]
        }


        try:
            api_call_id = execute_query_and_return_result(query=api_log_query, vars=args)

            return api_call_id
        
        except Exception as e:

            print(f"Error writing to database: {e}")

            print(traceback.format_exc())
    
    return 0

def log_drf_request(request,api_response: requests.Response,log_file_name:str=DEFAULT_LOG_FILE_NAME,log_to_database:bool=False,log_to_file:bool=True,application_id:int=0,user_id:int=0) -> int:
    # """_summary_

    # Example:
    #     api_response = requests.get("https://api.learnbasics.fun/testing?name=test")
    #     api_log_id = log_api_request(api_response=api_response,log_file_name=log_file_name,log_to_database=True,log_to_file=True)

    # Args:
    #     api_response (requests.Response): _description_
    #     log_file_name (str, optional): _description_. Defaults to DEFAULT_LOG_FILE_NAME.
    #     log_to_database (bool, optional): _description_. Defaults to False.
    #     log_to_file (bool, optional): _description_. Defaults to True.
    #     application_id (int, optional): _description_. Defaults to 0.
    #     user_id (int, optional): _description_. Defaults to 0.

    # Returns:
    #     int: Returns the api log id , returns 0 if not logged
    # """

    api_response.render()
    
    api_data = debug_drf_response(drf_response=api_response,request=request,application_id=application_id,user_id=user_id)

    if log_to_file and log_file_name:
        try:
            with open(log_file_name, "a") as log_file:
                # Append JSON-formatted log with a newline for each log entry
                log_file.write(json.dumps(api_data, indent=4) + "\n")
            print(f"Logged API request to file: {log_file_name}")
        except Exception as e:
            print(f"Error writing to log file: {e}")
    
    if log_to_database:

        api_log_query = """
        INSERT INTO tech.api_call_log(
         application_id, request_triggered_by_user_id,api_end_point, api_call_method, response_code, response_headers, response_content, request_headers, request_payload, created_at, created_by, updated_at, updated_by)
        VALUES (%(application_id)s, %(user_id)s,%(api_end_point)s, %(request_method)s, %(response_code)s, %(response_headers)s, %(response_content)s, %(request_headers)s, %(payload)s, %(created_at)s, %(created_by)s, %(updated_at)s, %(updated_by)s)
        RETURNING api_log_id;
        """

        args = {
            "application_id": application_id,
            "user_id": user_id,
            "request_method": api_data["data"]["request_method"],
            "response_code": api_data["data"]["response_code"],
            "response_headers": json.dumps(api_data["data"]["response_headers"]),
            "response_content": api_data["data"]["response_content"],
            "request_headers": json.dumps(api_data["data"]["request_headers"]),
            "payload": api_data["data"]["payload"],
            "created_at": "now()",
            "created_by": user_id,
            "updated_at": "now()",
            "updated_by": user_id,
            "api_end_point": api_data["data"]["api_end_point"]
        }


        try:
            api_call_id = execute_query_and_return_result(query=api_log_query, vars=args)

            return api_call_id
        
        except Exception as e:

            print(f"Error writing to database: {e}")

            print(traceback.format_exc())
    
    return 0

def throttle_api_call(minimum_api_wait_time_in_seconds=3, maximum_api_wait_time_in_seconds=5):
    """This is a decorator use to slow down API calls.
    SLowing down API calls by throttling to prevent overloading the server.

    Example:
        @throttle_api_call(minimum_api_wait_time_in_seconds=3,maximum_api_wait_time_in_seconds=5)
        def test_api():
            response = requests.get("https://api.learnbasics.fun/testing?name=test")

        @throttle_api_call
        def test_api():
            response = requests.get("https://api.learnbasics.fun/testing?name=test")

    Args:
        minimum_api_wait_time_in_seconds (int, optional): _description_. Defaults to 3.
        maximum_api_wait_time_in_seconds (int, optional): _description_. Defaults to 5.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Calculate delay time
            delay_time = random.randint(
                minimum_api_wait_time_in_seconds, maximum_api_wait_time_in_seconds
            )
            print(f"Throttling API call for {func.__name__} for {delay_time} seconds")
            
            # Delay execution
            time.sleep(delay_time)
            
            # Execute the actual function
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def unauthenticated_untracked_external_api(view_func):
    """
    Decorator for unauthenticated, untracked external APIs.
    This API does not require authentication and is not logged into the database.
    
    Args:
        view_func: The view function to be wrapped.

    Returns:
        Response from the view function.
    """
    def _wrapped_view(request, *args, **kwargs):
        return proccess_django_api(view_func,request,is_authentication_required=False, is_tracked_api=False, is_internal_api=False,under_development=False,*args, **kwargs)
    return _wrapped_view

def unauthenticated_untracked_internal_api(view_func):
    """
    Decorator for unauthenticated, untracked internal APIs.
    Validates the origin against ALLOWED_DOMAINS.

    Args:
        view_func: The view function to be wrapped.

    Returns:
        Response from the view function if origin is allowed; otherwise, a 403 error.
    """
    def _wrapped_view(request, *args, **kwargs):
        return proccess_django_api(view_func,request,is_authentication_required=False, is_tracked_api=False, is_internal_api=True,under_development=False,*args, **kwargs)
    return _wrapped_view


def unauthenticated_tracked_external_api(view_func):
    """
    Decorator for unauthenticated, tracked external APIs.
    Logs API calls into the database.

    Args:
        view_func: The view function to be wrapped.

    Returns:
        Response from the view function.
    """
    def _wrapped_view(request, *args, **kwargs):
        return proccess_django_api(view_func,request,is_authentication_required=False, is_tracked_api=True, is_internal_api=False,under_development=False,*args, **kwargs)
    return _wrapped_view


def unauthenticated_tracked_internal_api(view_func):
    """
    Decorator for unauthenticated, tracked internal APIs.
    Validates the origin against ALLOWED_DOMAINS and logs API calls into the database.

    Args:
        view_func: The view function to be wrapped.

    Returns:
        Response from the view function if origin is allowed; otherwise, a 403 error.
    """
    def _wrapped_view(request, *args, **kwargs):
       return proccess_django_api(view_func,request,is_authentication_required=False, is_tracked_api=True, is_internal_api=True,under_development=False,*args,**kwargs)
    return _wrapped_view


def authenticated_untracked_external_api(view_func):
    """
    Decorator for authenticated, untracked external APIs.
    Requires user token for access but does not log the API call into the database.

    Args:
        view_func: The view function to be wrapped.

    Returns:
        Response from the view function if token is valid; otherwise, a 401 or 403 error.
    """
    def _wrapped_view(request, *args, **kwargs):
       return proccess_django_api(view_func,request,is_authentication_required=True, is_tracked_api=False, is_internal_api=False,under_development=False,*args, **kwargs)
    return _wrapped_view

def authenticated_untracked_internal_api(view_func):
    """
    Decorator for authenticated, untracked internal APIs.
    Validates user token and origin against ALLOWED_DOMAINS.

    Args:
        view_func: The view function to be wrapped.

    Returns:
        Response from the view function if validation passes; otherwise, a 401 or 403 error.
    """
    def _wrapped_view(request, *args, **kwargs):
        return proccess_django_api(view_func,request,is_authentication_required=True, is_tracked_api=False, is_internal_api=False,under_development=False,*args, **kwargs)
    return _wrapped_view

def authenticated_tracked_external_api(view_func):
    """
    Decorator for authenticated, tracked external APIs.
    Requires user token and logs API calls into the database.

    Args:
        view_func: The view function to be wrapped.

    Returns:
        Response from the view function if token is valid; otherwise, a 401 or 403 error.
    """
    def _wrapped_view(request, *args, **kwargs):
        return proccess_django_api(view_func,request,is_authentication_required=True, is_tracked_api=True, is_internal_api=False,under_development=False,*args, **kwargs)
    return _wrapped_view


def authenticated_tracked_internal_api(view_func):
    """
    Decorator for authenticated, tracked internal APIs.
    Validates user token, origin against ALLOWED_DOMAINS, and logs API calls into the database.

    Args:
        view_func: The view function to be wrapped.

    Returns:
        Response from the view function if validation passes; otherwise, a 401 or 403 error.
    """
    def _wrapped_view(request, *args, **kwargs):
        return proccess_django_api(view_func,request,is_authentication_required=True, is_tracked_api=True,is_internal_api=True,under_development=False,*args, **kwargs)
    return _wrapped_view

def under_development_api(view_func):
    """
    Decorator for APIs under development.
    Allows access only from TESTING_HOST.

    Args:
        view_func: The view function to be wrapped.

    Returns:
        Response from the view function if host is in TESTING_HOST; otherwise, a 403 error.
    """
    def _wrapped_view(request, *args, **kwargs):
        return proccess_django_api(view_func,request,is_authentication_required=False, is_tracked_api=False, is_internal_api=False,under_development=True,*args, **kwargs)
    return _wrapped_view


def validate_token(mail,exp):
    """
    Validates the token's email and expiration timestamp.

    Args:
        mail (str): The email extracted from the token.
        exp (int): The expiration timestamp from the token.
    """

    is_valid_user = False

    status_code = response_code_status.HTTP_500_INTERNAL_SERVER_ERROR

    response_message = ""

    if mail and exp:

        query="select active_flag from organisation.employee_detail where official_mail= %(user_email)s"

        user_data = execute_query_and_return_result(query=query,vars={"user_email":mail})

        if len(user_data) == 0:
            is_valid_user = False
            status_code = response_code_status.HTTP_500_INTERNAL_SERVER_ERROR
            response_message = "User not found"

        
        if len(user_data) > 1:
            is_valid_user = False
            status_code = response_code_status.HTTP_500_INTERNAL_SERVER_ERROR
            response_message = "Multiple users found"

        active_flag = user_data[0][0]

        if active_flag:
            is_valid_user = True
            status_code = response_code_status.HTTP_200_OK
            response_message = "User is active"
        else:
            is_valid_user = False
            status_code = response_code_status.HTTP_403_FORBIDDEN
            response_message = "User is inactive"


    data_to_return = {
        "is_valid_user": is_valid_user,
        "response_status_code": status_code,
        "response_message": response_message
    }

    return data_to_return


def get_values_from_token(access_token):
    """
    Extracts email and expiration timestamp from the provided access token.
    
    Args:
        access_token (str): The access token from which details are extracted.
    """
    try:
        request_headers = {'Authorization': 'Bearer ' + access_token}

        user_detail_response = requests.get(url="https://graph.microsoft.com/v1.0/me",headers=request_headers).json()

        mail=user_detail_response['mail']

        decoded_token = jwt.decode(access_token, options={"verify_signature": False})

        exp_timestamp = decoded_token.get('exp')

        if mail and exp_timestamp:
            return mail,exp_timestamp
        else:
            return None,None

    except Exception as e:
        print("Error: ",e)
        return None,None
    
def proccess_django_api(view_func,
                        request:HttpRequest,
                        is_authentication_required:bool = True,
                        is_tracked_api:bool = True,
                        is_internal_api:bool = True,
                        under_development:bool = False,
                        *args,
                        **kwargs) -> HttpResponse:


    host_url_or_origin_url_or_ip = request.get_host()

    if is_authentication_required:
        try:
            token = request.headers.get(AUTH_HEADER_NAME)

            if not token:
                return JsonResponse({"error": "Authentication required."}, status=response_code_status.HTTP_401_UNAUTHORIZED)
            
            mail,exp=get_values_from_token(token)
            
            redis_token=get_user_token_from_redis(user_name=mail)

            if redis_token:
                print("using redis cached token")
                is_user_valid = True

                response_code = 200

                response_message ="User is authenticated"
            else:
                print("validating and saving new token")
                set_lb_auth_user_token_to_redis(
                    admin_name=mail,
                    token=token,
                    token_expiry_time=int(datetime.timedelta(minutes=30).total_seconds())
                )
                token_data = validate_token(mail,exp)

                is_user_valid = token_data["is_valid_user"]

                response_code = token_data["response_status_code"]

                response_message = token_data["response_message"]
            
                if not is_user_valid:
                    try:
                        return JsonResponse({"error": "Invalid token.","message": response_message}, status=response_code)
                    except Exception as e:
                        return JsonResponse({"error": str(e), "message": response_message}, status=response_code)

        except Exception as e:
            print("Error: ",e)
            return JsonResponse({"error": str(e), "message": "An error occured"})
    
    if is_internal_api:

        if host_url_or_origin_url_or_ip not in ALLOWED_DOMAINS:
            return JsonResponse({"error": "Domain not allowed."}, status=response_code_status.HTTP_403_FORBIDDEN)

    if under_development:

        if host_url_or_origin_url_or_ip not in TESTING_HOSTS:

            return JsonResponse({"error": "Access restricted to testing environments."}, status=response_code_status.HTTP_403_FORBIDDEN)

    response = view_func(request, *args, **kwargs)
    
    if is_tracked_api:
        log_drf_request(
            api_response=response,
            request=request,
            log_to_database=True,
            log_to_file=False
        )

    return response

@throttle_api_call
def test_api():
    api_response = requests.get("https://api.learnbasics.fun/testing?name=johnson")
    
def download_file_in_chunk_by_url(download_url,output_path,chunk_size=1024*1024,headers=None,is_download_in_chunks:bool=True,is_print_progress:bool=False):
    
    if output_path != '':
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
        except Exception as e:
            pass
            
    with requests.get(download_url, stream=True,headers=headers) as response:
        if response.status_code != 200:
            raise Exception(f"Failed to download file: {response.status_code} - {response.text}")
        
        total = int(response.headers.get('Content-Length', 0))
        downloaded = 0

        if is_download_in_chunks:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if is_print_progress:
                            print(f"Downloaded {downloaded / chunk_size:.2f} chunks ({(downloaded / (1024 * 1024)):.2f} MB) of {(total / (1024 * 1024)):.2f} MB", end="\r")


        else:
            with open(output_path, 'wb') as f:
                f.write(response.content)




if __name__ == "__main__":
    
    # log_file_name = "testing_api.log"

    # application_name = "Test Release"
    
    test_api()
    

    # api_log_id = log_api_request(api_response=api_response,log_file_name=log_file_name,log_to_database=True,log_to_file=True)
    # # print(debug_api_response(api_response=api_response))

    # api_response = requests.get("https://api.learnbasics.fun/")

    # log_api_request(api_response=api_response,log_file_name=log_file_name,log_to_database=True,log_to_file=True)

    # print(debug_api_response(api_response=api_response))

