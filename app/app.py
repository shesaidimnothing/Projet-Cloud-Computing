# Application Flask - API pour gérer des fichiers (upload, liste, download, delete)
# Les fichiers sont stockés dans Azure Blob Storage, les infos en base PostgreSQL

from flask import Flask, request, jsonify, Response
from config import Config
from models import db, FileRecord
from storage_service import (
    upload_file_to_blob,
    download_file_from_blob,
    delete_file_from_blob,
    list_blobs,
    list_containers,
)

VALID_CONTAINERS = {"images", "logs", "static"}


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    register_routes(app)
    return app


def register_routes(app):

    @app.route("/")
    def index():
        return jsonify({
            "status": "ok",
            "message": "Flask Cloud App is running (Azure)",
            "endpoints": {
                "health": "GET /health",
                "list_files": "GET /api/files",
                "upload_file": "POST /api/files",
                "get_file_info": "GET /api/files/<id>",
                "download_file": "GET /api/files/<id>/download",
                "update_file": "PUT /api/files/<id>",
                "delete_file": "DELETE /api/files/<id>",
                "list_blobs": "GET /api/storage/list?container=images",
                "list_containers": "GET /api/storage/containers",
            },
        })

    @app.route("/health")
    def health():
        return jsonify({"status": "healthy"})

    # ------------------------------------------------------------------
    # CRUD — File Records + Azure Blob Storage
    # ------------------------------------------------------------------

    @app.route("/api/files", methods=["GET"])
    def list_files():
        category = request.args.get("category")
        query = FileRecord.query
        if category:
            query = query.filter_by(category=category)
        records = query.order_by(FileRecord.uploaded_at.desc()).all()
        return jsonify([r.to_dict() for r in records])

    @app.route("/api/files", methods=["POST"])
    def upload_file():
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        category = request.form.get("category", "static")
        if category not in VALID_CONTAINERS:
            return jsonify({"error": f"Invalid category. Must be one of: {VALID_CONTAINERS}"}), 400

        content_type = file.content_type or "application/octet-stream"

        file.seek(0, 2)
        size = file.tell()
        file.seek(0)

        if not upload_file_to_blob(file, category, file.filename, content_type):
            return jsonify({"error": "Failed to upload to Azure Blob Storage"}), 500

        record = FileRecord(
            filename=file.filename,
            s3_key=f"{category}/{file.filename}",
            content_type=content_type,
            size_bytes=size,
            category=category,
        )
        db.session.add(record)
        db.session.commit()

        return jsonify(record.to_dict()), 201

    @app.route("/api/files/<int:file_id>", methods=["GET"])
    def get_file(file_id):
        record = FileRecord.query.get_or_404(file_id)
        return jsonify(record.to_dict())

    @app.route("/api/files/<int:file_id>/download", methods=["GET"])
    def download_file(file_id):
        record = FileRecord.query.get_or_404(file_id)
        container = record.category
        blob_name = record.filename
        data, content_type = download_file_from_blob(container, blob_name)
        if data is None:
            return jsonify({"error": "File not found in Azure Blob Storage"}), 404
        return Response(
            data,
            mimetype=content_type,
            headers={"Content-Disposition": f"attachment; filename={record.filename}"},
        )

    @app.route("/api/files/<int:file_id>", methods=["PUT"])
    def update_file(file_id):
        record = FileRecord.query.get_or_404(file_id)

        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        content_type = file.content_type or record.content_type

        file.seek(0, 2)
        size = file.tell()
        file.seek(0)

        delete_file_from_blob(record.category, record.filename)

        category = request.form.get("category", record.category)
        if category not in VALID_CONTAINERS:
            return jsonify({"error": f"Invalid category. Must be one of: {VALID_CONTAINERS}"}), 400

        if not upload_file_to_blob(file, category, file.filename, content_type):
            return jsonify({"error": "Failed to upload to Azure Blob Storage"}), 500

        record.filename = file.filename
        record.s3_key = f"{category}/{file.filename}"
        record.content_type = content_type
        record.size_bytes = size
        record.category = category
        db.session.commit()

        return jsonify(record.to_dict())

    @app.route("/api/files/<int:file_id>", methods=["DELETE"])
    def delete_file(file_id):
        record = FileRecord.query.get_or_404(file_id)
        delete_file_from_blob(record.category, record.filename)
        db.session.delete(record)
        db.session.commit()
        return jsonify({"message": f"File '{record.filename}' deleted"}), 200

    # ------------------------------------------------------------------
    # Direct Azure Blob Storage browsing
    # ------------------------------------------------------------------

    @app.route("/api/storage/containers", methods=["GET"])
    def get_containers():
        containers = list_containers()
        return jsonify(containers)

    @app.route("/api/storage/list", methods=["GET"])
    def list_storage():
        container = request.args.get("container", "static")
        prefix = request.args.get("prefix", "")
        blobs = list_blobs(container, prefix)
        return jsonify(blobs)


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
