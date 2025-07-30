import os

from flask import Flask, request, jsonify

from dataset_sh.multipart.multipart import MultipartFileWriter

app = Flask(__name__)

upload_base = '/tmp/upload-test'
os.makedirs(upload_base, exist_ok=True)


@app.route("/upload/<filename>", methods=['POST'])
def hello_world(filename):
    checksum_value = request.args['checksum_value']
    file_length = int(request.args['file_length'])
    action = request.args['action']
    target_file = os.path.join(upload_base, filename)

    writer = MultipartFileWriter(
        target_file,
        checksum=checksum_value,
        file_length=file_length
    )

    if action == 'init':
        existing = writer.load_existing_progress()
        if existing is None:
            writer.start()
            existing = writer.load_existing_progress()
        return jsonify(existing.model_dump(mode='json'))
    elif action == 'upload':
        part_id = request.args['part_id']
        part_file = writer.part_file(int(part_id))
        with open(part_file, 'wb') as out:
            out.write(request.data)
        return '', 204
    elif action == 'done':
        writer.done()
        return '', 204
    else:
        return '', 400


if __name__ == '__main__':
    app.run(port=9900, debug=True)
