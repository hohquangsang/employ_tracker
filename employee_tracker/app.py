from flask import Flask, render_template, Response, request, redirect, url_for, send_file
from camera import generate_frames, process_video
from database import init_db, get_latest_actions, clear_actions
import os
import json
import config  # import trạng thái video

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    actions = get_latest_actions()
    video_ready = config.CURRENT_VIDEO_PATH is not None and os.path.exists(config.OUTPUT_VIDEO_PATH)
    return render_template('index.html', actions=actions, video_ready=video_ready)

@app.route('/upload', methods=['POST'])
def upload():
    if 'video' not in request.files:
        return "Không có file được gửi", 400
    file = request.files['video']
    if file.filename == '':
        return "Không có tên file", 400

    # Lưu video người dùng upload
    path = os.path.join(app.config['UPLOAD_FOLDER'], 'input.mp4')
    file.save(path)

    # Cập nhật video hiện tại
    config.CURRENT_VIDEO_PATH = path

    # ✅ Xóa lịch sử hành động cũ
    clear_actions()

    # ✅ Xử lý video
    process_video(path, config.OUTPUT_VIDEO_PATH)

    # Sau khi xử lý, reload lại trang index
    return redirect(url_for('index'))

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/output_video')
def output_video():
    return send_file(config.OUTPUT_VIDEO_PATH, as_attachment=False)

@app.route('/download_output')
def download_output():
    return send_file(config.OUTPUT_VIDEO_PATH, as_attachment=True)

@app.route('/save_zones', methods=['POST'])
def save_zones():
    data = request.get_json()
    with open("zones.json", "w") as f:
        json.dump(data, f)
    return "OK"

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
