import os
import shutil
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import re
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Directory paths
input_folder = "/webdav_data/data/htmls"
old_files_folder = "/webdav_data/data/discard"
report_path = "/webdav_data/data/reports"
os.makedirs(old_files_folder, exist_ok=True)
os.makedirs(report_path, exist_ok=True)

# Endpoint to render the web UI
@app.route('/')
def home():
    return render_template('index.html')

# Endpoint to trigger the main script
@app.route('/trigger', methods=['POST'])
def trigger_script():
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
    timestamped_dir = os.path.join(old_files_folder, timestamp)
    os.makedirs(timestamped_dir, exist_ok=True)

    data = []
    for filename in os.listdir(input_folder):
        print(filename)
        file_path = os.path.join(input_folder, filename)
        if os.path.isfile(file_path) and filename.endswith('.html'):
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()

            for item in BeautifulSoup(html_content, 'html.parser').find_all('div', class_='details'):
                SO = 0
                SU = 0
                match1 = re.search(r'<div class="sku"[^>]*>([^<]+)', str(item))
                if match1:
                    sku = match1.group(1)
                else:
                    sku = "unable to find sku"
                    break

                match2 = re.findall(r'<div class="warehouse-value warehouse-in-stock">([^<]+)</div>', str(item))
                if match2:
                    for extracted_text in match2:
                        if extracted_text[:3] == 'Ohi':
                            SO = int(extracted_text.split(':', 1)[1].strip())
                        elif extracted_text[:3] == 'Uta':
                            SU = int(extracted_text.split(':', 1)[1].strip())
                        else:
                            print("*********************Hey, pay attention to this ********************")
                            print(extracted_text)

                print(sku)
                print(SO)
                print(SU)
                To = SO + SU
                if To >= 100:
                    CS = 100
                elif To <= 3:
                    CS = 0
                else:
                    CS = To
                data.append({"SKU": sku, "CS": CS})

            shutil.move(file_path, os.path.join(timestamped_dir, filename))

    if not os.path.exists(report_path):
        os.makedirs(report_path)

    df = pd.DataFrame(data)
    pd.set_option('display.max_columns', None)
    finalFile = os.path.join(report_path, f"inventory_report_{timestamp}.csv")
    df.to_csv(finalFile, index=False)

    return jsonify({"status": "success", "message": f"Report generated: {finalFile}"}), 200

# Endpoint to clear reports directory
@app.route('/clear-reports', methods=['POST'])
def clear_reports():
    for file in os.listdir(report_path):
        file_path = os.path.join(report_path, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
    return jsonify({"status": "success", "message": "Reports directory cleared."}), 200

# Endpoint to clear discard directory
@app.route('/clear-discard', methods=['POST'])
def clear_discard():
    for folder in os.listdir(old_files_folder):
        folder_path = os.path.join(old_files_folder, folder)
        if os.path.isdir(folder_path):
            shutil.rmtree(folder_path)
    return jsonify({"status": "success", "message": "Discard directory cleared."}), 200

# Endpoint to clear htmls directory
@app.route('/clear-htmls', methods=['POST'])
def clear_htmls():
    for file in os.listdir(input_folder):
        file_path = os.path.join(input_folder, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
    return jsonify({"status": "success", "message": "HTMLs directory cleared."}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

