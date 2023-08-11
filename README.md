# full-onchain-nft-checker-api | Firebase Functions

This repository contains the cloud functions for the "Full On-chain NFT Checker", a Chrome extension, which are deployed on Firebase.

## Setup

### Prerequisites

- Python installed (recommended version: 3.x)
- Firebase CLI tool (`npm install -g firebase-tools`)

### Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/yuki0627/full-onchain-nft-checker-api
    cd full-onchain-nft-checker-api
    ```

2. Install Python dependencies:

    ```sh
    pip install -r requirements.txt
    ```

3. Login to Firebase (only needed if you haven't logged in previously using Firebase CLI):

    ```.sh
    firebase login
    ```

## Deployment

Deploy the functions to Firebase:

```sh
firebase deploy --only functions
```

## Functions Overview

### get_info

This function is designed to retrieve information about an NFT, given either a `collection_slug` or a `contract_address`.

#### Parameters

- `collection_slug`: (Optional) Represents the slug of the NFT collection.
- `contract_address`: (Optional) The Ethereum contract address associated with the NFT.

Note: At least one of the parameters (either `collection_slug` or `contract_address`) must be provided for the function to execute correctly.

#### Response

- `short_uri`: The first 100 characters of the retrieved URI.
- `type`: Describes the NFT type based on its origin.
  - `0`: Unknown
  - `1`: Full On-Chain
  - `2`: Off-Chain

## Development and Testing

To test the functions locally, you can use the Firebase emulator suite.

1. Start the local API using the Firebase emulator:

   ```sh
   firebase emulators:start
   ```

2. Once the API is running, you can test the `get_info` function using the `curl` command. For example, to retrieve information about the NFT collection with the slug "nouns", use the following command:

    ```sh
    curl -X POST \
        -H "Content-Type: application/json" \
        -d '{"collection_slug": "nouns"}' \
        http://127.0.0.1:5001/full-on-chain-nft-checker/us-central1/get_info
    ```

This should return a response containing the short_uri and type information for the specified NFT collection.

Remember to replace "nouns" with the appropriate collection_slug or provide the contract_address in the payload as required.

## Environment Variables

create `functions/.env`

```.env
OPEN_SEA_API_KEY=hoge
ETH_SCAN_API_KEY=fuga
INFRA_API_KEY=piyo
```
