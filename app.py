from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from datetime import datetime

import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/diary', methods=['GET'])
def show():
    articles = list(db.diary.find({}, {'_id': False}))
    return jsonify({'articles': articles})


@app.route('/diary', methods=['POST'])
def save():
    # terima data dari form
    title_receive = request.form.get('title_give')
    content_receive = request.form.get('content_give')
    
    today = datetime.now()
    mytime = today.strftime("%Y-%m-%d-%H-%M-%S")
    
    file = request.files["file_give"]
    ext = file.filename.split('.')[-1]
    filename = f'static/post-{mytime}.{ext}'
    file.save(filename)
    
    profile = request.files["profile_give"]
    ext2 = profile.filename.split('.')[-1]
    profilename = f'static/profile-{mytime}.{ext2}'
    profile.save(profilename)
    
    post_time = today.strftime('%d-%m-%Y')
    
    count = db.diary.count_documents({})
    num = count + 1
    
    # masukan datanya ke list mongodb
    doc = {
        'file' : filename,
        'profile' : profilename,
        'title' : title_receive,
        'content' : content_receive,
        'time' : post_time,
        'num' : num
    }
    # insert kedalam database
    db.diary.insert_one(doc)
    
    #kembalikan respone ke client
    return jsonify({'msg' : 'Diary saved successfully'})

@app.route("/delete", methods=["POST"])
def delete_diary():
    diary_num = request.form['num_give']
    db.diary.delete_one({'num': int(diary_num)})
    return jsonify({'msg': 'Diary deleted successfully'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)