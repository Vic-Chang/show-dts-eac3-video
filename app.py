import os
from pymediainfo import MediaInfo

video_folder_path = 'videoFolder'
if not os.path.exists(video_folder_path):
    os.mkdir(video_folder_path)

for root, dirs, files in os.walk(video_folder_path):
    for file in files:
        file_path = os.path.join(root, file)
        media_info = MediaInfo.parse(file_path)

        is_video_flag = False
        for track in media_info.tracks:
            if track.track_type == "Video":
                is_video_flag = True
                break

        print('==============')
        print(media_info.audio_tracks)
        """
        目標有可能的格式類型:
        'E-AC-3'
        'DTX'
        'DTX XLL X'
        """
        detect_format_list = ['DTS', 'E-AC-3']
        if is_video_flag:
            detect_format_flag = False
            # 檢查所有音軌是否含有 DTS 或是 EAC3
            for track in media_info.audio_tracks:
                print(track.format)
                if any(format_type in track.format for format_type in detect_format_list)\
                        or any(x in codec_format for codec_format in track.to_data()['other_format'] for x in detect_format_list):
                    detect_format_flag = True
                    break

            # 若音軌格式出現 DTS 或是 EAC3 ，則要確認是否還有其他可用音軌
            # 若無其他音軌則代表該檔案無法撥放
            if detect_format_flag :
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
