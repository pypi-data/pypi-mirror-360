import os
import random
from copy import copy
from typing import Tuple, Union

try:
    from typing import Literal
except:
    from typing_extensions import Literal

import cv2
import numpy as np

from simba.third_party_label_appenders.transform.utils import \
    create_yolo_keypoint_yaml
from simba.utils.checks import (check_file_exist_and_readable, check_float,
                                check_if_dir_exists,
                                check_if_keys_exist_in_dict,
                                check_valid_boolean, check_valid_tuple)
from simba.utils.enums import Options
from simba.utils.errors import (FaultyTrainingSetError, InvalidInputError,
                                NoFilesFoundError)
from simba.utils.printing import SimbaTimer, stdout_success
from simba.utils.read_write import (create_directory, get_fn_ext, read_img,
                                    read_json, recursive_file_search)


class COCOKeypoints2Yolo:

    """
    Convert COCO Keypoints version 1.0 data format into a YOLO keypoints training set.

    .. note::
       COCO keypoint files can be created using `https://www.cvat.ai/ <https://www.cvat.ai/>`__.

       This function expects the path to a single  COCO Keypoints version 1.0 file. To merge several before passing the file to thsi function, use
       :func:`simba.third_party_label_appenders.transform.utils.merge_coco_keypoints_files`.

    .. important::
       All image file names have to be unique.

    :param Union[str, os.PathLike] coco_path: Path to coco keypoints 1.0 file in json format.
    :param Union[str, os.PathLike] img_dir: Directory holding img files representing the annotated entries in the ``coco_path``. Will search recursively, so its OK to have images in subdirectories.
    :param Union[str, os.PathLike] save_dir: Directory where to save the yolo formatted data.
    :param Tuple[float, float, float] split: The size of the training set. Value between 0-1.0 representing the percent of training data.
    :param bool verbose: If true, prints progress. Default: True.
    :param Tuple[int, ...] flip_idx: Tuple of ints, representing the flip of body-part coordinates when the animal image flips 180 degrees.
    :return: None

    :example:
    >>> runner = COCOKeypoints2Yolo(coco_path=r"D:\cvat_annotations\frames\coco_keypoints_1\s1\annotations\s1.json", img_dir=r"D:\cvat_annotations\frames\simon", save_dir=r"D:\cvat_annotations\frames\yolo_keypoints", clahe=True)
    >>> runner.run()

    :example II:
    >>> runner = COCOKeypoints2Yolo(coco_path=r"D:\cvat_annotations\frames\coco_keypoints_1\merged.json", img_dir=r"D:\cvat_annotations\frames", save_dir=r"D:\cvat_annotations\frames\yolo", clahe=False)
    >>> runner.run()

     :references:
        .. [1] Helpful YouTube tutorial by Farhan to get YOLO tracking data in animals - `https://www.youtube.com/watch?v=CcGbgFPwQTc <https://www.youtube.com/watch?v=CcGbgFPwQTc>`_.
        .. [2] Great YouTube tutorial by Felipe on annotating data and making data YOLO ready - `https://www.youtube.com/watch?v=m9fH9OWn8YM <https://www.youtube.com/watch?v=m9fH9OWn8YM>`_.
    """

    def __init__(self,
                 coco_path: Union[str, os.PathLike],
                 img_dir: Union[str, os.PathLike],
                 save_dir: Union[str, os.PathLike],
                 train_size: float = 0.7,
                 flip_idx: Tuple[int, ...] = (0, 2, 1, 3, 5, 4, 6, 7, 8),
                 verbose: bool = True,
                 greyscale: bool = False,
                 clahe: bool = False):

        check_file_exist_and_readable(file_path=coco_path)
        check_if_dir_exists(in_dir=save_dir, source=f'{self.__class__.__name__} save_dir')
        check_if_dir_exists(in_dir=img_dir, source=f'{self.__class__.__name__} img_dir')
        check_float(name=f'{self.__class__.__name__} train_size', value=train_size, max_value=0.99, min_value=0.1)
        check_valid_boolean(value=verbose, source=f'{self.__class__.__name__} verbose', raise_error=True)
        check_valid_boolean(value=greyscale, source=f'{self.__class__.__name__} greyscale', raise_error=True)
        check_valid_boolean(value=clahe, source=f'{self.__class__.__name__} clahe', raise_error=True)
        self.train_img_dir, self.val_img_dir = os.path.join(save_dir, 'images', 'train'), os.path.join(save_dir, 'images', 'val')
        self.train_lbl_dir, self.val_lbl_dir = os.path.join(save_dir, 'labels', 'train'), os.path.join(save_dir, 'labels', 'val')
        create_directory(paths=[self.train_img_dir, self.val_img_dir, self.train_lbl_dir, self.val_lbl_dir], overwrite=True)
        self.map_path = os.path.join(save_dir, 'map.yaml')
        self.coco_data = read_json(x=coco_path)
        check_if_keys_exist_in_dict(data=self.coco_data, key=['categories', 'images', 'annotations'], name=coco_path)
        self.map_dict = {i['id']: i['name'] for i in self.coco_data['categories']}
        map_ids = list(self.map_dict.keys())
        if sorted(map_ids) != list(range(len(map_ids))):
            self.map_id_lk = {}  # old: new
            new_map_dict = {}
            for cnt, v in enumerate(sorted(map_ids)):
                self.map_id_lk[v] = cnt
            for k, v in self.map_id_lk.items():
                new_map_dict[v] = self.map_dict[k]
            self.map_dict = copy(new_map_dict)
        else:
            self.map_id_lk = {k: k for k in self.map_dict.keys()}

        self.img_file_paths = recursive_file_search(directory=img_dir, extensions=Options.ALL_IMAGE_FORMAT_OPTIONS.value, case_sensitive=False, substrings=None, as_dict=True, raise_error=True)
        self.img_cnt = len(self.coco_data['images'])
        img_idx = list(range(len(self.coco_data['images']) + 1))
        self.train_idx = random.sample(img_idx, int(self.img_cnt * train_size))
        check_valid_tuple(x=flip_idx, source=self.__class__.__name__, valid_dtypes=(int,), minimum_length=1)
        self.verbose, self.coco_path, self.img_dir, self.coco_path, self.flip_idx = verbose, coco_path, img_dir, coco_path, flip_idx
        self.save_dir, self.greyscale, self.clahe = save_dir, greyscale, clahe

    def run(self):
        shapes, timer = [], SimbaTimer(start=True)
        for cnt in range(len(self.coco_data['images'])):
            img_data = self.coco_data['images'][cnt]
            check_if_keys_exist_in_dict(data=img_data, key=['width', 'height', 'file_name', 'id'], name=self.coco_path)
            _, img_name, ext = get_fn_ext(filepath=img_data['file_name'])
            if self.verbose:
                print(f'Processing annotation {cnt + 1}/{self.img_cnt} from COCO to YOLO ({img_name})...')
            if not img_name in self.img_file_paths.keys():
                raise NoFilesFoundError(msg=f'The file {img_name} could not be found in the {self.img_dir} directory', source=self.__class__.__name__)
            img = read_img(img_path=self.img_file_paths[img_name], greyscale=self.greyscale, clahe=self.clahe)
            if (img.shape[0] != img_data['height']) or (img.shape[1] != img_data['width']):
                raise FaultyTrainingSetError(msg=f'Image {img_name} is of shape {img.shape[0]}x{img.shape[1]}, but the coco data has been annotated on an image of {img_data["height"]}x{img_data["width"]}.')
            img_annotations = [x for x in self.coco_data['annotations'] if x['image_id'] == img_data['id']]
            roi_str = ''
            if cnt in self.train_idx:
                label_save_path, img_save_path = os.path.join(self.train_lbl_dir, f'{img_name}.txt'), os.path.join(self.train_img_dir, f'{img_name}.png')
            else:
                label_save_path, img_save_path = os.path.join(self.val_lbl_dir, f'{img_name}.txt'), os.path.join(self.val_img_dir, f'{img_name}.png')
            for img_annotation in img_annotations:
                check_if_keys_exist_in_dict(data=img_annotation, key=['bbox', 'keypoints', 'id', 'image_id', 'category_id'], name=self.coco_path)
                x1, y1 = img_annotation['bbox'][0], img_annotation['bbox'][1]
                w, h = img_annotation['bbox'][2], img_annotation['bbox'][3]
                x_center = np.clip((x1 + (w / 2)) / img_data['width'], 0, 1)
                y_center = np.clip((y1 + (h / 2)) / img_data['height'], 0, 1)
                w = np.clip(w / img_data['width'], 0, 1)
                h = np.clip(h / img_data['height'], 0, 1)
                roi_str += ' '.join([f"{self.map_id_lk[img_annotation['category_id']]}", str(x_center), str(y_center), str(w), str(h), ' '])
                kps = np.array(img_annotation['keypoints']).reshape(-1, 3).astype(np.int32)
                x, y, v = kps[:, 0], kps[:, 1], kps[:, 2]
                x = np.clip(x / img_data['width'], 0, 1)
                y = np.clip(y / img_data['height'], 0, 1)
                shapes.append(x.shape[0])
                kps = list(np.column_stack((x, y, v)).flatten())
                roi_str += ' '.join(str(x) for x in kps) + '\n'

            with open(label_save_path, mode='wt', encoding='utf-8') as f:
                f.write(roi_str)
            cv2.imwrite(img_save_path, img)
        if len(list(set(shapes))) > 1:
            raise InvalidInputError(
                msg=f'The annotation data {self.coco_path} contains more than one keypoint shapes: {set(shapes)}', source=self.__class__.__name__)
        if len(self.flip_idx) != shapes[0]:
            raise InvalidInputError(msg=f'flip_idx contains {len(self.flip_idx)} values but {shapes[0]} keypoints detected per image in coco data.', source=self.__class__.__name__)
        missing = [x for x in self.flip_idx if x not in list(range(shapes[0]))]
        if len(missing) > 0:
            raise InvalidInputError(msg=f'flip_idx contains index values not in keypoints ({missing}).', source=self.__class__.__name__)
        missing = [x for x in list(range(shapes[0])) if x not in self.flip_idx]
        if len(missing) > 0:
            raise InvalidInputError(msg=f'keypoints contains index values not in flip_idx ({missing}).', source=self.__class__.__name__)

        create_yolo_keypoint_yaml(path=self.save_dir, train_path=self.train_img_dir, val_path=self.val_img_dir, names=self.map_dict, save_path=self.map_path, kpt_shape=(int(shapes[0]), 3), flip_idx=self.flip_idx)
        timer.stop_timer()
        if self.verbose: stdout_success(msg=f'COCO keypoints to YOLO conversion complete. Data saved in directory {self.save_dir}.', elapsed_time=timer.elapsed_time_str)



# runner = COCOKeypoints2Yolo(coco_path=r"D:\cvat_annotations\frames\coco_keypoints_1\merged\merged_07032025.json",
#                             img_dir=r"D:\cvat_annotations\frames",
#                             save_dir=r"D:\cvat_annotations\yolo_07032025",
#                             clahe=False)
# runner.run()


# runner = COCOKeypoints2Yolo(coco_path=r"D:\cvat_annotations\frames\coco_keypoints_1\s1\annotations\s1.json", img_dir=r"D:\cvat_annotations\frames\simon", save_dir=r"D:\cvat_annotations\frames\yolo_keypoints", clahe=True)
# runner.run()