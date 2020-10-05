#TODO 지현이 코드 넣기
import os
import cv2
import youtube_dl
import numpy as np
from PIL import Image

#ffmpeg에 시간 정보 넣어주기 위해 사용
def sec_to_time(sec):
    time = ""
    temp = 0

    for i in range(3):
        temp = sec % 60
        if temp < 10:
            time = "0" + str(temp) + time
        else:
            time = str(sec % 60) + time
        sec = sec // 60

        if i < 2:
            time = ":" + time

    return time

#DB에서 데이터 가져오는거 함수 안에서 할지 밖에서 할지 정해야함
#영상 다운 받는 부분 빼야함
#중간단계 영상들이 코드가 있는 폴더와 같은 폴더에 저장되고 그 영상을 다시 읽어오면서 코드가 진행되는데 이 부분 어떻게할지
def video_merge(vidlink):
    vidlink = [
    'https://www.youtube.com/watch?v=QDqlB8M25DQ',
    'https://www.youtube.com/watch?v=Pg-SswwMc9w'
    ]
    start_frame = [560, 660]
    end_frame = [660, 760]
    y_max = [933, 957]
    y_min = [323, 264]
    x_mean = [1402, 916]
    bpm = [109, 102]
    fps = [0 for i in range(len(bpm))]
    target_bpm = 100


    ## 필요한 부분 영상 다운받기

    ydl = youtube_dl.YoutubeDL({'format': '137'}, )

    for idx in range(len(vidlink)):

        with ydl:
            video = ydl.extract_info(
                vidlink[idx],
                download=False
            )
        #print(video)
        url = video['url']
        fps[idx] = video['fps']

        start_sec = ((start_frame[idx]-10) // fps[idx]) - 1
        end_sec = ((end_frame[idx]+10) // fps[idx]) + 1

        print(start_sec, end_sec)

        start_time = sec_to_time(start_sec)
        duration_time = sec_to_time(end_sec - start_sec)

        print(start_time, duration_time)

        os.system("ffmpeg -i '%s' -ss %s -t %s -async 1 -strict -2 'vid1_%d.mp4'" % (url, start_time, duration_time, idx))
        
    ## 필요한 프레임만 남기면서 흑백으로 변환 & 노래 120bpm 되도록 영상 속도 조절

    for idx in range(len(vidlink)):
        vidcap = cv2.VideoCapture('vid1_'+str(idx)+'.mp4')

        org_fps = vidcap.get(cv2.CAP_PROP_FPS)
        mod_fps = 120 * org_fps / bpm[idx]

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('vid2_'+str(idx)+'.mp4', fourcc, mod_fps, (1920, 1080), 0)

        org_start_frame = (((start_frame[idx]-10) // fps[idx]) - 1) * fps[idx] + 1
        org_end_frame = (((end_frame[idx]+10) // fps[idx]) + 1) * fps[idx] - 1

        count = 0

        while(vidcap.isOpened()):
            ret, image = vidcap.read()
            count += 1

            if(count <= start_frame[idx] - 10 - org_start_frame):
                continue
            if(count > end_frame[idx] + 10 - org_start_frame + 1):
                break

            if ret == False:
                break
            else:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                out.write(gray)

        os.remove('vid1_'+str(idx)+'.mp4')

        out.release()
        vidcap.release()

    ## 사람 크기 맞추고 영상 크기 조절 & 변화 상태에서 원래 상태로 천천히 돌아오기

    os.system('cp vid2_0.mp4 vid3_0.mp4')

    for idx in range(1, len(vidlink)):
        #영상 호출
        vidcap = cv2.VideoCapture('vid2_'+str(idx)+'.mp4')
        fps = vidcap.get(cv2.CAP_PROP_FPS)
        frame_num = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)
        change_value = 0
        count = 0
        curr = 0

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('vid3_'+str(idx)+'.mp4', fourcc, fps, (1920, 1080))

        #사람 크기 동일하게 조절 값 구하기
        resize_ratio = (y_max[idx-1] - y_min[idx-1]) / (y_max[idx] - y_min[idx])
        resized_x = (int)(1920 * resize_ratio)
        resized_y = (int)(1080 * resize_ratio)

        #사람 위치 동일하게 조절 & 영상 사이즈 동일하게 조절 값 구하기
        Cx1 = Cy1 = 0
        Cx2 = resized_x
        Cy2 = resized_y
        Mx1 = Mx2 = My1 = My2 = 0
        rx_mean = (int)(x_mean[idx] * resize_ratio)
        ry_max = (int)(y_max[idx] * resize_ratio)
        ry_min = (int)(y_min[idx] * resize_ratio)

        if x_mean[idx-1] > rx_mean: # 인물 왼쪽 사이즈 조절
            Mx1 = x_mean[idx-1] - rx_mean
        else:
            Cx1 = rx_mean - x_mean[idx-1]

        if 1920 - x_mean[idx-1] > resized_x - rx_mean: # 인물 오른쪽 사이즈 조절
            Mx2 = (1920 - x_mean[idx-1]) - (resized_x - rx_mean)
        else:
            Cx2 = resized_x - ((resized_x - rx_mean) - (1920 - x_mean[idx-1]))

        if y_max[idx-1] > ry_max: # 인물 상단 사이즈 조절
            My1 = y_max[idx-1] - ry_max
        else:
            Cy1 = ry_max - y_max[idx-1]

        if 1080 - y_min[idx-1] > resized_y - ry_min: #인물 하단 사이즈 조절
            My2 = (1080 - y_min[idx-1]) - (resized_y - ry_min)
        else:
            Cy2 = resized_y - ((resized_y - ry_min) - (1080 - y_min[idx-1]))

        #실제 영상 편집 시작
        while(vidcap.isOpened()):
            ret, image = vidcap.read()

            if ret == False:
                break

            curr += 1
            if curr > 20 and curr < (frame_num-20):
                count += 1
                change_value = count/(frame_num-40)

            resized_xC = resized_x + (int)((1920 - resized_x)*change_value)
            resized_yC = resized_y + (int)((1080 - resized_y)*change_value)

            resize = cv2.resize(image, dsize=(resized_xC, resized_yC), interpolation=cv2.INTER_AREA)

            Cx1C = Cx1 + (int)((0 - Cx1)*change_value)
            Cx2C = Cx2 + (int)((1920 -Cx2)*change_value)
            Cy1C = Cy1 + (int)((0 - Cy1)*change_value)
            Cy2C = Cy2 + (int)((1080 - Cy2)*change_value)

            Mx1C = Mx1 + (int)((0 - Mx1)*change_value)
            Mx2C = Mx2 + (int)((0 - Mx2)*change_value)
            My1C = My1 + (int)((0 - My1)*change_value)
            My2C = My2 + (int)((0 - My2)*change_value)

            crop = resize.copy()
            crop = resize[Cy1C:Cy2C-Cy1C, Cx1C:Cx2C-Cx1C]

            margin = cv2.copyMakeBorder(crop, My1C, My2C, Mx1C, Mx2C, cv2.BORDER_CONSTANT, value=[0,0,0])

            final = cv2.resize(margin, dsize=(1920, 1080), interpolation = cv2.INTER_AREA)

            out.write(final)
            #os.remove('vid2_'+str(idx)+'.mp4')

        vidcap.release()
        out.release()
        cv2.destroyAllWindows()

    ## 모든 영상 24 fps로 맞추기

    for idx in range(len(vidlink)):
        os.system("ffmpeg -i 'vid3_%d.mp4' -r 24 -y 'vid4_%d.mp4'" % (idx, idx))
        #os.remove('vid3_'+str(idx)+'.mp4')

    #영상 이어붙이기 (fade in & out 있음)

    import cv2
    from PIL import Image

    target_fps = target_bpm * 24 / 120

    vidcap1 = cv2.VideoCapture('vid4_0.mp4')
    vidcap2 = cv2.VideoCapture('vid4_1.mp4')

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('result.mp4', fourcc, target_fps, (1920, 1080))

    count = 0

    while(vidcap1.isOpened() and vidcap2.isOpened()):
        count += 1

        if count < 560:
            continue
        elif count > 760:
            break;

        else:
            if count < 650:
                ret1, image1 = vidcap1.read()
                out.write(image1)
            elif count <= 670:
                ret1, image1 = vidcap1.read()
                ret2, image2 = vidcap2.read()
                blending = cv2.addWeighted(image1, ((670-count)/20), image2, 1-((670-count)/20), 0)        
                out.write(blending)
            else:
                ret2, image2 = vidcap2.read()
                out.write(image2)

    vidcap1.release()
    vidcap2.release()
    out.release()
