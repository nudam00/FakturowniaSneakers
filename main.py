import requests
import json
import pandas as pd


def get_settings(setting):
    # Gets settings from settings.json
    settings_file = open("settings.json")
    settings = json.load(settings_file)
    return settings[setting]


# Post url and basic headers
url = 'https://{}.fakturownia.pl/invoices.json'.format(get_settings('domena'))
headers = {'Accept': 'application/json',
           'Content-Type': 'application/json',
           }


def get_client(client):
    # Gets client from clients.json
    json_file = open("clients.json")
    clients = json.load(json_file)
    return clients[client]


def post_invoice():
    # Post invoice with data from input.xlsx

    data = pd.read_excel('input.xlsx')
    api_key = get_settings('api_key')
    stockx_number = get_settings('stockx_number')
    positions = []
    sell_date = None
    buyer_name = None

    for index, row in data.iterrows():
        if str(row['sell_date']).replace(' 00:00:00', '') == sell_date and buyer_name == row['buyer_name'] or index == 0:
            # Puts into positions if item was sold on the same date and site
            sell_date = str(row['sell_date']).replace(' 00:00:00', '')
            buyer_name = row['buyer_name']
            name = row['name']
            total_price_gross = str(row['total_price_gross']).replace(',', '.')
            size = row['size']
            order = row['order']
            try:
                inv = stockx_number+'-'+row['order'].split('-')[1]
            except:
                pass
            tracking = row['tracking']
            client = get_client(buyer_name)

            positions.append({"name": name, "tax": client['tax'],
                              "total_price_gross": total_price_gross,  "quantity": 1})

            if buyer_name == 'StockXde' or buyer_name == 'StockXnl':
                positions.append({'kind': 'text_separator', 'name': "Size: {}\nOrder: {}\nInvoice: {}\nTracking: {}".format(
                    size, order, inv, tracking)})
            else:
                positions.append({'kind': 'text_separator', 'name': "Size: {}\nOrder: {}\nTracking: {}".format(
                    size, order, tracking)})
        else:
            # If different site or date then post invoice
            invoice = {
                "api_token": api_key,
                "invoice": {
                    "kind": "vat",
                    "issue_date": sell_date,
                    'place': "Mosina",
                    "sell_date": sell_date,
                    "payment_to_kind": 14,
                    'payment_type': 'transfer',
                    "buyer_name": client['buyer_name'],
                    "buyer_post_code": client['buyer_post_code'],
                    "buyer_city": client['buyer_city'],
                    "buyer_street": client['buyer_street'],
                    "buyer_country": client['buyer_country'],
                    'lang': 'pl/en',
                    "currency": client['currency'],
                    "positions": positions
                }}

            if buyer_name == 'Alias' or buyer_name == 'StockXde' or buyer_name == 'StockXnl' or buyer_name == 'Sneakit':
                invoice['invoice']["buyer_tax_no"] = client['buyer_tax_no']

            positions = []

            requests.post(url=url, data=json.dumps(invoice), headers=headers)

            sell_date = str(row['sell_date']).replace(' 00:00:00', '')
            buyer_name = row['buyer_name']
            name = row['name']
            total_price_gross = str(row['total_price_gross']).replace(',', '.')
            size = row['size']
            order = row['order']
            try:
                inv = stockx_number+'-'+row['order'].split('-')[1]
            except:
                pass
            tracking = row['tracking']
            client = get_client(buyer_name)

            positions.append({"name": name, "tax": client['tax'],
                              "total_price_gross": total_price_gross,  "quantity": 1})

            if buyer_name == 'StockXde' or buyer_name == 'StockXnl':
                positions.append({'kind': 'text_separator', 'name': "Size: {}\nOrder: {}\nInvoice: {}\nTracking: {}".format(
                    size, order, inv, tracking)})
            else:
                positions.append({'kind': 'text_separator', 'name': "Size: {}\nOrder: {}\nTracking: {}".format(
                    size, order, tracking)})

    invoice = {
        "api_token": api_key,
        "invoice": {
            "kind": "vat",
            "issue_date": sell_date,
            'place': "Mosina",
            "sell_date": sell_date,
            "payment_to_kind": 14,
            'payment_type': 'transfer',
            "buyer_name": client['buyer_name'],
            "buyer_post_code": client['buyer_post_code'],
            "buyer_city": client['buyer_city'],
            "buyer_street": client['buyer_street'],
            "buyer_country": client['buyer_country'],
            'lang': 'pl/en',
            "currency": client['currency'],
            "positions": positions
        }}

    if buyer_name == 'Alias' or buyer_name == 'StockXde' or buyer_name == 'StockXnl' or buyer_name == 'Sneakit':
        invoice['invoice']["buyer_tax_no"] = client['buyer_tax_no']

    # Post last invoice
    requests.post(url=url, data=json.dumps(invoice), headers=headers)

    return True


post_invoice()
