#!/usr/bin/env python3

import os, json
import pandas as pd
import requests
from flask import Flask, jsonify, request, url_for, make_response, render_template

app = Flask(__name__)

@app.route('/')
def review_form():
    '''Route for submitting app reviews.
    '''
    review_title = request.args.get('review_title')
    review = request.args.get('review')

    apps = ['App 1']

    stars = False

    if review:
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        data = {'title': review_title, 'review': review}
        req = requests.post("http://127.0.0.1:80/score", data=json.dumps(data), headers=headers)
        stars=req.json()['stars']

    return render_template("review_form.html", app_names=apps,
                            review_title=review_title if review_title else None,
                            review=review if review else None,
                            stars=stars if stars else None)

if __name__ == "__main__":
    app.debug = True
    app.run()