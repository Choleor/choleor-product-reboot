import argparse
import logging
import sys
import time

from tf_pose import common
import cv2
import numpy as np
from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh

import csv

logger = logging.getLogger('TfPoseEstimatorRun')
logger.handlers.clear()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='tf-pose-estimation run')
    parser.add_argument('--image', type=str, default='./images/p1.jpg')
    parser.add_argument('--model', type=str, default='cmu',
                        help='cmu / mobilenet_thin / mobilenet_v2_large / mobilenet_v2_small')
    parser.add_argument('--resize', type=str, default='0x0',
                        help='if provided, resize images before they are processed. '
                             'default=0x0, Recommends : 432x368 or 656x368 or 1312x736 ')
    parser.add_argument('--resize_out_ratio', type=float, default=4.0,
                        help='if provided, resize heatmaps before they are post-processed. default=1.0')
    parser.add_argument('--human_num', type=int, default=1, help='only one person who have human_num will detected')

    args = parser.parse_args()

    w, h = model_wh(args.resize)
    if w == 0 or h == 0:
        e = TfPoseEstimator(get_graph_path(args.model), target_size=(432, 368))
    else:
        e = TfPoseEstimator(get_graph_path(args.model), target_size=(w, h))

    # estimate human poses from a single image !
    image = common.read_imgfile(args.image, None, None)
    if image is None:
        logger.error('Image can not be read, path=%s' % args.image)
        sys.exit(-1)

    t = time.time()
    humans = e.inference(image, resize_to_default=(w > 0 and h > 0), upsample_size=args.resize_out_ratio)

    # print detected keypoint coordinates

    image_h, image_w = image.shape[:2]
    key_point = [0] * 2

    x_sum = 0
    x_count = 0
    x_mean = [0.0]
    y_min = [image_h]
    y_max = [0]
    human_num = args.human_num
    hn = 0

    with open('key_point_coordinates.csv', 'w', newline='') as f:
        makewrite = csv.writer(f)
        for human in humans:
            hn += 1
            if hn != human_num:  # 여기서 사람 위치 수정!
                continue
            for i in range(common.CocoPart.Background.value):
                if i not in human.body_parts.keys():
                    key_point[0] = 0  # int(0.5 * image_w + 0.5)
                    key_point[1] = 0  # int(0.5 * image_h + 0.5)
                    makewrite.writerow(key_point)
                    continue

                body_part = human.body_parts[i]

                key_point[0] = int(body_part.x * image_w + 0.5)
                key_point[1] = int(body_part.y * image_h + 0.5)

                x_sum += key_point[0]
                x_count += 1
                y_min[0] = min(y_min[0], key_point[1])
                y_max[0] = max(y_max[0], key_point[1])

                makewrite.writerow(key_point)

        x_mean[0] = int(x_sum / x_count)
        makewrite.writerow(x_mean)
        makewrite.writerow(y_min)
        makewrite.writerow(y_max)

    elapsed = time.time() - t

    logger.info('inference image: %s in %.4f seconds.' % (args.image, elapsed))

    image = TfPoseEstimator.draw_humans(image, humans, human_num, imgcopy=False)

    try:
        import matplotlib.pyplot as plt

        fig = plt.figure()
        a = fig.add_subplot(2, 2, 1)
        a.set_title('Result')
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        cv2.imwrite('result.jpg', image)

        bgimg = cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_BGR2RGB)
        bgimg = cv2.resize(bgimg, (e.heatMat.shape[1], e.heatMat.shape[0]), interpolation=cv2.INTER_AREA)

        # show network output
        a = fig.add_subplot(2, 2, 2)
        plt.imshow(bgimg, alpha=0.5)
        tmp = np.amax(e.heatMat[:, :, :-1], axis=2)
        plt.imshow(tmp, cmap=plt.cm.gray, alpha=0.5)
        plt.colorbar()

        tmp2 = e.pafMat.transpose((2, 0, 1))
        tmp2_odd = np.amax(np.absolute(tmp2[::2, :, :]), axis=0)
        tmp2_even = np.amax(np.absolute(tmp2[1::2, :, :]), axis=0)

        a = fig.add_subplot(2, 2, 3)
        a.set_title('Vectormap-x')
        # plt.imshow(CocoPose.get_bgimg(inp, target_size=(vectmap.shape[1], vectmap.shape[0])), alpha=0.5)
        plt.imshow(tmp2_odd, cmap=plt.cm.gray, alpha=0.5)
        plt.colorbar()

        a = fig.add_subplot(2, 2, 4)
        a.set_title('Vectormap-y')
        # plt.imshow(CocoPose.get_bgimg(inp, target_size=(vectmap.shape[1], vectmap.shape[0])), alpha=0.5)
        plt.imshow(tmp2_even, cmap=plt.cm.gray, alpha=0.5)
        plt.colorbar()
        plt.show()
    except Exception as e:
        logger.warning('matplitlib error, %s' % e)
        cv2.imshow('result', image)
        cv2.waitKey()
