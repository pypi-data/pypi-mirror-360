import os
import json
from flask import Flask, redirect, url_for, session, request, render_template_string
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
AUTH_BASE = 'https://login.xero.com/identity/connect'
TOKEN_URL = f'{AUTH_BASE}/token'
AUTH_URL = f'{AUTH_BASE}/authorize'
API_BASE = 'https://api.xero.com/api.xro/2.0'

SCOPES = [
    'openid', 'profile', 'email',
    'accounting.transactions',
    'accounting.contacts',
    'offline_access'
]

def make_session(token=None, state=None):
    return OAuth2Session(
        CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        scope=SCOPES,
        token=token,
        state=state
    )

@app.route('/')
def index():
    if 'token' not in session:
        return '<a href="/login">Connect to Xero</a>'
    return '''
    <h2>Xero Invoice App</h2>
    <a href="/invoices">View Invoices</a><br>
    <a href="/create">Create Invoice</a><br>
    <a href="/logout">Logout</a>
    '''

@app.route('/login')
def login():
    oauth = make_session()
    auth_url, state = oauth.authorization_url(AUTH_URL)
    session['oauth_state'] = state
    return redirect(auth_url)

@app.route('/callback')
def callback():
    oauth = make_session(state=session.get('oauth_state'))
    token = oauth.fetch_token(
        TOKEN_URL,
        authorization_response=request.url,
        client_secret=CLIENT_SECRET
    )
    session['token'] = token
    return redirect(url_for('index'))

@app.route('/invoices')
def invoices():
    try:
        # Ensure token is in session
        if 'token' not in session:
            return redirect(url_for('login'))

        # Use the token to create session
        oauth = make_session(token=session['token'])

        # Get the tenant ID
        connections_response = oauth.get('https://api.xero.com/connections')
        if connections_response.status_code != 200:
            return f"<h3>Error getting connections:</h3><pre>{connections_response.text}</pre>"

        connections_data = connections_response.json()
        if not connections_data:
            return "<h3>No connections found.</h3>"

        tenant_id = connections_data[0]['tenantId']

        # Prepare headers for API call
        headers = {
            'xero-tenant-id': tenant_id,
            'Accept': 'application/json'
        }

        # Call the invoices endpoint
        invoices_response = oauth.get(f'{API_BASE}/Invoices', headers=headers)

        if invoices_response.status_code != 200:
            return f"<h3>Error fetching invoices:</h3><pre>{invoices_response.status_code} - {invoices_response.text}</pre>"

        try:
            invoice_data = invoices_response.json()
        except ValueError as e:
            return f"<h3>Invalid JSON in response:</h3><pre>{invoices_response.text}</pre>"

        invoices = invoice_data.get('Invoices', [])
        if not invoices:
            return "<h3>No invoices found.</h3>"

        # Display the invoices
        html = "<h2>Invoices</h2><ul>"
        for inv in invoices:
            contact_name = inv.get('Contact', {}).get('Name', 'Unknown')
            total = inv.get('Total', '0.00')
            html += f"<li>{contact_name}: ${total}</li>"
        html += "</ul><a href='/'>Back</a>"
        return html

    except Exception as e:
        return f"<h3>Exception occurred:</h3><pre>{str(e)}</pre>"

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        contact_name = request.form['contact']
        amount = float(request.form['amount'])

        oauth = make_session(token=session['token'])

        # Get tenant ID
        connections_response = oauth.get('https://api.xero.com/connections')
        tenant_id = connections_response.json()[0]['tenantId']

        headers = {
            'xero-tenant-id': tenant_id,
            'Content-Type': 'application/json',
            'Accept': 'application/json'  # Request JSON response
        }

        invoice_data = {
            "Type": "ACCREC",
            "Contact": {"Name": contact_name},
            "LineItems": [{
                "Description": "Sample item",
                "Quantity": 1.0,
                "UnitAmount": amount,
                "AccountCode": "200"
            }],
            "Date": "2025-05-27",
            "DueDate": "2025-06-10",
            "LineAmountTypes": "Exclusive",
            "Status": "AUTHORISED"
        }

        response = oauth.post(f'{API_BASE}/Invoices', headers=headers, json={"Invoices": [invoice_data]})

        print("Status Code:", response.status_code)
        print("Response Headers:", response.headers)
        print("Response Text:", response.text)

        try:
            data = response.json()
            return f"Invoice created successfully: {data}"
        except requests.exceptions.JSONDecodeError:
            return f"Failed to decode JSON. Raw response:\n{response.text}"

    return '''
    <h2>Create Invoice</h2>
    <form method="post">
        Contact Name: <input name="contact"><br>
        Amount: <input name="amount" type="number" step="0.01"><br>
        <button type="submit">Create</button>
    </form>
    <a href="/">Back</a>
    '''

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(debug=True,port=8000)
