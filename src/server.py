# server.py  (run with:  python server.py)
import threading
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS

# ---- import the helpers you already wrote -----------------
from face_data_collection import FaceDataCollector
from training            import train_model            # <-- your train_model()
from recognizing         import start_recognition      # <-- your start_recognition()

app  = Flask(__name__)
CORS(app)                              # allow requests from http://localhost:3000 etc.
root = Path(__file__).parent           # convenience

# keep one collector instance around so we don’t reopen the webcam each time
collector = FaceDataCollector(
    data_dir = root / "face_data",
    names_path = root / "person_names.json"
)

# --------------------------------------------------------------------------
# 1)  /api/collect-faces   ---------------  triggered by “Collect Faces” btn
# --------------------------------------------------------------------------
@app.route("/api/collect-faces", methods=["POST"])
def api_collect_faces():
    data = request.get_json(force=True)          # force=True → 400 if body missing
    person_id   = data.get("personId")
    person_name = data.get("personName")
    num_images  = int(data.get("numImages", 20))

    if person_id is None or person_name is None:
        return jsonify({"message": "personId and personName are required"}), 400

    # run the long‑running OpenCV capture in a background thread
    threading.Thread(
        target=collector.collect_face_data,
        args=(person_id, person_name, num_images),
        daemon=True
    ).start()

    return jsonify({
        "message": f"Started collecting {num_images} images for {person_name} (ID {person_id})."
    }), 202     # 202 = accepted / processing

# --------------------------------------------------------------------------
# 2)  /api/train-model     ---------------  triggered by “Train Model” btn
# --------------------------------------------------------------------------
@app.route("/api/train-model", methods=["POST"])
def api_train_model():
    # optional request body lets you override defaults if you ever need to
    data        = request.get_json(silent=True) or {}
    epochs      = int(data.get("epochs",      50))
    batch_size  = int(data.get("batchSize",   32))
    dataset_pth = str(data.get("datasetPath", "face_dataset.npz"))
    model_pth   = str(data.get("modelPath",   "face_recognition_model.h5"))

    def train_job():
        _, val_acc = train_model(model_pth, dataset_pth, epochs, batch_size)
        print(f"[TRAIN] finished – best val_acc={val_acc:.4f}")

    threading.Thread(target=train_job, daemon=True).start()
    return jsonify({"message": "Training job started"}), 202

# --------------------------------------------------------------------------
# 3)  /api/start-recognition  -----------  triggered by “Start Recognition” btn
# --------------------------------------------------------------------------
@app.route("/api/start-recognition", methods=["POST"])
def api_start_recognition():
    data          = request.get_json(force=True)
    location_name = data.get("location", "Main Entrance")
    confidence    = float(data.get("confidence", 0.5))
    model_pth     = str(data.get("modelPath", "face_recognition_model.h5"))
    names_pth     = str(data.get("namesPath", "person_names.json"))
    csv_pth       = str(data.get("csvPath",   "recognition_log.csv"))

    if not Path(model_pth).exists():
        return jsonify({"message": f"Model file {model_pth} not found"}), 404

    threading.Thread(
        target=start_recognition,
        kwargs=dict(
            model_path=model_pth,
            names_path=names_pth,
            csv_path=csv_pth,
            location=location_name,
            confidence_threshold=confidence
        ),
        daemon=True
    ).start()

    return jsonify({"message": f"Recognition started at '{location_name}'"}), 202

# --------------------------------------------------------------------------
# health‑check / convenience
# --------------------------------------------------------------------------
@app.route("/api/health", methods=["GET"])
def api_health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    # host='0.0.0.0' so Docker or a phone on the LAN can reach it
    app.run(host="0.0.0.0", port=5000, debug=True)
