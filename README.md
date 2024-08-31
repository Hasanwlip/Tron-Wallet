# Tron Wallet Scanner and Mnemonic Generator

## Introduction

This project is a Tron wallet scanner and mnemonic generator. It generates random 12-word mnemonics and checks the associated Tron wallet's balance and transaction status using the TronGrid and TronScan APIs.

## Features

- **Generate 12-word Mnemonics:** Randomly generates 12-word mnemonic codes.
- **Scan Tron Wallets:** Checks the balance and transaction history of wallets associated with the mnemonic codes.
- **Save Results:** Saves results to files based on whether the wallets have balances or not.

## Requirements

- **Python 3.7+**
- Required Libraries:
  - `tronpy`
  - `bip_utils`
  - `colorama`
  - `tabulate`
  - `requests`

## Installation

### 1. Clone the Repository

First, clone the project repository:

```bash
git clone https://github.com/yourusername/tron-wallet-scanner.git
cd tron-wallet-scanner
```
### 2. Install Dependencies

Install the required dependencies using the following command:

```bash
pip install -r requirements.txt
```
## Usage
### Running the Script
To run the script and start the process:
```bash
python tron_wallet_scanner.py
```
## Viewing Results
After running the script, the results of the scans will be displayed in the console. Additionally, the results are saved to two files:
### valid_wallets_trx.txt: Contains wallets with a balance or transaction history.
### empty_wallets_trx.txt: Contains wallets that are empty and have no transaction history.
## Configuring API Keys
This script uses TronGrid API keys to interact with the Tron network. Please ensure you have valid API keys and replace the placeholders in the script with your own.

## Configuration
### Changing API Keys
To change the API keys, refer to the following section in the script:
```bash
trongrid_api_keys = [
    '2b8805fb-c870-48f9-867e-a76744616937',
    'e5ed10f0-0e66-48bd-8efc-0bba2ecd2908',
]
```
Replace these with your own API keys.
## Setting the Number of Mnemonic Words
By default, the script generates 12 words for the mnemonic. If you need to change this, modify the num_words parameter in the mnemonic_producer function:
```bash
def mnemonic_producer(num_words=12):
    while True:
        mnemonic = Bip39MnemonicGenerator().FromWordsNumber(Bip39WordsNum(num_words))
        mnemonic_queue.put(mnemonic)
        time.sleep(0.1)  # Reduce generation speed
```
## Important Notes
### API Rate Limits: Be aware that each API may have its own rate limits. If you encounter an "Exceed the user daily usage" error, you may need to add more API keys or use another account.
### Running the Script Continuously: To avoid hitting API limits, you might need to increase the time interval between requests.
## License
This project is licensed under the MIT License. For more information, see the LICENSE file.
```bash
This section completes your `README.md` file with all necessary information to guide users through the installation, configuration, and usage of the Tron Wallet Scanner and Mnemonic Generator. If you have any more sections or information you would like to add, feel free to ask!
```

```bash
Any questions @deeplogs
```
