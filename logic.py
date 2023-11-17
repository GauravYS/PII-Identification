from flask import Flask, render_template, request
import os
from google.cloud import dlp_v2

app = Flask(__name__)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"

dlp_client = dlp_v2.DlpServiceClient()

info_types = [
    {"name": "INDIA_PAN_INDIVIDUAL"},
    {"name": "US_SOCIAL_SECURITY_NUMBER"},
    {"name": "IBAN_CODE"},
    {"name": "PASSWORD"},
    {"name": "DOMAIN_NAME"},
    {"name": "EMAIL_ADDRESS"},
    {"name": "SWIFT_CODE"},
    {"name": "US_BANK_ROUTING_MICR"},
    {"name": "AMERICAN_BANKERS_CUSIP_ID"}
]

parent = "projects/turnkey-env-392723/locations/global"

inspect_config = {
    "info_types": info_types,
    "include_quote": True,
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_content', methods=['POST'])
def process_content():
    content = request.form['content']
    item = {"value": content}

    request_dlp = {
        "parent": parent,
        "inspect_config": inspect_config,
        "item": item,
    }

    response = dlp_client.inspect_content(request=request_dlp)

    if response.result.findings:
        for finding in response.result.findings:
            content = content.replace(finding.quote, "###")

    masked_sentence = content

    total_detected = len(response.result.findings)
    total_likelihood = sum(finding.likelihood for finding in response.result.findings)
    mean_likelihood = total_likelihood / len(info_types)
   # mean_percentage = mean_likelihood * 100

    if mean_likelihood > 2.2:
        alert_message = "Click on the alert button"
    else:
        alert_message = ""

    return render_template('index.html', masked_sentence=masked_sentence, alert_message=alert_message, mean_percentage=mean_likelihood)

@app.route('/alert', methods=['GET'])
def alert():

    alert_message = "You are passing sensitive information which exceeds the threshold value for PII's. Do not send such information unless absolutely needed !"
    return render_template('alert.html', alert_message=alert_message)


if __name__ == '__main__':
    app.run(debug=True)




