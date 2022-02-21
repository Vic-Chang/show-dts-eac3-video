import os
from pymediainfo import MediaInfo
import multiprocessing as mp


class ShowVideoInfo:
    def __init__(self, path):
        self.path = path
        self.track_count = 0
        self.format = []
        self.other_format = []

    def show_info(self):
        print(f'{self.path}')
        print(f'共 {self.track_count} 個音軌')
        print(f'主格式: {", ".join(self.format)}')
        print(f'其他格式: {", ".join(self.other_format)}')


def process_mp(files_list):
    for file in files_list:
        process_file(file)


def process_file(file_path):
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
    print('Process start ...')
    video_folder_path = 'videoFolder'
    if not os.path.exists(video_folder_path):
        os.mkdir(video_folder_path)
    all_files = []
    for root, dirs, files in os.walk(video_folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            all_files.append(file_path)

    jobs_list = []
    half_files_count = int(len(all_files) / 2)
    jobs_list.append(mp.Process(target=process_mp, args=(all_files[: half_files_count],)))
    jobs_list.append(mp.Process(target=process_mp, args=(all_files[half_files_count:],)))
    for job in jobs_list:
        job.start()

    for job in jobs_list:
        job.join()
    print('All files are checked ! Container will close automatically.')


if __name__ == '__main__':
    run()
