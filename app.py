from flask import Flask, render_template, request, url_for, redirect, session, jsonify, flash
from forms import *
from flask_session import Session
import json
import logging
import requests
import RMQ
import pickle
import uuid

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = "some secret key"
#sess = Session()
app.config["SECRET_KEY"] = "some secret key"
#sess.init_app(app)

tab_names = {
    ("first", "/first"),
    ("second", "/second"),
    ("third", "/third")
}

def update_session_data(data, sk):
    if sk not in session:
        session[sk] = dict()
    for key in data.keys():
        if key not in ("csrf_token", "submit"):
            session[sk][key] = data[key]


def send_data_to_wr():
    print(session)
    selected_os = session["first"].get("selectfield", "Windows 10")
    owner = session["first"].get("textfield", "Purushotham")
    final_json = {
        "WorkReuqest": {
            "os_name": selected_os,
            "owner": owner
        }
    }
    final_json = json.dumps(final_json, indent=4, sort_keys=4)
    validator_json = {"fjson": final_json}
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    response = requests.post(
        url_for("send_to_wre", _external=True),
        json=validator_json, headers=headers)
    print(response)
    print(validator_json)


@app.route("/send_to_wre", methods = ["POST"])
def send_to_wre():
    wr_json = request.json['fjson']
    print(wr_json)
    wreHost = "pchowdam-webui-test.acelab.com"
    complete_hostname = wreHost.lower().strip()
    RMQ.sendData("{}.WRVSubmitQueue".format(complete_hostname.split('.')[0]),
                 pickle.dumps(request.json), complete_hostname, 'guest', 'guest')
    return jsonify({"value": "Sent Work Request to WRE."})

@app.route("/first", methods = ["GET", "POST"])
def first():
    data = dict()
    data["Header"] = "Select Operating System"
    fform = SimpleForm()
    if request.method == "POST":
        update_session_data(fform.data, "first")
        return redirect("second")

    return render_template("first.html", form=fform, data=data)

@app.route("/second", methods = ["GET", "POST"])
def second():
    data = dict()
    data["header"] = ""
    sform = AnotherForm()
    if request.method == "POST":
        wrid = send_data_to_wr()
        print(session)
        session.clear()
        flash("Your request is submitted !!")
        return redirect("/")
    return render_template("index.html", form=sform, data=data)


@app.route('/', methods=['POST', 'GET'])
def hello_world():
    data = dict()
    data["Header"] = "Select Operating System"
    fform = SimpleForm()
    if request.method == "POST":
        update_session_data(fform.data, "first")
        return redirect("second")

    return render_template("first.html", form=fform, data=data)


if __name__ == '__main__':
    app.run(debug=True)
