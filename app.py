from flask import Flask, render_template, request, send_file
import os
import tempfile

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploaded_files = request.files.getlist("log_files")
        search_select = request.form.get("search_select")
        search_text = request.form.get("search_text")
        key_pattern = request.form.get("key_pattern", "").strip()

        # اگر کاربر گزینه OTHER رو انتخاب کرده بود، از فیلد دستی استفاده می‌کنیم
        search_phrase = search_text if search_select == "OTHER" else search_select

        # مسیر موقت امن برای سرور
        tmp_dir = tempfile.gettempdir()
        output_path = os.path.join(tmp_dir, "processed_logs.txt")

        # پردازش فایل‌ها
        with open(output_path, "w", encoding="utf-8") as out_f:
            for file in uploaded_files:
                for line in file.read().decode("utf-8", errors="ignore").splitlines():
                    if search_phrase in line:
                        out_f.write(line + "\n")

        # برگردوندن فایل برای دانلود
        return send_file(output_path, as_attachment=True, download_name="processed_logs.txt")

    # لیست عبارت‌های پیش‌فرض برای انتخاب
    search_options = ["heraldEventID", "userID", "sessionToken", "errorCode"]

    return render_template("index.html", search_options=search_options)


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # پورت از محیط Render گرفته میشه
    app.run(host="0.0.0.0", port=port)