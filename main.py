import vercel_blob
from flask import Flask, request, jsonify
import os
import json
import subprocess
import dotenv
from waitress import serve

app = Flask(__name__)
UPLOAD_DIRECTORY = "OLMT/metdata_tools/site"
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
    script_path = os.path.join(UPLOAD_DIRECTORY, 'data_to_elmbypass.py')
    result = subprocess.run([script_path],
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


if __name__ == '__main__':
    serve(app, listen='*:80')
