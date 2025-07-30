import json
import timeit
import os
import requests


def timed_execution(func):
    """This is a decorator to time the execution time of a function

    Example:
        @timed_execution
        def test_api():
            response = requests.get("https://api.learnbasics.fun/testing?name=test")

    Args:
        func (_type_): Function to be timed
    """

    def wrapper(*args, **kwargs):
        start_time = timeit.default_timer()
        result = func(*args, **kwargs)
        end_time = timeit.default_timer()
        execution_time = end_time - start_time
        print(f"Execution time for {func.__name__}: {execution_time} seconds")
        return result
    
    return wrapper

def display_indented_text(data:dict,indent_level:int=4):
    
    print(json.dumps(data,indent=indent_level))
    
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
