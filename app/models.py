from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class FileRecord(db.Model):
    """Tracks files uploaded to S3 with metadata."""

    __tablename__ = "file_records"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    s3_key = db.Column(db.String(512), nullable=False, unique=True)
    content_type = db.Column(db.String(128), default="application/octet-stream")
    size_bytes = db.Column(db.Integer, default=0)
    category = db.Column(db.String(64), default="static")  # images, logs, static
    uploaded_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "s3_key": self.s3_key,
            "content_type": self.content_type,
            "size_bytes": self.size_bytes,
            "category": self.category,
            "uploaded_at": self.uploaded_at.isoformat(),
        }
