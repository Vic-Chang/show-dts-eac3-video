import datetime
import math
import os
import configparser
from pathlib import Path
from pymediainfo import MediaInfo
import multiprocessing as mp

config = configparser.ConfigParser()
config.read('config.ini')


def process_pending_file(files_list):
    for file in files_list:
        start_time = datetime.datetime.now()
        check_file(file)
        end_time = datetime.datetime.now()
        time_delta = end_time - start_time
        print('file name:', file)
        print(time_delta.total_seconds())


def check_file(file_path):
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
            print('=========')
            print(media_info.audio_tracks)
            for track in media_info.audio_tracks:
                print('Format: ', track.format)
                for i in track.to_data()['other_format']:
                    print('other_format : ', i)

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
                    print('Found')
    except FileNotFoundError:
        print("File not found : ", file_path)
    except:
        print('Exception raise : ', file_path)


def run():
    print('Script start ...')
    video_folder_path = 'videoFolder'
    if not os.path.exists(video_folder_path):
        os.mkdir(video_folder_path)

    all_files = []
    common_extension = ['.srt', '.ass', '.saa', '.jpg', '.png', '.zip', '.rar', '.7z', '.tar', '.tmp', '.mp3', '.doc',
                        '.docx', '.txt']
    for root, dirs, files in os.walk(video_folder_path):
        for file in files:
            file_extension = Path(file).suffix
            if file_extension not in common_extension:
                file_path = os.path.join(root, file)
                all_files.append(file_path)

    jobs_list = []
    process_count = int(config['Setting']['ProcessCount'])
    average_count = math.ceil(len(all_files) / process_count)
    start_index = 0
    print('The number of process : ', process_count)
    for index in range(process_count):
        end_index = average_count + (index * average_count)
        jobs_list.append(mp.Process(target=process_pending_file, args=(all_files[start_index:end_index],)))
        start_index = end_index

    print('All process start ...')
    for job in jobs_list:
        job.start()

    for job in jobs_list:
        job.join()
    print('===========================================================')
    print('All files are checked ! Container will close automatically.')


if __name__ == '__main__':
    run()
