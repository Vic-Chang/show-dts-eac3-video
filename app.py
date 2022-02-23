import datetime
import math
import os
import configparser
import multiprocessing as mp
from multiprocessing import Queue
from pathlib import Path
from pymediainfo import MediaInfo

config = configparser.ConfigParser()
config.read('config.ini')

show_info = bool(int(config['Setting']['ShowDetail']))


def print_info(value):
    global show_info
    if show_info:
        print(value)


def process_pending_file(que, files_list):
    for file in files_list:
        start_time = datetime.datetime.now()
        check_file(que, file)
        end_time = datetime.datetime.now()
        time_delta = end_time - start_time
        print_info(f'File processing time spent : {time_delta.total_seconds()} s')


def check_file(que, file_path):
    try:
        media_info = MediaInfo.parse(file_path)

        is_video_flag = False
        for track in media_info.tracks:
            if track.track_type == "Video":
                is_video_flag = True
                break

        """
        目標有可能的格式類型:
        'E-AC-3'
        'DTX'
        'DTX XLL X'
        """
        detect_format_list = ['DTS', 'E-AC-3']
        if is_video_flag:
            print_info('=========')
            print_info(f'File path: {file_path}')
            print_info(f'Audio tracks count: {len(media_info.audio_tracks)}')
            for track in media_info.audio_tracks:
                print_info(f'   Audio format: {track.format}')
                for i in track.to_data()['other_format']:
                    print_info(f'       other_format : {i}')

            detect_format_flag = False
            # 檢查所有音軌是否含有 DTS 或是 EAC3
            for track in media_info.audio_tracks:
                if any(format_type in track.format for format_type in detect_format_list) \
                        or any(x in codec_format for codec_format in track.to_data()['other_format'] for x in
                               detect_format_list):
                    detect_format_flag = True
                    break

            # 若音軌格式出現 DTS 或是 EAC3 ，則要確認是否還有其他可用音軌
            # 若無其他音軌則代表該檔案無法撥放
            if detect_format_flag:
                has_other_format_type = False
                for track in media_info.audio_tracks:
                    # 看格式是否非 DTS 或 EAC3
                    if not any(format_type in track.format for format_type in detect_format_list):
                        has_other_format_type = True
                        break

                    # 尋找清單內是否有非 DTS 或 EAC3 格式
                    for other_format in track.to_data()['other_format']:
                        if not any(format_type in other_format for format_type in detect_format_list):
                            has_other_format_type = True
                            break

                if not has_other_format_type:
                    print_info("> [X] This file can't be played !")
                    que.put((file_path, media_info.audio_tracks[0].format))
    except FileNotFoundError:
        print("[!] File not found : ", file_path)
    except Exception as e:
        print('[!] Exception raise : ', e)


def run():
    script_start_time = datetime.datetime.now()
    print('Script start ...')
    video_folder_path = 'videoFolder'
    if not os.path.exists(video_folder_path):
        os.mkdir(video_folder_path)

    all_files = []
    result_file = []
    common_extension = ['.srt', '.ass', '.saa', '.jpg', '.png', '.zip', '.rar', '.7z', '.tar', '.tmp', '.mp3', '.doc',
                        '.docx', '.txt', '.vsmeta', '.nfo', '.torrent', '.sub', '.idx', '.sup', '.lock']
    for root, dirs, files in os.walk(video_folder_path):
        for file in files:
            file_extension = Path(file).suffix
            # 在群輝上會有無副檔名索引檔或是特殊符號副檔名
            if file_extension.lower() not in common_extension and file_extension != '' and '@' not in file_extension:
                file_path = os.path.join(root, file)
                all_files.append(file_path)

    jobs_list = []
    process_count = int(config['Setting']['ProcessCount'])
    average_count = math.ceil(len(all_files) / process_count)
    start_index = 0
    print('The number of process : ', process_count)
    que = Queue()
    for index in range(process_count):
        end_index = average_count + (index * average_count)
        jobs_list.append(mp.Process(target=process_pending_file, args=(que, all_files[start_index:end_index],)))
        start_index = end_index

    print(f'{len(all_files)} files to be checked.')
    print('All process start ...')
    for job in jobs_list:
        job.start()

    for job in jobs_list:
        job.join()

    script_end_time = datetime.datetime.now()
    time_delta = script_end_time - script_start_time
    print('===========================================================')
    print(f'{len(all_files)} files are checked !')
    print('Result:')
    if que.qsize() > 0:
        print(f'   Found {que.qsize()} video with DTS, EAC3 audio format !')
        for index in range(que.qsize()):
            (file_path, audio_format) = que.get()
            print(f'      {index+1}. {file_path}')
            print(f'         Audio Format: {audio_format}')
    else:
        print('   No DTS, EAC3 audio format video file found.')
    print(f'Total time spent : {time_delta.total_seconds()} s')
    print('Container will close automatically.')


if __name__ == '__main__':
    run()
