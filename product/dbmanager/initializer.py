from product.utils.reader import CsvReader
from product.models import *
import cv2


class Initializer:
    start_dict = {}
    end_dict = {}
    start_idx = 0
    data_n = 312
    end_idx = data_n
    csv_reader = CsvReader()

    @staticmethod
    def product_csv_extractor(file="/home/jihee/choleor_media/choreo/choreo_data.csv"):
        Initializer.start_dict = Initializer.csv_reader.read(file,
                                                             **{'col1': 'start_pose_id',
                                                                'col2': 'start_pose_type',
                                                                'col3': 'frame',
                                                                'col4': 'start_x_mean',
                                                                'col5': 'start_y_min',
                                                                'col6': 'start_y_max'})  # 리스트를 value로 갖는 dictionary
        Initializer.end_dict = Initializer.csv_reader.read(file, **{'col1': 'end_pose_id',
                                                                    'col2': 'end_pose_type',
                                                                    'col3': 'frame',
                                                                    'col4': 'end_x_mean',
                                                                    'col5': 'end_y_min',
                                                                    'col6': 'end_y_max'})
        key = None
        val = None
        Initializer.start_dict['s_frame'] = []
        Initializer.start_dict['e_frame'] = []
        Initializer.end_dict['s_frame'] = []
        Initializer.end_dict['e_frame'] = []

        total = []

        for dic in [Initializer.start_dict, Initializer.end_dict]:
            for idx in range(312):
                dic['s_frame'] += [list(map(lambda x: int(x), dic['frame'][idx].split("~")))[0]]
                dic['e_frame'] += [list(map(lambda x: int(x), dic['frame'][idx].split("~")))[1]]
            total.append([dic['s_frame']])
            total.append([dic['e_frame']])

            for key, val in dic.items():
                if key not in ["frame", "s_frame", "e_frame", "start_pose_id", "end_pose_id"]:
                    total.append(list(map(lambda x: 0 if x is "" else int(x), val)))

        Initializer.start_dict['s_frame'], Initializer.end_dict['s_frame'] = total[0] * 2
        Initializer.start_dict['e_frame'], Initializer.end_dict['e_frame'] = total[1] * 2
        Initializer.start_dict['start_pose_type'], Initializer.end_dict['end_pose_type'] = total[2], total[8]
        Initializer.start_dict['start_x_mean'], Initializer.end_dict['end_x_mean'] = total[3], total[9]
        Initializer.start_dict['start_y_min'], Initializer.end_dict['end_y_min'] = total[4], total[10]
        Initializer.start_dict['start_y_max'], Initializer.end_dict['end_y_max'] = total[5], total[11]

        for i, v in enumerate(total):
            print(i, v)
        for k, i in Initializer.start_dict.items():
            print("============key=============")
            print(k)
            print("===========value============")
            print(i)

        print("--------------------------------------------------------------")

        for k, i in Initializer.end_dict.items():
            print("============key=============")
            print(k)
            print("===========value============")
            print(i)

    @staticmethod
    def set_data_range(start, end):
        Initializer.start_idx = start
        Initializer.end_idx = end

    @staticmethod
    def insert_db():
        for i in range(Initializer.start_idx, Initializer.end_idx):
            StartPose(start_pose_id=Initializer.start_dict['start_pose_id'][i],
                      type=Initializer.start_dict['start_pose_type'][i],
                      s_frame=Initializer.start_dict['s_frame'][i],
                      e_frame=Initializer.start_dict['e_frame'][i],
                      x_mean=Initializer.start_dict['start_x_mean'][i],
                      y_min=Initializer.start_dict['start_y_min'][i],
                      y_max=Initializer.start_dict['start_y_max'][i]).save()
            EndPose(end_pose_id=Initializer.end_dict['end_pose_id'][i],
                    type=Initializer.end_dict['end_pose_type'][i],
                    s_frame=Initializer.end_dict['s_frame'][i],
                    e_frame=Initializer.end_dict['e_frame'][i],
                    x_mean=Initializer.end_dict['end_x_mean'][i],
                    y_min=Initializer.end_dict['end_y_min'][i],
                    y_max=Initializer.end_dict['end_y_max'][i]).save()

    @staticmethod
    def initialize():
        Initializer.product_csv_extractor()
        # Initializer.set_data_range()
        Initializer.insert_db()

    @staticmethod
    def make_thumbnail(path, cslice_ids):
        vidlink = []
        cids = []

        for csid in cslice_ids:
            cids += [csid.split("~")[0]]
            vidlink.append(
                '{}/{}.mp4'.format(path, csid))

        # 24fps로 변환
        for idx in range(len(vidlink)):
            vidcap = cv2.VideoCapture(
                f'/home/jihee/choleor_media/choreo/SLICE/{cids[idx]}/{cslice_ids[idx]}.mp4')
            count = 0

            while vidcap.isOpened():
                count += 1

                ret, image = vidcap.read()
                if ret is False:
                    break
                if count <= 10:
                    continue

                cv2.imwrite('썸네일 저장할 경로', image)
                break

            vidcap.release()

if __name__ == '__main__':
    # Initializer.initialize()
    choreo_slice_id = "yNM2DU3fkgE~5"
    choreo_obj = StartPose.objects.get(start_pose_id="s_" + choreo_slice_id)
    print(choreo_obj.s_frame)
