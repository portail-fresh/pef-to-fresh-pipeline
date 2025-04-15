import pandas as pd
import json
import requests
from urllib.parse import urlparse,urljoin
from os.path import exists
from pipeline.utils.load_config import load_config


config = load_config("api.yaml")

# Configuring API URL and key
api_host=config.get('nada-api-host')
api_key=config.get('nada-api-key')

http_headers={}
http_headers['X-API-KEY']=api_key

api_base_url=urljoin(api_host,'index.php/api/')

def is_url(string):
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def depth(d):
    """Returns the depth of a dictionary
    """
    if isinstance(d, dict):
        return 1 + (max(map(depth, d.values())) if d else 0)
    return 0

def make_post_request(endpoint, data, files=None):
    """Make a general POST HTTP request

    Overview
    --------
    Sends a POST request to the specified API endpoint with optional data and file uploads.
    
    Parameters
    ----------
    endpoint : str
        API endpoint
    data : dict
        POST data to be sent in the request.
    files : dict, optional
        Files to be uploaded in the request (default is None).

    Returns
    -------
    dict
        The JSON response from the API.

    Raises
    ------
    ValueError
        If the server response is not JSON-serializable.
    Exception
        For any unsuccessful response or specific API error messages.

    Usage Example
    -------------
    response = make_post_request('/api/data', {'key': 'value'})

    Implementation Details
    ----------------------
    Uses the requests library for making HTTP POST requests.
    """
    
    if len(data) == 0:
        data = ""
    elif isinstance(data, dict) and files is None:
        data = json.dumps(data)

    # Construct the request URL
    request_url = urljoin(api_base_url, endpoint)
    print('Request URL:', request_url)

    try:
        # Make the request
        response = requests.post(request_url, headers=http_headers, data=data, files=files)
        
        # Check for a non-200 status code
        if response.status_code != 200:
            try:
                response_data = response.json()
                if 'errors' in response_data:
                    for err in response_data['errors']:
                        print(err)
                raise Exception(f"POST {endpoint} failed: {response_data.get('message', 'Unknown error')}")
            except ValueError:
                raise Exception(f"POST {endpoint} failed with status {response.status_code}: {response.text}")
        
        # Attempt to parse JSON response
        try:
            json_response = response.json()
        except ValueError:
            raise ValueError(f"Failed to parse JSON response: {response.text}")

        return json_response

    except requests.RequestException as e:
        raise Exception(f"An error occurred while making the POST request: {e}")
    
    
def make_get_request(endpoint, params):
    """Make a general GET HTTP request

    Parameters
    ----------
    endpoint : str
        API endpoint
    params : dict
        GET parameters

    Returns
    -------
    response : dict
        HTTP response
    """

    response = requests.get(api_base_url + endpoint, headers=http_headers, params=params)
    
    if response.status_code != 200:
        raise Exception("GET /"+endpoint+"/ {}".format(response.status_code) + " " + f"{response.text}")

    try:
        json_response = response.json()
    except ValueError:
        raise Exception("GET /" + endpoint + "/ {}".format(response.status_code) + " " + f"{response.text}")

    return json_response

def make_delete_request(endpoint):
    """Make a general DELETE HTTP request

    Parameters
    ----------
    endpoint : str
        API endpoint

    Returns
    -------
    response : dict
        HTTP response
    """

    response = requests.delete(api_base_url + endpoint, headers=http_headers)

    if response.status_code != 200:
        raise Exception("DELETE /" + endpoint + "/ {}".format(response.status_code) + " " + f"{response.text}")

    try:
        json_response = response.json()
    except ValueError:
        raise Exception("GET /" + endpoint + "/ {}".format(response.status_code) + " " + f"{response.text}")

    return json_response


def nada_import_DDI(
        file=None,
        overwrite=None,
        repository_id=None,
        access_policy=None,
        data_remote_url=None,
        rdf=None,
        published=None
):
    """Add a new survey dataset to the catalog

    Parameters
    ----------
    file : str
        DDI XML file path or URL pointing to the XML file
    overwrite : str
        Valid values: "yes" "no"
    repository_id : str
        Collection identifier where the survey will be added to
    access_policy : str
        Valid values: "open" "direct" "public" "licensed" "enclave" "remote" "other"
    data_remote_url : str
        Link to the website for 'Data available from external repository' section
    rdf : str
        RDF file path or URL to the file
    published : int
        0=draft, 1=published
    """
    if is_url(file):
        print("You provided a URL for the DDI XML. Processing...")
    
    elif exists(file):
        print("You provided a file for the DDI XML. Processing...")
        file = {'file': open(file, 'rb')}
    else:
        raise Exception("The DDI XML file you provided doesn't seem to be a valid file path or URL." 
                        "If it is a file, please check the path."
                        "If it is a URL, make sure to add a proper prefix such as http://")

    if rdf is not None:
        if is_url(rdf):
            print("You provided a URL for the RDF. Processing...")
        elif exists(rdf):
            print("You provided a file for the RDF. Processing...")
            rdf = {'file': open(rdf, 'rb')}
        else:
            raise Exception("The RDF file you provided doesn't seem to be a valid file path or URL."
                            "If it is a file, please check the path."
                            "If it is a URL, make sure to add a proper prefix such as http://")

    data = {
        # 'file': file,
        'overwrite': overwrite,
        'repositoryid': repository_id,
        'access_policy': access_policy,
        'data_remote_url': data_remote_url,
        'rdf': rdf,
        'published': published,
    }

    data = {key: value for key, value in data.items() if value is not None}
    request_url=urljoin('datasets/','import_ddi')
    response = make_post_request(request_url, data, file)

    if response['status'] == "success":
        print("Survey dataset successfully added to the catalog.")

    return response['survey']

def list_datasets():
    """Returns a list of all datasets in the catalog

    Returns
    -------
    pd.DataFrame
        dataset information
    """

    params = {
    }
    response = make_get_request('datasets', params)
    return pd.DataFrame.from_dict(response['datasets']).set_index('id')


def delete_dataset(dataset_id):
    """Delete dataset

    Parameters
    ----------
    dataset_id : str
        Dataset IDNo
    """
    response = make_delete_request("datasets/" + dataset_id)

    if response['status'] == "success":
        print("Dataset successfully deleted from the catalog.")


def upload_ddi(filepath,overwrite='yes', published=1):
    try:
        repository_id='central'
        response = nada_import_DDI(file=filepath, overwrite=overwrite, repository_id=repository_id, published=published)
        
    except Exception as e:
        raise
    
        

