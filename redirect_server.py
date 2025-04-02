from flask import Flask, request

app = Flask(__name__)

@app.route('/callback')
def callback():
    auth_code = request.args.get('auth_code')
    print(f"\n🔐 AUTH CODE: {auth_code}\n")
    return f"Auth code received: {auth_code}. You can close this window."
