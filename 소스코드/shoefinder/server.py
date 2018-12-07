from flask import Flask,render_template, redirect,request,url_for,request
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
import heapq
import sys
import subprocess
import os
import re
import json
import requests
import ast

UPLOAD_PATH = 'data/'
DEFAULT_BINARY_OUTPUT_PATH = '/Users/jeongjoonhyun/Desktop/TIMBERLAND_data/TIMBERLAND-batches-bin/test_batch.bin'
RESULT_REPRESENTATION_PATH = 'static/'
RESNET_SCRIPT_PATH = '/Users/jeongjoonhyun/PycharmProjects/models/official/resnet/cifar10_main.py'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])



app = Flask(__name__)
app.config['UPLOAD_PATH'] = UPLOAD_PATH
app.config['DEFAULT_BINARY_OUTPUT_PATH'] = DEFAULT_BINARY_OUTPUT_PATH

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def convert_image_to_binary(input_path, output_path=app.config['DEFAULT_BINARY_OUTPUT_PATH']):
    image = Image.open(input_path)
    image = image.resize((500, 500))
    image = (np.array(image))

    r = image[:, :, 0].flatten()
    g = image[:, :, 1].flatten()
    b = image[:, :, 2].flatten()

    label = [0]
    out = list(label) + list(r) + list(g) + list(b)
    out = np.array(out, np.uint8)
    out.tofile(output_path)

def run_resnet_model(script_path, K=3):
    output = subprocess.check_output(
        [sys.executable, script_path, "--predict"])
    output = output.decode('utf-8')
    # print(output)
    # json_output_string = output.replace("\'", "\"")
    # print(json.loads(json_output_string))
    # predicted_classes = re.findall(r"'classes': (.+?),", output, re.DOTALL)
    probability_of_classes = re.findall(r"'probabilities': array\((.+?), dtype=float32", output, re.DOTALL)
    probability_of_classes = ast.literal_eval(probability_of_classes[0].strip())
    numpy_casted_probability_of_classes = np.array(probability_of_classes)
    top_K_indices = heapq.nlargest(K, range(len(numpy_casted_probability_of_classes)), numpy_casted_probability_of_classes.take)
    top_K_probabilities = [probability_of_classes[idx] for idx in top_K_indices]
    result = {
        "top_K_indices": top_K_indices,
        "top_K_probabilities": top_K_probabilities
    }
    return result

def crawl_with_shoenames(top_K_shoename_list, search_engine_list=['Google']):
    # returns shopping url with top K shoenames.
    # params: top_K_shoename_list ordered by most probable shoename.
    search_url = []
    top_K_shopping_url_list = []
    for engine in search_engine_list:
        if engine == 'Google':
            for shoename in top_K_shoename_list:
                search_url.append("https://www.google.co.kr/search?q="+shoename)
    for url in search_url:
        received = requests.get(url)
        text = received.content
        text = text.decode('euc_kr')

        shopping_url_list = re.findall(r'<h3 class="r"><a href="/url\?q=(.+?)">', text, re.DOTALL)
        top_K_shopping_url_list.append(shopping_url_list[0])

    return top_K_shopping_url_list


def process_result(result):
    top_K_indices = result['top_K_indices']
    # print(top_K_indices)
    representation_imgs = os.listdir(RESULT_REPRESENTATION_PATH)
    if '.DS_Store' in representation_imgs:
        representation_imgs.remove('.DS_Store')
    def is_filename_contain_label(filename, target_label):
        start_index = filename.rfind('_')
        end_index = filename.rfind('.')
        label = int(filename[start_index + 1: end_index]) - 1
        if target_label == label:
            return True

        return False

    def shoename_parse(filename_list):
        return [filename[:filename[:filename.rfind('_')].rfind('_')].replace(RESULT_REPRESENTATION_PATH, "") for filename in filename_list]

    top_K_representation_paths = []

    for idx in top_K_indices:
        for img in representation_imgs:
            if is_filename_contain_label(img, idx):
                top_K_representation_paths.append(os.path.join(RESULT_REPRESENTATION_PATH, img))
                break
    result['top_K_representation_paths'] = top_K_representation_paths
    result['top_K_shoenames'] = shoename_parse(top_K_representation_paths)
    result['top_K_shopping_urls'] = crawl_with_shoenames(result['top_K_shoenames'])

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/upload',methods=['POST'])
def upload():
    if request.method == "POST":
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_PATH'], filename)
            file.save(file_path)
            convert_image_to_binary(file_path)
            result = run_resnet_model(RESNET_SCRIPT_PATH)
            process_result(result)
            # print(result)
            return render_template('show_result.html', enumerate=enumerate, top_K_representation_paths=result['top_K_representation_paths'], top_K_shoenames=result['top_K_shoenames'], top_K_probabilities=[int(prob * 100) for prob in result['top_K_probabilities']], top_K_shopping_urls=result['top_K_shopping_urls'])

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')