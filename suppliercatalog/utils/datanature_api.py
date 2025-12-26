import frappe
import requests
import json

def fetch_and_store_security_token():
    settings = frappe.get_single("Supplier Catalog API Datanature")

    username = settings.username.strip()
    password = settings.get_password("password").strip()
    api_url = settings.api_url.rstrip("/")

    token_url = f"{api_url}/resources/security/accesstoken/"

    payload = {
        "userid": username,
        "password": password
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    response = requests.post(token_url, data=json.dumps(payload), headers=headers)
    data = response.json()

    if data.get("status") == "SUCCESS" and data.get("token"):
        settings.security_token = data["token"]
        settings.save()
        frappe.db.commit()
    else:
        frappe.throw(
            "<b>Login fehlgeschlagen</b><br>❌ Benutzername oder Passwort ist falsch.<br>"
            "Bitte überprüfe deine Zugangsdaten in den Supplier Catalog API Datanature."
        )

def fetch_security_token():
    settings = frappe.get_single("Supplier Catalog API Datanature")

    username = settings.username.strip()
    password = settings.get_password("password").strip()
    api_url = settings.api_url.rstrip("/")

    token_url = f"{api_url}/resources/security/accesstoken/"

    payload = {
        "userid": username,
        "password": password
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    response = requests.post(token_url, data=json.dumps(payload), headers=headers)
    data = response.json()

    if data.get("status") == "SUCCESS" and data.get("token"):
        return data["token"]
    else:
        frappe.throw(
            "<b>Login fehlgeschlagen</b><br>❌ Benutzername oder Passwort ist falsch.<br>"
            "Bitte überprüfe deine Zugangsdaten in den Supplier Catalog API Datanature."
        )
