import requests
from datetime import datetime, timedelta

class PaymentChecker:
    def __init__(self, config):
        if not config.get('merchantId'):
            raise ValueError('merchantId harus diisi')
        self.config = {
            'merchantId': config.get('merchantId')
        }

    def check_payment_status(self, reference, amount):
        try:
            if not reference or not amount or amount <= 0:
                raise ValueError('Reference dan amount harus diisi dengan benar')

            url = 'https://api.wahdx.co/api/mutasi-orkut'
            headers = {
                'accept': 'application/json',
                'tokenKey': '8bdba486f2087137c22abd5f3988140d54da9e08db2b6812d6b5677a025c30c1',
                'Content-Type': 'application/json'
            }
            payload = {
                'merchantId': self.config['merchantId']
            }
            response = requests.post(url, json=payload, headers=headers)

            if not response.ok:
                raise Exception(f"HTTP error: {response.status_code}")
            data = response.json()
            if not data.get('status') or not data.get('data'):
                raise Exception('Response tidak valid dari server')

            transactions = data['data']
            matching_transactions = []
            now = datetime.now()
            for tx in transactions:
                try:
                    tx_amount = int(tx['amount'])
                    tx_date = datetime.strptime(tx['date'], '%Y-%m-%d %H:%M:%S')
                    time_diff = (now - tx_date).total_seconds()
                    if (
                        tx_amount == amount and
                        tx.get('qris') == 'static' and
                        tx.get('type') == 'CR' and
                        time_diff <= 600
                    ):
                        matching_transactions.append(tx)
                except Exception:
                    continue

            if matching_transactions:
                latest_transaction = max(
                    matching_transactions,
                    key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d %H:%M:%S')
                )
                return {
                    'success': True,
                    'data': {
                        'status': 'PAID',
                        'amount': int(latest_transaction['amount']),
                        'reference': latest_transaction['issuer_reff'],
                        'date': latest_transaction['date'],
                        'brand_name': latest_transaction.get('brand_name'),
                        'buyer_reff': latest_transaction.get('buyer_reff')
                    }
                }

            return {
                'success': True,
                'data': {
                    'status': 'UNPAID',
                    'amount': amount,
                    'reference': reference
                }
            }
        except Exception as error:
            return {
                'success': False,
                'error': f'Gagal cek status pembayaran: {str(error)}'
            } 