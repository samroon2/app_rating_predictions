import keras
import os, json, sys, pickle
import tensorflow as tf
from quart import Quart, jsonify, request, make_response
from keras.preprocessing.sequence import pad_sequences
from sklearn.externals import joblib
sys.path.insert(0, '../code/')
from text_cleaning import TextClean


# https://github.com/tensorflow/tensorflow/issues/24496
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.Session(config=config)

# Open project info and load tokenizer.
with open('binary_project_info.json') as f:
    info = json.loads(f.read())
with open("./models/"+info['tokenizer'], 'rb') as handle:
    tokenizer = pickle.load(handle)

cleaner = TextClean('.')

# Load model, store in memory to reduce request fulfillment time (loading the model every request takes time and can cause problems).
model = keras.models.load_model("./models/"+info['model'])
model._make_predict_function()

app = Quart(__name__)

@app.route('/score', methods=['POST'])
async def predict_stars():
    '''API scoring function, requires http POST request to contain 'title' and 'review'.
    '''

    try:
        postjson = await request.json
    except Exception as e:
        raise e

    # Check request isn't empty or missing required information.    
    if not postjson or [x for x in ['review', 'title'] if x not in postjson.keys()]:
        return make_response(jsonify({'error': 'Missing required information, "title" or "review".'}), 400)

    title = postjson['title']
    review = postjson['review']

    # Process request data.
    clean_text = cleaner.clean(title+'. '+review)

    X = tokenizer.texts_to_sequences([clean_text])
    X = pad_sequences(X, info['max_sequence'])

    # Make prediction.
    pred = model.predict(X)

    # Return prediction.
    apiresponse = jsonify({'prob':str(pred[0][0]), 'pos_neg':'Positive' if pred[0][0] >= 0.5 else 'Negative'})
    apiresponse.status_code = 200

    return (apiresponse)

if __name__ == "__main__":
    app.run(port=80)