import vercel_blob
from flask import Flask, request, jsonify, send_file, render_template, redirect
import os
import json
import subprocess
import dotenv

app = Flask(__name__)
UPLOAD_DIRECTORY = "/project/workspace/OLMT/metdata_tools/site"
dotenv.load_dotenv()


@app.route('/upload', methods=['POST'])
def upload():
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)

    data = request.json
    json_file_path = os.path.join(
        UPLOAD_DIRECTORY, 'processed_ameriflux_data.json')

    # Write JSON data to a file
    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file)

    # Construct absolute paths
    venv_python = os.path.join("/OLMT/metdata_tools/site", 'bin', 'python')
    script_path = os.path.join(UPLOAD_DIRECTORY, 'data_to_elmbypass.py')
    result = subprocess.run([venv_python, script_path],
                            cwd=UPLOAD_DIRECTORY, capture_output=True, text=True)

    # Check if the script ran successfully
    if result.returncode != 0:
        return jsonify({"error": "Script execution failed", "details": result.stderr}), 500

    # Wait for the file to be created
    output_file_path = os.path.join(
        UPLOAD_DIRECTORY, '1x1pt_MAR-NE/all_hourly.nc')

    if not os.path.exists(output_file_path):
        return jsonify({"error": "Output file not found"}), 500

    print(output_file_path)
    with open(output_file_path, 'rb') as f:
        result = vercel_blob.put(output_file_path, f.read(), {})
    print(result)
    return result


@app.route('/upload-json', methods=['POST'])
def upload_json():
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)

    data = request.json
    json_file_path = os.path.join(
        UPLOAD_DIRECTORY, 'processed_ameriflux_data.json')

    # Write JSON data to a file
    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file)

    # Construct absolute paths
    venv_python = os.path.join("/OLMT/metdata_tools/site", 'bin', 'python')
    script_path = os.path.join(UPLOAD_DIRECTORY, 'data_to_elmbypass.py')
    result = subprocess.run([venv_python, script_path],
                            cwd=UPLOAD_DIRECTORY, capture_output=True, text=True)

    # Check if the script ran successfully
    if result.returncode != 0:
        return jsonify({"error": "Script execution failed", "details": result.stderr}), 500

    # Wait for the file to be created
    output_file_path = os.path.join(
        UPLOAD_DIRECTORY, '1x1pt_MAR-NE/all_hourly.nc')

    if not os.path.exists(output_file_path):
        return jsonify({"error": "Output file not found"}), 500

    # Send the file as a response
    return send_file(output_file_path, mimetype='application/x-netcdf', as_attachment=True, download_name='all_hourly.nc')


if __name__ == '__main__':
    app.run(debug=True)
