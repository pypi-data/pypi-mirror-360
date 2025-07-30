# mask to polygon
import json

import cv2
import numpy as np
import scipy.spatial
import shapely
import tifffile
import tqdm
import uuid

mask = tifffile.imread(
    r"Z:\yc296\computation\YC-20250105-mcmicro-issue-568-s3seg\mcmicro\mcmicro-issue-568-crop2\segmentation\crop2\nucleiRing.ome.tif"
)


def shapely_polygons_to_mask(polygons, mask_shape=None, fill_value_min=None):
    coords = [np.array(pp.exterior.coords) for pp in polygons]

    if mask_shape is None:
        mask_shape = np.ceil(np.vstack(coords).max(axis=0)).astype("int")[::-1]
    h, w = mask_shape

    if fill_value_min is None:
        fill_value_min = 1
    fill_value = int(fill_value_min)

    mask = np.zeros((int(h), int(w)), np.uint8)
    for pp in coords:
        cv2.fillPoly(mask, [pp.round().astype("int")], fill_value)
        fill_value += 1
    return mask


def mask_to_polygons(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    polygons = [shapely.Polygon(np.reshape(cc, (-1, 2))) for cc in contours]
    centroids = np.array([np.array(pp.centroid.coords).flatten() for pp in polygons])

    tree = scipy.spatial.cKDTree(centroids)

    pairs = np.unique(
        np.sort(tree.query(centroids, k=2, distance_upper_bound=3)[1]), axis=0
    )

    filtered = []
    for p1, p2 in tqdm.tqdm(pairs):
        if p2 == tree.n:
            filtered.append(polygons[p1])
            continue
        p1, p2 = polygons[p1], polygons[p2]
        if p1.contains(p2):
            filtered.append(p1)
        elif p2.contains(p1):
            filtered.append(p2)
        else:
            filtered.extend([p1, p2])
    return filtered


def mask_to_qupath(mask):
    h, w = mask.shape
    polygons = shapely.to_geojson(mask_to_polygons(mask))
    out = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": str(uuid.uuid4()),
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[0, 0], [w, 0], [w, h], [0, h], [0, 0]]],
                },
                "properties": {"objectType": "annotation", "isLocked": True},
            }
        ],
    }
    for pp in polygons:
        out["features"].append(
            {
                "type": "Feature",
                "id": str(uuid.uuid4()),
                "geometry": json.loads(pp),
                "properties": {"objectType": "detection"},
            }
        )
    return out


with open(
    r"Z:\yc296\computation\YC-20250105-mcmicro-issue-568-s3seg\mcmicro\mcmicro-issue-568-crop2\segmentation\crop2\nucleiRing.ome.tif.geojson",
    "w",
) as f:
    json.dump(mask_to_qupath(mask), f)
