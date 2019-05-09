import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter
import string
import pandas as pd
from nltk import pos_tag
from nltk.stem import PorterStemmer
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import Pool, cpu_count
import emoji
import random
import os, json


class TextClean:

    def __init__(self, data_location, **kwargs):
        self.data_location = data_location
        self.dir_setup= kwargs.get('dir_setup', False) 
        self.data = []
        self.app_name = kwargs.get('app_name', False)
        self.exisiting = []
        self.dir_prep()

    def dir_prep(self):
        if self.dir_setup and 'temp_pre' not in os.listdir('.') and self.dir_setup:
            os.mkdir('temp_pre')
        else:
            [self.exisiting.append(x) for x in os.listdir('./temp_pre')] if self.dir_setup else None

    def load_data(self):
        for file in os.listdir(self.data_location):
            with open(self.data_location+'/'+file) as f:
                j = json.load(f)
                [self.data.append(x) for x in j]
        print(self.data[0])

    def clean(self, text):
        text = str(emoji.demojize(text))
        text2 = " ".join("".join([" " if ch in string.punctuation else ch for ch in text]).split())
        tokens = [word.lower() for sent in nltk.sent_tokenize(text2) for word in
                  nltk.word_tokenize(sent)]
        return " ".join([token for token in tokens if token not in stopwords.words('english') and len(token)>=3])

    def write_to_json(self, file, data):    
        with open(file, 'w') as outfile:
            json.dump(data, outfile)

    def process_data(self, data_chunk):
        new = []
        print(len(data_chunk))
        for data in data_chunk:
            txt = self.clean(data['title']+ '. ' + data['review'])
            data['cleaned_text'] = txt
            new.append(data)

        self.write_to_json(f"./temp_pre/outfile_{len(os.listdir('./temp_pre'))}.json", new)

    def combine_products(self):
        #new_files = [x for x in os.listdir('./temp_pre') if x not in self.exisiting]
        new_files = [x for x in os.listdir('./temp_pre')]
        print(new_files)
        data = []
        for file in new_files:
            with open('./temp_pre/'+file) as f:
                j = json.load(f)
                [data.append(i) for i in j]
        self.write_to_json(f"./temp_pre/{self.app_name if self.app_name else 'combined_outfile'}_{len(os.listdir('./temp_pre'))}.json", data)

    def multi_process(self):
        workers = cpu_count()
        pool = Pool(processes=workers)    
        result = pool.map(self.process_data, [self.data[i::workers] for i in range(workers)])
        self.combine_products()
   
    def even_sample(self, X, y):
        cnts = Counter(y)
        minimum = min(cnts, key=cnts.get)
        min_count = cnts[minimum] + 1000
        fives = []
        fours = []
        threes = []
        twos = []
        ones = []
        for n, i in enumerate(X):
            if y[n] == '5 stars' or y[n] == 5:
                fives.append([i, y[n]])
            elif y[n] == '4 stars' or y[n] == 4:
                fours.append([i, y[n]])
            elif y[n] == '3 stars' or y[n] == 3:
                threes.append([i, y[n]])
            elif y[n] == '2 stars' or y[n] == 2:
                twos.append([i, y[n]])
            elif y[n] == '1 star' or y[n] == 1:
                ones.append([i, y[n]])
                
        data = []        
        for x in [fives, fours, threes, twos, ones]:
            random.shuffle(x)
            data = data + x[:min_count]
        random.shuffle(data)
        X_ = [x[0] for x in data]
        y_ = [x[1] for x in data]
        return X_, y_ 

def main():
    a = TextClean('../data', app_name='temple_')
    #a.multi_process()
    a.combine_products()

if __name__ == '__main__':
    main()