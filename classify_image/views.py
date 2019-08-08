import io
import os

from base64 import b64decode
import numpy as np
import tensorflow as tf
from PIL import Image
from django.core.files.temp import NamedTemporaryFile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import matplotlib.pyplot as plt
import matplotlib.patches as patches


LOWER_THRESHOLD = 0.35
UPPER_THRESHOLD = 0.80

TF_GRAPH = "{base_path}/megadetector/megadetector_v3.pb".format(
    base_path=os.path.abspath(os.path.dirname(__file__)))
TF_LABELS = "{base_path}/megadetector/labels.txt".format(
    base_path=os.path.abspath(os.path.dirname(__file__)))


def load_graph():
    sess = tf.Session()
    with tf.gfile.FastGFile(TF_GRAPH, 'rb') as tf_graph:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(tf_graph.read())
        tf.import_graph_def(graph_def, name='')
    label_lines = [line.rstrip() for line in tf.gfile.GFile(TF_LABELS)]

    input_tensor = sess.graph.get_tensor_by_name('image_tensor:0')
    box_tensor = sess.graph.get_tensor_by_name('detection_boxes:0')
    score_tensor = sess.graph.get_tensor_by_name('detection_scores:0')
    class_tensor = sess.graph.get_tensor_by_name('detection_classes:0')
    output_tensors = [box_tensor, score_tensor, class_tensor]
    return sess, input_tensor, output_tensors, label_lines


SESS, INPUT_TENSOR, OUTPUT_TENSORS, LABELS = load_graph()


@csrf_exempt
def classify_api(request):
    data = {"success": False}

    if request.method == "POST":
        tmp_f = NamedTemporaryFile()

        if request.FILES.get("image", None) is not None:
            image_request = request.FILES["image"]
            image_bytes = image_request.read()
            image = Image.open(io.BytesIO(image_bytes))
            image.save(tmp_f, image.format)
        elif request.POST.get("image64", None) is not None:
            base64_data = request.POST.get("image64", None).split(',', 1)[1]
            plain_data = b64decode(base64_data)
            tmp_f.write(plain_data)

        classify_result = tf_classify(tmp_f)
        tmp_f.close()

        if classify_result:
            data["success"] = True
            data["confidence"] = {}
            for res in classify_result:
                data["confidence"][res[0]] = float(res[1])

    return JsonResponse(data)


def classify(request):
    return render(request, 'classify.html', {})


# noinspection PyUnresolvedReferences
def tf_classify(image_file):
    width, height = 1920, 1920 * 0.75
    predictions = []

    image = Image.open(image_file.name).convert("RGB")
    image = image.resize((width, int(height)))
    image = np.expand_dims(image, axis=0)

    boxes, scores, classes = SESS.run(OUTPUT_TENSORS, {INPUT_TENSOR: image})

    above_threshold = scores > LOWER_THRESHOLD
    boxes_above_threshold = boxes[above_threshold]
    classes_above_threshold = classes[above_threshold]
    scores_above_threshold = scores[above_threshold]

    is_animal = np.sum(classes_above_threshold == 1) > 0
    max_score = np.max(scores_above_threshold)
    predictions.append([LABELS[int(is_animal)], max_score])

    fig, ax = plt.subplots(1)
    ax.imshow(image.squeeze())
    for box, cls in zip(boxes_above_threshold, classes_above_threshold):
        ymin, xmin, ymax, xmax = box
        x = xmin * width
        y = ymin * height
        w = (xmax - xmin) * width
        h = (ymax - ymin) * height
        edgecolor = 'g' if cls == 1 else 'r'
        rect = patches.Rectangle((x, y), w, h, linewidth=5,
                                 edgecolor=edgecolor, facecolor='none')
        ax.add_patch(rect)

    plt.axis('off')
    plt.savefig('tmp', dpi=100, transparent=True, optimize=True, quality=90)
    return predictions
