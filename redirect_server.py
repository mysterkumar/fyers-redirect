from flask import Flask, request
import requests
import json
import os

app = Flask(__name__)

@app.route('/callback')
def callback():
    auth_code = request.args.get('auth_code')
    print(f"\n🔐 AUTH CODE: {auth_code}\n")
    
    # POST to Fyers API to get access token
    token_url = "https://api.fyers.in/api/v3/token"
    payload = {
        "grant_type": "authorization_code",
        "appIdHash": os.environ.get("FYERS_APP_ID_HASH"),
        "secret_key": os.environ.get("FYERS_SECRET_KEY"),
        "auth_code": auth_code,
        "redirect_uri": os.environ.get("FYERS_REDIRECT_URI")
    }
    
    try:
        response = requests.post(token_url, json=payload)
        token_data = response.json()
        
        # Save token to file
        with open("access_token.json", "w") as token_file:
            json.dump(token_data, token_file, indent=4)
            
        print(f"\n✅ Token saved to access_token.json\n")
        return """
            <html>
                <body style="text-align: center; font-family: Arial, sans-serif; margin-top: 50px;">
                    <h1>✅ Auth Successful!</h1>
                    <p>You may close this tab.</p>
                </body>
            </html>
        """
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        return f"""
            <html>
                <body style="text-align: center; font-family: Arial, sans-serif; margin-top: 50px;">
                    <h1>❌ Authentication Error</h1>
                    <p>Error details: {str(e)}</p>
                </body>
            </html>
        """

@app.route('/token')
def get_token():
    try:
        with open("access_token.json", "r") as token_file:
            token_data = json.load(token_file)
        return token_data, 200
    except FileNotFoundError:
        return {"error": "access_token.json not found"}, 404
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}, 500
