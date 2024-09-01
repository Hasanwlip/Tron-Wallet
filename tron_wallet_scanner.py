import time
import threading
import requests
import os
import hashlib
from queue import Queue
from tronpy import Tron
from tronpy.providers import HTTPProvider
from tronpy.keys import PrivateKey
from bip_utils import Bip39MnemonicGenerator, Bip39SeedGenerator, Bip39WordsNum, Bip39MnemonicValidator
from colorama import init, Fore, Style
from tabulate import tabulate
import random

# برای اطمینان از نمایش صحیح رنگ‌ها در ویندوز
init(autoreset=True)

# لیست API Key های TronGrid
trongrid_api_keys = [
    '2b8805fb-c870-48f9-867e-a76744616937',
    'e5ed10f0-0e66-48bd-8efc-0bba2ecd2908',
]

# لیست URL های TronGrid و TronScan
urls = [
    f"https://api.trongrid.io/v1/accounts?apikey={key}" for key in trongrid_api_keys
] + [
    "https://apilist.tronscan.org/api/account"  # TronScan API (بدون نیاز به API Key)
]

# انتخاب تصادفی یک URL برای هر درخواست
def get_random_provider():
    url = random.choice(urls)
    return HTTPProvider(url)

# ایجاد client ترون با یک provider تصادفی
def get_tron_client():
    return Tron(provider=get_random_provider())

# صف برای نگهداری mnemonic هایی که تولید می‌شوند
mnemonic_queue = Queue()

# شمارنده‌ها
total_checked = 0
valid_wallets = 0
empty_wallets = 0

# دریافت نرخ تبدیل TRX به دلار از CoinGecko
def get_trx_to_usd_rate():
    try:
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=tron&vs_currencies=usd")
        if response.status_code == 200:
            return response.json()["tron"]["usd"]
        else:
            print("Error fetching TRX to USD rate")
            return None
    except Exception as e:
        print(f"Error fetching TRX to USD rate: {e}")
        return None

# تولید Mnemonic Code و اضافه کردن به صف
def mnemonic_producer(num_words=12):
    while True:
        mnemonic = Bip39MnemonicGenerator().FromWordsNumber(Bip39WordsNum(num_words))
        mnemonic_queue.put(mnemonic)
        time.sleep(0.1)  # کاهش سرعت تولید

# بررسی اعتبار Mnemonic
def is_valid_mnemonic(mnemonic):
    validator = Bip39MnemonicValidator()
    return validator.IsValid(mnemonic)

# ذخیره نتایج در فایل مناسب
def save_mnemonic_and_derivative(mnemonic, derivative, has_valid_transaction):
    global valid_wallets, empty_wallets
    if has_valid_transaction:
        valid_wallets += 1
        file_name = "valid_wallets_trx.txt"
    else:
        empty_wallets += 1
        file_name = "empty_wallets_trx.txt"
    
    with open(file_name, "a") as f:
        f.write(f"Mnemonic: {mnemonic.ToStr()}\n")
        f.write(f"  {derivative['address']} | Private Key: {derivative['private_key']} | Balance: {derivative['balance']} TRX (${derivative['balance_usd']}) | TX: {derivative['tx_status']}\n\n")

# تولید کلید خصوصی و آدرس ترون
def generate_address(mnemonic):
    seed = Bip39SeedGenerator(mnemonic).Generate()
    private_key_bytes = hashlib.sha256(seed).digest()  # ایجاد کلید خصوصی از seed با استفاده از SHA-256
    private_key = PrivateKey(private_key_bytes)
    address = private_key.public_key.to_base58check_address()
    return private_key, address

# درخواست موجودی و وضعیت تراکنش برای چند آدرس با استفاده از TronGrid و TronScan
def get_balance_and_tx_status(address, trx_to_usd_rate):
    client = get_tron_client()
    try:
        balance = client.get_account_balance(address)
        tx_count = client.get_account(address).get('total_tx', 0)
        balance_usd = round(balance * trx_to_usd_rate, 2)  # تبدیل TRX به دلار
        tx_status = "YES" if tx_count > 0 else "NO"
        return balance, balance_usd, tx_status
    except Exception as e:
        print(f"Error fetching balance and tx status for {address}: {e}")
        return None, None, "NO"

# اسکن کیف پول با استفاده از مسیر اصلی
def scan_wallet():
    global total_checked
    trx_to_usd_rate = get_trx_to_usd_rate()
    if trx_to_usd_rate is None:
        print("Could not retrieve TRX to USD rate. Exiting...")
        return

    while True:
        mnemonic = mnemonic_queue.get()  # دریافت mnemonic از صف
        total_checked += 1

        if not is_valid_mnemonic(mnemonic):
            print(f"{Fore.RED}Invalid Mnemonic:{Style.RESET_ALL} {mnemonic.ToStr()}")
            continue
        
        private_key, address = generate_address(mnemonic)
        balance, balance_usd, tx_status = get_balance_and_tx_status(address, trx_to_usd_rate)
        
        if balance is None:
            balance = 0.0
            balance_usd = 0.0
        color_balance = Fore.GREEN if balance > 0 else Fore.RED
        color_tx = Fore.GREEN if tx_status == "YES" else Fore.RED
        
        derivative = {
            "address": address,
            "balance": f"{balance}",
            "balance_usd": f"{balance_usd}",
            "tx_status": tx_status,
            "private_key": private_key.hex()
        }
        
        table = [
            ["Mnemonic", mnemonic.ToStr()],
            ["Address", address],
            ["Private Key", private_key.hex()],
            ["Balance (TRX)", f"{color_balance}{balance} TRX{Style.RESET_ALL}"],
            ["Balance (USD)", f"${balance_usd}"],
            ["TX Status", f"{color_tx}{tx_status}{Style.RESET_ALL}"],
        ]
        
        # پاک کردن خطوط قبلی و نمایش اطلاعات جدید
        os.system('cls' if os.name == 'nt' else 'clear')
        print(tabulate(table, headers=["Field", "Value"], tablefmt="grid"))
        
        save_mnemonic_and_derivative(mnemonic, derivative, balance > 0 or tx_status == "YES")
        
        # نمایش آمارها
        print(f"\nTotal Checked: {total_checked} | Empty Wallets: {empty_wallets} | Valid Wallets: {valid_wallets}\n")

    time.sleep(0.5)

# نمایش انیمیشن برای نشان دادن اجرای اسکریپت
def show_progress_animation():
    animation = "|/-\\"
    idx = 0
    while True:
        print(f"\rRunning... {animation[idx % len(animation)]}", end="")
        idx += 1
        time.sleep(0.1)

# اجرای تولید و بررسی در رشته‌های جداگانه
if __name__ == "__main__":
    producer_thread = threading.Thread(target=mnemonic_producer)
    consumer_thread = threading.Thread(target=scan_wallet)
    animation_thread = threading.Thread(target=show_progress_animation, daemon=True)

    producer_thread.start()
    consumer_thread.start()
    animation_thread.start()

    producer_thread.join()
    consumer_thread.join()
