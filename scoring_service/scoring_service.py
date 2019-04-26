import keras
import os, json, sys, pickle
from flask import Flask, jsonify, request
from keras.preprocessing.sequence import pad_sequences
from sklearn.externals import joblib
sys.path.insert(0, '../code/')
from text_cleaning import TextClean
import tensorflow as tf

config = tf.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.Session(config=config)
with open('project_info.json') as f:
	info = json.loads(f.read())

with open("./models/"+info['tokenizer'], 'rb') as handle:
    tokenizer = pickle.load(handle)

cleaner = TextClean('.')

model = keras.models.load_model("./models/"+info['model'])
model._make_predict_function()

app = Flask(__name__)

@app.route('/score', methods=['POST'])
def predict_stars():

	try:
		postjson = request.json
	except Exception as e:
		raise e

	title = postjson['title']
	review = postjson['review']

	clean_text = cleaner.clean(title+'. '+review)

	print(clean_text)

	X = tokenizer.texts_to_sequences([clean_text])
	print(X)
	X = pad_sequences(X, info['max_sequence'])

	print(X.shape)

	if not postjson:
		return(bad_request())

	pred = model.predict(X)

	apiresponse = jsonify({'stars':pred.argmax(axis=1).tolist()[0]})
	apiresponse.status_code = 200

	return (apiresponse)

if __name__ == "__main__":
	app.run(port=80)