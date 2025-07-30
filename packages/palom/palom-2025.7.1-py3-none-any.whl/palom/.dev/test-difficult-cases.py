import palom
import cv2
from palom import img_util
import numpy as np
from palom import register_util
import matplotlib.pyplot as plt

r1 = palom.reader.OmePyramidReader(
    "difficult/LSP14383/22199$LSP14383$HE$HE$OR$001 _121041.tiff"
)
r2 = palom.reader.OmePyramidReader(
    "difficult/LSP14383/LSP14383_P54_A31_C100_HMS_Orion7@20221201_025039_540685-zlib.ome.tiff"
)


palom.register.feature_based_registration(
    palom.img_util.cv2_downscale_local_mean(r1.pyramid[1][0], 1),
    palom.img_util.cv2_downscale_local_mean(r2.pyramid[0][1], 1),
    plot_match_result=True,
    n_keypoints=20_000,
    test_flip=True,
    test_intensity_invert=True,
    auto_mask=False,
)

def cv2_feature_detect_and_match(
    img_left, img_right, n_keypoints=1000,
    plot_keypoint_result=False, plot_match_result=False
):
    
    img_left, img_right = [
        img_util.cv2_to_uint8(i)
        for i in (img_left, img_right)
    ]
    descriptor_extractor = cv2.ORB_create(n_keypoints, edgeThreshold=0)

    keypoints_left, descriptors_left = descriptor_extractor.detectAndCompute(
        np.dstack(3*(img_left,)), None
    )
    keypoints_right, descriptors_right = descriptor_extractor.detectAndCompute(
        np.dstack(3*(img_right,)), None
    )
    if plot_keypoint_result:
        register_util.plot_img_keypoints(
            [img_left, img_right], [keypoints_left, keypoints_right]
        )
    # logger.debug(f"keypts L:{len(keypoints_left)}, keypts R:{len(keypoints_right)}")
    if len(keypoints_left) == 0 or len(keypoints_right) == 0:
        return np.empty((1, 2)), np.empty((1, 2))

    bf_matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf_matcher.match(descriptors_left, descriptors_right)

    src_pts = np.float32(
        [keypoints_left[m.queryIdx].pt for m in matches]
    )
    dst_pts = np.float32(
        [keypoints_right[m.trainIdx].pt for m in matches]
    )
    t_matrix, mask = cv2.estimateAffine2D(
        dst_pts, src_pts,
        method=cv2.RANSAC, ransacReprojThreshold=30, maxIters=5000
    )
    if plot_match_result:
        plt.figure()
        imgmatch_ransac = cv2.drawMatches(
            img_left, keypoints_left,
            img_right, keypoints_right,
            matches, None,
            matchColor=(0, 255, 0), singlePointColor=None,
            matchesMask=mask.flatten(),
            flags=cv2.DRAW_MATCHES_FLAGS_DEFAULT
        )
        plt.gca().imshow(imgmatch_ransac)
    return src_pts[mask.flatten()>0], dst_pts[mask.flatten()>0]