from web3 import Web3
from firebase_functions import https_fn
from firebase_admin import initialize_app
import requests
import json
import base64
import os

initialize_app()

@https_fn.on_request()
def get_info(req: https_fn.Request) -> https_fn.Response:
    # Check if it's an OPTIONS request (preflight)
    if req.method == 'OPTIONS':
        # Create a response with appropriate CORS headers
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return https_fn.Response("", headers=headers, status=204)
    
    params = req.get_json()

    collection_slug = params.get('collection_slug')
    contract_address = params.get('contract_address')
    print(f"{collection_slug=}")

    if not contract_address:
        contract_address = get_contract_address(collection_slug)
        print(f"{contract_address=}")

    contract_abi = get_contract_abi(contract_address)

    type = 0 # UnKnown
    short_uri = ""
    if contract_abi != None: # None => Contract source code not verified or etc..
        
        print(f"{contract_abi=}")

        tokenURI = get_tokenURI(contract_address, contract_abi)
        short_uri = tokenURI[:64]
        print(f"{short_uri=}")
        
        
        if is_full_onchain(tokenURI):
            type = 1 # UnKnown
        else:
            print(f"{short_uri}")
            type = 2 # OffChain

    res = {
        "short_uri": short_uri,
        "type": type
    }

    headers = {
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json"
    }
    return https_fn.Response(json.dumps(res), headers=headers)

def get_contract_address(collection_slug):
    open_sea_api_key = os.environ.get('OPEN_SEA_API_KEY')

    url = f"https://api.opensea.io/v2/collection/{collection_slug}/nfts?limit=1"
    headers = {
        'X-API-KEY': open_sea_api_key,
        'accept': 'application/json',
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = json.loads(response.text)
        return data['nfts'][0]['contract']
    else:
        print("Request failed. Please check your collection slug and API key.")

def get_contract_abi(contract_address):
    eth_scan_api_key = os.environ.get('ETH_SCAN_API_KEY')

    base_url = "https://api.etherscan.io/api"
    params = {
        "module": "contract",
        "action": "getabi",
        "address": contract_address,
        "apikey": eth_scan_api_key
    }
    response = requests.get(base_url, params=params)
    data = response.json()

    if data['status'] != '1':
        print(f'Error: {data["message"]}')
        return None

    return data['result']

def get_tokenURI(contract_address, contract_abi):
    
    infra_API_Key = os.environ.get('INFRA_API_KEY')
    infura_url = f"https://mainnet.infura.io/v3/{infra_API_Key}"

    web3 = Web3(Web3.HTTPProvider(infura_url))

    contract_address_checksum = Web3.to_checksum_address(contract_address)
    contract = web3.eth.contract(address=contract_address_checksum, abi=contract_abi)

    return contract.functions.tokenURI(1).call()

def is_svg_image(data: str) -> bool:
    """
    Determines if the given data represents an SVG image.

    Args:
    - data (str): The potentially base64 encoded data to check.

    Returns:
    - bool: True if the data appears to be an SVG image, False otherwise.
    """
    try:
        decoded_str = base64.b64decode(data.split('base64,', 1)[1]).decode('utf-8')
        if '<svg' in decoded_str and '</svg>' in decoded_str:
            return True
    except Exception:
        pass
    return False


def is_full_onchain(file_content: str) -> bool:
    """
    Determines if the given file content indicates the NFT is fully on-chain.

    Args:
    - file_content (str): The content of the file which may contain base64 encoded NFT metadata.

    Returns:
    - bool: True if the NFT appears to be fully on-chain, False otherwise.
    """
    prefix = "data:application/json;base64,"
    if prefix not in file_content:
        return False

    encoded_data = file_content.split(prefix, 1)[1]

    try:
        decoded_data_str = base64.b64decode(encoded_data).decode('utf-8')
        nft_data = json.loads(decoded_data_str)
    except Exception:
        return False

    image_data = nft_data.get('image', '')
    if not image_data.startswith('http') and 'base64,' in image_data and is_svg_image(image_data):
        return True
    return False

