"""
#함수 호출 예시

slice_id = [
	'Zx1n1R_OQs0ㅡ2',
	'Ekidn3lkD0gㅡ3',
	'0JEdj4ih_i4ㅡ16'
]
target_bpm = 105 -> 사용자가 input한 음악의 bpm

editor = CrossEditor()
editor.video_merge(slice_id, target_bpm)
"""

import os
import cv2
import youtube_dlc

class CrossEditor:
    # ffmpeg에 시간 정보 넣어주기 위해 사용
    @staticmethod
    def sec_to_time(sec):
        time = ""
        temp = 0
        for i in range(3):
            temp = sec % 60
            time = str(sec % 60) + time if temp >= 10 else "0" + str(temp) + time
            sec //= 60
            if i < 2:
                time = ":" + time
        return time

    # slice_id list, 사용자 input 음악의 bpm
    @staticmethod
    def video_merge(slice_id, target_bpm):
        vidlink = []
        start_frame = []
        end_frame = []
        bpm = []
        x_mean = []
        y_min = []
        y_max = []

        for sid in slice_id:
            vidlink.append('choleor_media/choreo/SLICE/choreo_id/choreo_id_idx/'+slice_id+'.mp4')

#여기 DB에서 불러온 데이터 넣어줘야함
        for i in range(len(slice_id)):
            start_frame.append("""slice_id[i]의 start_frame""" + 10)
            end_frame.append("""slice_id[i]의 end_frame""" - 10)
            bpm.append("""slice_id[i]의 bpm""")

        for i in range(len(slice_id)-1):
            x_m = []
            x_m.append("""slice_id[i]의 end_pose의 x_mean""")
            x_m.append("""slice_id[i+1]의 start_pose의 x_mean""")
            x_mean.append(x_m)

            y_m = []
            y_m.append("""slice_id[i]의 end_pose의 y_min""")
            y_m.append("""slice_id[i+1]의 start_pose의 y_min""")
            y_min.append(y_m)

            y_M = []
            y_M.append("""slice_id[i]의 end_pose의 y_max""")
            y_M.append("""slice_id[i+1]의 start_pose의 y_max""")
            y_max.append(y_M)
# """
# 여기까지 수행한 결과
#
# vidlink = [
#     'https://www.youtube.com/watch?v=Zx1n1R_OQs0',
#     'https://www.youtube.com/watch?v=Zx1n1R_OQs0',
#     'https://www.youtube.com/watch?v=Zx1n1R_OQs0'
# ]
# start_frame = [103, 202, 301]
# end_frame = [222, 321, 421]
# bpm = [72, 72, 72]
# x_mean = [[635, 635], [468, 468]]
# y_min = [[370, 370], [329, 329]]
# y_max = [[857, 857], [892, 892]]
# """

        ## 사람 크기 맞추고 영상 크기 조절 & 변화 상태에서 원래 상태로 천천히 돌아오기

        os.system('cp %s vid1_0.mp4' % (vidlink[0]))

        for idx in range(1, len(vidlink)):
            # 영상 호출
            vidcap = cv2.VideoCapture(vidlink[idx])
            fps = vidcap.get(cv2.CAP_PROP_FPS)
            frame_num = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)
            change_value = 0
            count = 0
            curr = 0

            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter('vid1_' + str(idx) + '.mp4', fourcc, fps, (1920, 1080))

            # 사람 크기 동일하게 조절 값 구하기
            resize_ratio = (y_max[idx - 1][0] - y_min[idx - 1][0]) / (y_max[idx - 1][1] - y_min[idx - 1][1])
            resized_x = (int)(1920 * resize_ratio)
            resized_y = (int)(1080 * resize_ratio)

            # 사람 위치 동일하게 조절 & 영상 사이즈 동일하게 조절 값 구하기
            Cx1 = Cy1 = 0
            Cx2 = resized_x
            Cy2 = resized_y
            Mx1 = Mx2 = My1 = My2 = 0
            rx_mean = (int)(x_mean[idx-1][1] * resize_ratio)
            ry_max = (int)(y_max[idx-1][1] * resize_ratio)
            ry_min = (int)(y_min[idx-1][1] * resize_ratio)

            if x_mean[idx - 1][0] > rx_mean:  # 인물 왼쪽 사이즈 조절
                Mx1 = x_mean[idx - 1][0] - rx_mean
            else:
                Cx1 = rx_mean - x_mean[idx - 1][0]

            if 1920 - x_mean[idx - 1][0] > resized_x - rx_mean:  # 인물 오른쪽 사이즈 조절
                Mx2 = (1920 - x_mean[idx - 1][0]) - (resized_x - rx_mean)
            else:
                Cx2 = resized_x - ((resized_x - rx_mean) - (1920 - x_mean[idx - 1][0]))

            if y_min[idx - 1][0] > ry_min:  # 인물 상단 사이즈 조절
                My1 = y_min[idx - 1][0] - ry_min
            else:
                Cy1 = ry_min - y_min[idx - 1][0]

            if 1080 - y_max[idx - 1][0] > resized_y - ry_max:  # 인물 하단 사이즈 조절
                My2 = (1080 - y_max[idx - 1][0]) - (resized_y - ry_max)
            else:
                Cy2 = resized_y - ((resized_y - ry_max) - (1080 - y_max[idx - 1][0]))

            # 실제 영상 편집 시작
            while vidcap.isOpened():
                ret, image = vidcap.read()

                if ret is False:
                    break

                curr += 1
                if 20 < curr < (frame_num - 20):
                    count += 1
                    change_value = count / (frame_num - 40)

                resized_xC = resized_x + (int)((1920 - resized_x) * change_value)
                resized_yC = resized_y + (int)((1080 - resized_y) * change_value)

                resize = cv2.resize(image, dsize=(resized_xC, resized_yC), interpolation=cv2.INTER_AREA)

                Cx1C = Cx1 + (int)((0 - Cx1) * change_value)
                Cx2C = Cx2 + (int)((1920 - Cx2) * change_value)
                Cy1C = Cy1 + (int)((0 - Cy1) * change_value)
                Cy2C = Cy2 + (int)((1080 - Cy2) * change_value)

                Mx1C = Mx1 + (int)((0 - Mx1) * change_value)
                Mx2C = Mx2 + (int)((0 - Mx2) * change_value)
                My1C = My1 + (int)((0 - My1) * change_value)
                My2C = My2 + (int)((0 - My2) * change_value)

                crop = resize.copy()
                crop = resize[Cy1C:Cy2C, Cx1C:Cx2C]

                margin = cv2.copyMakeBorder(crop, My1C, My2C, Mx1C, Mx2C, cv2.BORDER_CONSTANT, value=[0, 0, 0])

                final = cv2.resize(margin, dsize=(1920, 1080), interpolation=cv2.INTER_AREA)

                out.write(final)
                # os.remove('vid2_'+str(idx)+'.mp4')

            vidcap.release()
            out.release()
            cv2.destroyAllWindows()

        ## 모든 영상 24 fps로 맞추기
        for idx in range(len(vidlink)):
            os.system("ffmpeg -i 'vid1_%d.mp4' -r 24 -y 'vid2_%d.mp4'" % (idx, idx))
            os.remove('vid1_'+str(idx)+'.mp4')

        # 영상 이어붙이기 (fade in & out 있음)
        target_fps = target_bpm * 24 / 120
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('result.mp4', fourcc, target_fps, (1920, 1080))

        for idx in range(1, len(vidlink)):

            vidcap1 = cv2.VideoCapture('vid2_'+str(idx-1)+'.mp4')
            vidcap2 = cv2.VideoCapture('vid2_'+str(idx)+'.mp4')

            end = int(vidcap1.get(cv2.CAP_PROP_FRAME_COUNT))

            count = 0

            while (vidcap1.isOpened() and vidcap2.isOpened()):
                count += 1

                if count > end:
                    break;

                else:
                    if count < end - 20:
                        ret1, image1 = vidcap1.read()

                        if count <= 20:
                            continue;

                        out.write(image1)
                    elif count < end:
                        ret1, image1 = vidcap1.read()
                        ret2, image2 = vidcap2.read()

                        if(ret1 == False or ret2 == False):
                            break

                        blending = cv2.addWeighted(image1, ((end - count) / 20), image2, 1 - ((end - count) / 20), 0)
                        out.write(blending)
                    else:
                        ret2, image2 = vidcap2.read()
                        out.write(image2)
            vidcap1.release()
            vidcap2.release()

        os.remove('vid2_'+str(idx-1)+'.mp4')

        #마지막 영상 뒷부분 합치기
        vidcap1 = cv2.VideoCapture('vid2_'+str(len(vidlink)-1)+'.mp4')
        end = int(vidcap1.get(cv2.CAP_PROP_FRAME_COUNT))
        count = 0

        while (vidcap1.isOpened()):
            count += 1
            if count > end:
                break

            else:
                ret1, image1 = vidcap1.read()
                if count <= 20:
                    continue

                out.write(image1)

        vidcap1.release()
        out.release()

        os.remove('vid2_'+str(len(vidlink)-1)+'.mp4')
