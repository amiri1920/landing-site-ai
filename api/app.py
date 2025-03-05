
from flask import Flask, request, jsonify
import requests
import re
import os
from flask_cors import CORS  # Add for cross-origin support

app = Flask(__name__)
CORS(app)  # Enable CORS if needed

@app.route('/')
def home():
    return "LandingSite AI Automation Service - POST to /generate to create websites"

@app.route('/generate', methods=['POST'])
def generate_website():
    try:
        # Verify environment variables
        if 'USER_SUB' not in os.environ or 'API_TOKEN' not in os.environ:
            missing_vars = []
            if 'USER_SUB' not in os.environ:
                missing_vars.append('USER_SUB')
            if 'API_TOKEN' not in os.environ:
                missing_vars.append('API_TOKEN')
            error_msg = f"Server missing required credentials: {', '.join(missing_vars)}"
            print(f"ERROR: {error_msg}")
            return jsonify({"error": error_msg}), 500

        # Log request data
        data = request.get_json(silent=True) or {}
        print(f"Processing request for business: {data.get('business_name', 'N/A')}")
        
        # Get parameters from request
        data = request.get_json(silent=True) or {}
        business_name = data.get('business_name', 'food truck')
        business_about = data.get('business_about', 'founded in 2024')

        # STEP 1: Build Form
        buildform_response = requests.post(
            "https://api.landingsite.ai/buildForm",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://app.landingsite.ai",
                "Referer": "https://app.landingsite.ai/",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            },
            data={
                "business-name": business_name,
                "business-about": business_about,
                "user-sub": os.environ['USER_SUB']
            },
            allow_redirects=False
        )

        if buildform_response.status_code != 303:
            return jsonify({
                "error": "Build form failed",
                "status_code": buildform_response.status_code,
                "response": buildform_response.text[:200]
            }), 500

        # Extract website ID
        redirect_url = buildform_response.headers.get("location", "")
        match = re.search(r'/website-chat/([^/]+)$', redirect_url)
        if not match:
            return jsonify({"error": "Failed to extract website ID from redirect URL"}), 500

        website_id = match.group(1)

        # STEP 2: Template Selection
        graphql_response = requests.post(
            "https://api.landingsite.ai/graphql",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {os.environ['API_TOKEN']}",
                "Origin": "https://app.landingsite.ai",
                "Referer": "https://app.landingsite.ai/"
            },
            json={
                "operationName": "StartBuildingWebsiteMutation",
                "query": """mutation StartBuildingWebsiteMutation($id: String!, $templateId: String!) {
                    startBuildingWebsite(id: $id, templateId: $templateId) {
                        __typename id startedGeneratingAt
                    }
                }""",
                "variables": {
                    "id": website_id,
                    "templateId": data.get('template_id', '6ab01f4a-e390-46a8-9518-049be2fc8656')
                }
            }
        )

        return jsonify({
            "website_id": website_id,
            "status": "success",
            "graphql_status": graphql_response.status_code,
            "response": graphql_response.json()
        })

    except requests.exceptions.RequestException as e:
        error_msg = f"API request failed: {str(e)}"
        print(f"ERROR: {error_msg}")
        return jsonify({"error": error_msg, "details": str(e)}), 500
    except Exception as e:
        import traceback
        error_msg = f"Unexpected error: {str(e)}"
        error_details = traceback.format_exc()
        print(f"ERROR: {error_msg}")
        print(f"TRACEBACK: {error_details}")
        return jsonify({"error": error_msg, "details": error_details}), 500

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "alive"})

if __name__ == '__main__':
    # Set environment variables directly if not present
    if 'API_TOKEN' not in os.environ:
        os.environ['API_TOKEN'] = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InlEUVNWODlXdTlLeVJRQ2RzVW5leCJ9.eyJodHRwczovL2FwcC5sYW5kaW5nc2l0ZS5haS9hcHBfbWV0YWRhdGEiOnsiYXV0aG9yaXphdGlvbiI6eyJncm91cHMiOltdLCJwZXJtaXNzaW9ucyI6W10sInJvbGVzIjpbXX19LCJpc3MiOiJodHRwczovL2xhbmRpbmdzaXRlLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2NzlhMThjOTcyZWRkM2RjMGU5MGRhOGMiLCJhdWQiOlsiaHR0cHM6Ly9sYW5kaW5nc2l0ZS51cy5hdXRoMC5jb20vYXBpL3YyLyIsImh0dHBzOi8vbGFuZGluZ3NpdGUudXMuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTc0MDYxNzM4MSwiZXhwIjoxNzQwNzAzNzgxLCJzY29wZSI6Im9wZW5pZCBwcm"
    
    if 'USER_SUB' not in os.environ:
        # For USER_SUB, extract it from the API token's 'sub' claim
        # This is a temporary solution - you need to get the actual USER_SUB from dev tools
        import base64
        import json
        
        try:
            token_parts = os.environ['API_TOKEN'].split('.')
            if len(token_parts) >= 2:
                # Decode the payload part (second part of JWT)
                padding = '=' * (4 - len(token_parts[1]) % 4)
                payload = json.loads(base64.b64decode(token_parts[1] + padding).decode('utf-8'))
                os.environ['USER_SUB'] = payload.get('sub', '')
                print(f"Extracted USER_SUB from token: {os.environ['USER_SUB']}")
            else:
                print("WARNING: Could not extract USER_SUB from token")
        except Exception as e:
            print(f"WARNING: Error extracting USER_SUB: {str(e)}")
    
    print("=== LandingSite AI Automation Service Starting ===")
    print(f"API_TOKEN set: {'API_TOKEN' in os.environ}")
    print(f"USER_SUB set: {'USER_SUB' in os.environ}")
    print(f"Starting server on port {os.getenv('PORT', '8080')}")
    app.run(host='0.0.0.0', port=os.getenv('PORT', '8080'))
