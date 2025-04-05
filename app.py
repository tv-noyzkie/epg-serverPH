from flask import Flask, send_file
import os
import subprocess

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ EPG Server is Running!"

@app.route("/epg.xml")
def serve_epg():
    file_path = os.path.abspath("epg.xml")

    # ❌ Delete the old EPG file to force regeneration
    if os.path.exists(file_path):
        os.remove(file_path)
        print("🗑️ Deleted old epg.xml")

    # 🔄 Regenerate the EPG file using the script
    print("⚙️ Running epg_script.py to generate a new epg.xml...")
    subprocess.run(["python", "epg_script.py"])

    # ✅ Check if the new file exists
    if not os.path.exists(file_path):
        return "❌ Error: epg.xml was not generated!", 500

    # 📂 Log file size before serving
    file_size = os.path.getsize(file_path)
    print(f"📂 Serving epg.xml - Size: {file_size} bytes")

    return send_file(file_path, mimetype="application/xml")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
