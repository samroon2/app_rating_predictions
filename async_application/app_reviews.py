#!/usr/bin/env python3

import aiohttp
import asyncio
import os, json
import requests
from datetime import datetime
from quart import Quart, jsonify, request, url_for, make_response, render_template
from flask_sqlalchemy import SQLAlchemy

app = Quart(__name__)

db_path = os.path.join(os.path.dirname(__file__), 'app.db')
db_uri = 'sqlite:///{}'.format(db_path)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
db = SQLAlchemy(app)

async def get_pred(url, data):
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=json.dumps(data), headers=headers) as response:
            pred = await response.json(content_type=None)
            return {'url':url, 'pred': pred}

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
        return str({'title': self.review_title, 'body': self.review, 'stars': self.stars, 'sent': self.sent})


@app.route('/')
async def review_form():
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
        new_review = AppReview(app, review_title.strip(), review.strip(), predicted_pos.strip(), sub_pos.strip(), predicted_stars, sub_stars)
        db.session.add(new_review)
        db.session.commit()
        return await render_template("review_form.html", app_names=apps,
                                review_title=None, review=None,
                                pred_stars=None, pred_pos=None
                                )
    if review:
        data = {'title': review_title, 'review': review}
        urls = ["http://127.0.0.1:81/score", "http://127.0.0.1:80/score"]
        futures = [asyncio.ensure_future(get_pred(url, data)) for url in urls]
        preds = []
        for future in futures:
            resp = await future
            preds.append(resp)
      
        pred_stars = [x.get('pred').get('stars') for x in preds if x.get('url') == "http://127.0.0.1:81/score"][0]
        pos = [x.get('pred').get('pos_neg') for x in preds if x.get('url') == "http://127.0.0.1:80/score"][0]
        prob = [x.get('pred').get('prob') for x in preds if x.get('url') == "http://127.0.0.1:80/score"][0]
        pos = f'{pos}, {prob}'

    return await render_template("review_form.html", app_names=apps,
                            review_title=review_title if review_title else None,
                            review=review if review else None,
                            pred_stars=pred_stars if pred_stars else None,
                            pred_pos=pos if pos else None
                            )

if __name__ == "__main__":
    app.debug = True
    app.run(port=5000)