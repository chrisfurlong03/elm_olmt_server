#!/usr/bin/python
import vercel_blob
from flask import Flask, request, jsonify
import os
import json
import subprocess
import dotenv
from waitress import serve

app = Flask(__name__)
UPLOAD_DIRECTORY = "/usr/src/elm_olmt_server/OLMT/metdata_tools/site"
dotenv.load_dotenv()


@app.route('/upload', methods=['POST'])
def upload():
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)

    data = request.json
    json_file_path = os.path.join(
        UPLOAD_DIRECTORY, "processed_ameriflux_data.json")

    # Write JSON data to a file
    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file)

    # Check for the query parameter to set the time_step
    time_step = 48 if request.args.get('aflux') is not None else 24

    # Construct absolute paths
    result = subprocess.run(["python","data_to_elmbypass.py",str(time_step)], shell=True,
                            cwd=UPLOAD_DIRECTORY, capture_output=True, text=True)

    # Check if the script ran successfully
    if result.returncode != 0:
        return jsonify({"error": "Script execution failed", "details": result.stderr}), 500

    # Wait for the file to be created
    output_file_path = os.path.join(
        UPLOAD_DIRECTORY, "1x1pt_MAR-NE/all_hourly.nc")

    if not os.path.exists(output_file_path):
        return jsonify({"error": "Output file not found"}), 500

    print(output_file_path)
    with open(output_file_path, 'rb') as f:
        result = vercel_blob.put(output_file_path, f.read(), {})
    print(result)
    return result

@app.route('/aflux', methods=['GET'])
def aflux():
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)

    os.chdir(UPLOAD_DIRECTORY)

    site = request.args.get("site")
    start_year = request.args.get("start_year")
    end_year = request.args.get("end_year")
    command = [f"Rscript ameriflux_tool.R {str(site)} {str(start_year)} {str(end_year)}"]

    # Run the R script
    result = subprocess.run(command, shell=True, cwd=UPLOAD_DIRECTORY, capture_output=True, text=True)

    if result.returncode != 0:
        return jsonify({"error": "Script execution failed", "details": result.stderr}), 500
    
    data_path = os.path.join(
        UPLOAD_DIRECTORY, "data_to_upload.json")
    
    if not os.path.exists(data_path):
        return jsonify({"error": "Output file not found"}), 500
    
    with open(data_path, 'r') as json_file:
        data = json.load(json_file)
    
    # Return the JSON data as a response
    return jsonify(data)

if __name__ == '__main__':
    serve(app, listen='*:80')
