# from flask import Flask

# app = Flask(__name__)
import os.path
import configparser
from os import listdir
from os.path import isfile, join

config = configparser.ConfigParser()
config.read('config.ini')
mypath = config['VideoFolder']['Path']
videoFiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
from pymediainfo import MediaInfo

for item in videoFiles:
    check_flag = False
    item = os.path.join(mypath,item)
    print(item)
    media_info = MediaInfo.parse(item)
    for track in media_info.tracks:
        if track.track_type == "Audio":
            print(track.to_data()['other_format'])
            if any (x in codec_format for codec_format in track.to_data()['other_format'] for x in ['DTS','E-AC-3']):
                print('Found~')
    print('===================')


# @app.route('/')
# def index_page():
#     return 'This is a tool for show video with dts and eac3 audio'


# if __name__ == '__main__':
    # app.run()
