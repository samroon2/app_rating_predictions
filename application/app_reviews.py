#!/usr/bin/env python3

import os, json
import requests
from datetime import datetime
from flask import Flask, jsonify, request, url_for, make_response, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

db_path = os.path.join(os.path.dirname(__file__), 'app.db')
db_uri = 'sqlite:///{}'.format(db_path)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
db = SQLAlchemy(app)

#-------------------------------------------------------------------------------------------------------------------------------------------
# Data Models
# Migrations: from app import db --> db.create_all()

class AppReview(db.Model):
    '''Data model for job requests.
    '''
    review_id = db.Column(db.Integer, primary_key=True)
    review_date = db.Column(db.DateTime, unique=False, nullable=False, default=datetime.now)
    app_name = db.Column(db.String(20), unique=False, nullable=True)
    review_title = db.Column(db.String(180), unique=False, nullable=True)
    review = db.Column(db.String(180), unique=False, nullable=True)
    predicted_sent = db.Column(db.String(10), unique=False, nullable=True)
    sent = db.Column(db.String(10), unique=False, nullable=True)
    predicted_stars = db.Column(db.Integer)
    stars = db.Column(db.Integer)

    def __init__(self, app_name:str, review_title: str, review: str, predicted_sent: str, sent: str, predicted_stars: int, stars: int):
        self.app_name = app_name
        self.review_title = review_title
        self.review = review
        self.predicted_sent = predicted_sent
        self.sent = sent
        self.predicted_stars = predicted_stars
        self.stars = stars

    def __repr__(self):
        return str({'title': review_title, 'body':review, 'stars':stars, 'sent':sent})


@app.route('/')
def review_form():
    '''Route for submitting app reviews.
    '''
    review_title = request.args.get('review_title', False)
    review = request.args.get('review', False)
    sub_stars = request.args.get('stars', False)
    predicted_stars = request.args.get('pred_stars', False)
    sub_pos = request.args.get('pos', False)
    predicted_pos = request.args.get('pred_pos', False)
    app = request.args.get('app_name')

    print(request.args)

    apps = ['App 1']

    pred_stars = False
    pos = False
    prob = False

    if review and sub_stars:
        new_review = AppReview(app, review_title.strip(), review.strip(), predicted_pos, sub_pos, predicted_stars, sub_stars)
        db.session.add(new_review)
        db.session.commit()
        return render_template("review_form.html", app_names=apps,
                                review_title=None,
                                review=None,
                                pred_stars=None,
                                pred_pos=None
                                )
    if review:
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        data = {'title': review_title, 'review': review}
        req = requests.post("http://127.0.0.1:81/score", data=json.dumps(data), headers=headers)
        pred_stars = req.json()['stars']
        req = requests.post("http://127.0.0.1:80/score", data=json.dumps(data), headers=headers)
        pos = req.json()['pos_neg']
        prob = req.json()['prob']
        pos = f'{pos}:{prob}'

    return render_template("review_form.html", app_names=apps,
                            review_title=review_title if review_title else None,
                            review=review if review else None,
                            pred_stars=pred_stars if pred_stars else None,
                            pred_pos=pos if pos else None
                            )

if __name__ == "__main__":
    app.debug = True
    app.run(port=5000)