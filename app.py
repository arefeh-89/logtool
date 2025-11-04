import os
import re
from datetime import datetime
import tempfile
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename

# ------------------ تنظیم مسیر پوشه‌ی قالب‌ها ------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

app = Flask(__name__, template_folder=TEMPLATES_DIR)

# ------------------ توابع اصلی پردازش ------------------
def save_matching_lines(input_files, search_text):
    all_lines = []
    for input_file in input_files:
        with open(input_file, 'r', encoding='utf-8') as infile:
            for line in infile:
                if search_text in line:
                    all_lines.append(line.rstrip() + '\n')
    return all_lines

def parse_time(value):
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return value

def group_and_sort_logs(lines, key_pattern, output_path):
    key_re = re.compile(rf"{re.escape(key_pattern)}(\d+)\b")
    time_re = re.compile(r'"time":"([\d\-T:\+]+)"')
    groups = {}

    for line in lines:
        key_match = key_re.search(line)
        time_match = time_re.search(line)
        if key_match:
            key_value = key_match.group(1)
            time_value = time_match.group(1) if time_match else "9999-99-99T99:99:99+00:00"
            groups.setdefault(key_value, []).append((parse_time(time_value), line))

    sorted_keys = sorted(groups.keys(), key=lambda x: int(x))

    with open(output_path, 'w', encoding='utf-8') as outfile:
        for i, key in enumerate(sorted_keys):
            sorted_lines = sorted(groups[key], key=lambda x: x[0])
            outfile.writelines([line for _, line in sorted_lines])
            if i < len(sorted_keys) - 1:
                outfile.write('\n')

# ------------------ مسیرها (Routes) ------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_text = request.form['search_text']
        key_pattern = request.form['key_pattern']
        uploaded_files = request.files.getlist('log_files')

        temp_dir = tempfile.mkdtemp()
        file_paths = []

        for f in uploaded_files:
            filename = secure_filename(f.filename)
            file_path = os.path.join(temp_dir, filename)
            f.save(file_path)
            file_paths.append(file_path)

        all_lines = save_matching_lines(file_paths, search_text)
        output_file = os.path.join(temp_dir, "sorted.txt")
        group_and_sort_logs(all_lines, key_pattern, output_file)

        return send_file(output_file, as_attachment=True)

    return render_template('index.html')

# برای تست سریع در Render
@app.route('/ping')
def ping():
    return "pong ✅ Flask is alive!"

# ------------------ اجرای برنامه ------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)