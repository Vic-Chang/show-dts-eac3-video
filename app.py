import os
from os import listdir
from os.path import isfile, join
from pymediainfo import MediaInfo

videoFolderPath = 'videoFolder'

# todo: 遞迴抓取該資料夾底下的所有影片檔
videoFiles = [f for f in listdir(videoFolderPath) if isfile(join(videoFolderPath, f))]

for item in videoFiles:
    check_flag = False
    item = os.path.join(videoFolderPath, item)
    media_info = MediaInfo.parse(item)
    for track in media_info.tracks:
        if track.track_type == "Audio":
            print(track.to_data()['other_format'])
            if any (x in codec_format for codec_format in track.to_data()['other_format'] for x in ['DTS','E-AC-3']):
                print('Found~')
    print('===================')

