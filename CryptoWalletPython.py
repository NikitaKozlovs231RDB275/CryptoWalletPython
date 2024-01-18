import requests
from datetime import datetime, timedelta
from fpdf import FPDF

def get_crypto_data(asset, date):
    base_url = 'https://api.coincap.io/v2'
    symbol_id = asset['symbol'].lower()
    response = None

    if date == 'latest':
        response = requests.get(f'{base_url}/assets/{symbol_id}')
    else:
        response = requests.get(f'{base_url}/assets/{symbol_id}/history',
                                params={'interval': 'd1', 'start': int(date.timestamp()) * 1000, 'end': int((date + timedelta(days=1)).timestamp()) * 1000})

    if response.ok:
        if date == 'latest':
            data = response.json().get('data', {})
            if 'priceUsd' in data:
                return {
                    'name': asset['name'],
                    'symbol': asset['symbol'],
                    'quantity': asset['quantity'],
                    'current_price': float(data['priceUsd'])
                }
        else:
            data = response.json().get('data', [{}])
            if data and 'priceUsd' in data[0]:
                closing_price = float(data[0]['priceUsd'])
                return {
                    'name': asset['name'],
                    'symbol': asset['symbol'],
                    'quantity': asset['quantity'],
                    'price': closing_price
                }

    print(f"Invaild coin name: {asset['symbol']}")
    return None
        
def generate_report(asset, current_crypto_data, historical_crypto_data, report_filename='crypto_report.pdf'):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.set_font("Arial", 'B', size=14)
    pdf.cell(200, 10, txt=f"{asset['name']} {asset['symbol']}", ln=True, align='C')
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 7, txt=f"Quantity: {asset['quantity']:.2f}", ln=True, align='L')
    pdf.cell(200, 7, txt=f"Current Price: ${current_crypto_data['current_price']:.2f}", ln=True, align='L')
    current_net_value = current_crypto_data['current_price'] * asset['quantity']
    pdf.cell(200, 7, txt=f"Net Portfolio Value (Current): ${current_net_value:.2f}", ln=True, align='L')

    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    for period, historical_data in historical_crypto_data.items():
        gain_loss = ((current_crypto_data['current_price'] - historical_data['price']) / historical_data['price']) * 100
        historical_net_value = historical_data['price'] * asset['quantity']

        pdf.cell(200, 7, txt=f"Price {period} ago: ${historical_data['price']:.2f}", ln=True, align='L')
        pdf.cell(200, 7, txt=f"Gain/Loss for {period}: {gain_loss:.2f}%", ln=True, align='L')
        pdf.cell(200, 7, txt=f"Net Portfolio Value ({period}): ${historical_net_value:.2f}", ln=True, align='L')
        pdf.ln(5)
        
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.output(report_filename)

def main():
    crypto_symbol = input("Enter the name of the cryptocurrency: ")
    quantity = float(input("Enter the quantity of the cryptocurrency: "))

    user_asset = {'symbol': crypto_symbol.upper(), 'quantity': quantity, 'name': ''}

    current_crypto_data = get_crypto_data(user_asset, 'latest')

    if current_crypto_data:
        end_date = datetime.now()
        periods = {'1 month': end_date - timedelta(days=30),
                   '3 months': end_date - timedelta(days=90),
                   '6 months': end_date - timedelta(days=180),
                   '1 year': end_date - timedelta(days=365)}

        historical_crypto_data = {}
        for period, date in periods.items():
            historical_data = get_crypto_data(user_asset, date)
            if historical_data:
                historical_crypto_data[period] = historical_data

        generate_report(user_asset, current_crypto_data, historical_crypto_data)
    else:
        print("Error getting current crypto data.")
main()
