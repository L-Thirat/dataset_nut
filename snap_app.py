import pathlib
import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile

from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image

from object_detection.utils import ops as utils_ops
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
import time

# import cv2


# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = 'trained_pb/ssd_mobilenetv2' + '/frozen_inference_graph.pb'

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = 'data/object-detection.pbtxt'

NUM_CLASSES = 4

detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

# ## Loading label map
# Label maps map indices to category names, so that when our convolution network predicts `5`, we know that this corresponds to `airplane`.  Here we use internal utility functions, but anything that returns a dictionary mapping integers to appropriate string labels would be fine

# In[7]:


label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES,
                                                            use_display_name=True)
category_index = label_map_util.create_category_index(categories)


# ## Helper code

# In[8]:


def load_image_into_numpy_array(image):
    # BW -> RGB
    last_axis = -1
    image = np.expand_dims(image, last_axis)
    dim_to_repeat = 2
    repeats = 3
    image = np.repeat(image, repeats, dim_to_repeat)
    return image

    # (im_width, im_height) = image.size
    # return np.array(image.getdata()).reshape(
    #     (im_height, im_width, 3)).astype(np.uint8)


# # Detection

# In[9]:


# For the sake of simplicity we will use only 2 images:
# image1.jpg
# image2.jpg
# If you want to test the code with your images, just add path to the images to the TEST_IMAGE_PATHS.
PATH_TO_TEST_IMAGES_DIR = 'images/test/'
TEST_IMAGE_PATHS = []
for filename in os.listdir(PATH_TO_TEST_IMAGES_DIR):
    if filename.endswith(".jpg"):
        TEST_IMAGE_PATHS.append(PATH_TO_TEST_IMAGES_DIR + filename)

# Size, in inches, of the output images.
IMAGE_SIZE = (12, 8)

with detection_graph.as_default():
    with tf.Session(graph=detection_graph) as sess:
        for i, image_path in enumerate(TEST_IMAGE_PATHS):
            try:
                start_t = time.time()
                image = Image.open(image_path)
                # the array based representation of the image will be used later in order to prepare the
                # result image with boxes and labels on it.
                image_np = load_image_into_numpy_array(image)
                # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
                image_np_expanded = np.expand_dims(image_np, axis=0)
                image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
                # Each box represents a part of the image where a particular object was detected.
                boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
                # Each score represent how level of confidence for each of the objects.
                # Score is shown on the result image, together with the class label.
                scores = detection_graph.get_tensor_by_name('detection_scores:0')
                classes = detection_graph.get_tensor_by_name('detection_classes:0')
                num_detections = detection_graph.get_tensor_by_name('num_detections:0')
                # Actual detection.
                (boxes, scores, classes, num_detections) = sess.run(
                    [boxes, scores, classes, num_detections],
                    feed_dict={image_tensor: image_np_expanded})
                # Visualization of the results of a detection.
                image_np = vis_util.visualize_boxes_and_labels_on_image_array(
                    image_np,
                    boxes=np.squeeze(boxes),
                    classes=np.squeeze(classes).astype(np.int32),
                    scores=np.squeeze(scores),
                    category_index=category_index,
                    use_normalized_coordinates=True,
                    line_thickness=8,
                    min_score_thresh=0.01)
                plt.figure(figsize=IMAGE_SIZE)
                plt.imshow(image_np)
                plt.imsave('%dimage.png' % i, image_np)
                # plt.figure(figsize=IMAGE_SIZE)
                # plt.imshow(image_np)
                # plt.imsave('/root/models/0image.png',image_np )
                end_t = time.time()
                print("Usage = ", end_t - start_t)
            except Exception as e:
                print(e)
                break
