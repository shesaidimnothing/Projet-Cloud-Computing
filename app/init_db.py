#!/usr/bin/env python3
"""Initialize the database: create all tables and optionally seed sample data."""

import sys
from app import create_app
from models import db, FileRecord
from datetime import datetime, timezone


def init_database(seed=False):
    app = create_app()
    with app.app_context():
        print("[*] Creating all database tables...")
        db.create_all()
        print("[+] Tables created successfully.")

        if seed:
            if FileRecord.query.count() == 0:
                samples = [
                    FileRecord(
                        filename="sample-logo.png",
                        s3_key="images/sample-logo.png",
                        content_type="image/png",
                        size_bytes=2048,
                        category="images",
                        uploaded_at=datetime.now(timezone.utc),
                    ),
                    FileRecord(
                        filename="app.log",
                        s3_key="logs/app.log",
                        content_type="text/plain",
                        size_bytes=512,
                        category="logs",
                        uploaded_at=datetime.now(timezone.utc),
                    ),
                ]
                db.session.add_all(samples)
                db.session.commit()
                print(f"[+] Seeded {len(samples)} sample records.")
            else:
                print("[=] Database already contains records, skipping seed.")

        print("[+] Database initialization complete.")


if __name__ == "__main__":
    seed = "--seed" in sys.argv
    init_database(seed=seed)
