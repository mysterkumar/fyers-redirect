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
        # Allow '123456' as a test auth_code to always show the success tick and print a test token to the log for testing purposes.
        if auth_code == "123456":
            print(f"\n✅ Test Token data: {{'access_token': 'test_token', 'auth_code': '{auth_code}'}}\n")
            return """
                <html>
                    <body style="text-align: center; font-family: Arial, sans-serif; margin-top: 50px;">
                        <h1>✅ Auth Successful!</h1>
                        <p>You may close this tab.</p>
                    </body>
                </html>
            """
        
        response = requests.post(token_url, json=payload)
        
        # Check if the response contains valid JSON
        if response.status_code == 200:
            try:
                token_data = response.json()
                print(f"\n✅ Token data: {token_data}\n")  # Print token data to log
                return """
                    <html>
                        <body style="text-align: center; font-family: Arial, sans-serif; margin-top: 50px;">
                            <h1>✅ Auth Successful!</h1>
                            <p>You may close this tab.</p>
                        </body>
                    </html>
                """
            except json.JSONDecodeError:
                print("\n❌ Error: Invalid JSON response from Fyers API\n")
                print(f"Response content: {response.text}")
                return """
                    <html>
                        <body style="text-align: center; font-family: Arial, sans-serif; margin-top: 50px;">
                            <h1>❌ Authentication Error</h1>
                            <p>Invalid response received from Fyers API.</p>
                        </body>
                    </html>
                """
        else:
            print(f"\n❌ Error: Received status code {response.status_code} from Fyers API\n")
            # Try to extract error message from response
            error_message = "Failed to fetch token. Please try again later."
            try:
                error_data = response.json()
                if 'message' in error_data:
                    error_message = error_data['message']
                elif 'error' in error_data:
                    error_message = error_data['error']
            except Exception:
                error_message = response.text.strip() or error_message
            # Check for common credential errors
            if response.status_code == 401 or 'invalid' in error_message.lower() or 'credentials' in error_message.lower():
                error_message = "Invalid credentials or configuration. Please check your Fyers API keys and settings."
            return f"""
                <html>
                    <body style=\"text-align: center; font-family: Arial, sans-serif; margin-top: 50px;\">
                        <h1>❌ Authentication Error</h1>
                        <p>{error_message}</p>
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
