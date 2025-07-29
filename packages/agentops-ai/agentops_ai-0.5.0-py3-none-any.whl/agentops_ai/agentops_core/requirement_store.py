"""Requirement store module for AgentOps.

Implements SQLite-based storage for requirements.
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class Requirement:
    """Represents a stored functional requirement."""

    id: Optional[int]
    requirement_text: str
    file_path: str
    code_symbol: str
    commit_hash: Optional[str]
    confidence: float
    status: str  # 'approved', 'pending', 'rejected'
    created_at: str
    metadata: Dict[str, Any]


class RequirementStore:
    """SQLite-based storage for functional requirements."""

    def __init__(self, db_path: str = ".agentops/requirements.db"):
        """Initialize the requirement store.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_database()

    def _ensure_db_directory(self):
        """Ensure the .agentops directory exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

    def _init_database(self):
        """Initialize the SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS requirements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    requirement_text TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    code_symbol TEXT NOT NULL,
                    commit_hash TEXT,
                    confidence REAL NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    metadata TEXT,
                    UNIQUE(file_path, code_symbol, requirement_text)
                )
            """
            )

            # Index for faster lookups
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_file_path 
                ON requirements(file_path)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_status 
                ON requirements(status)
            """
            )

            conn.commit()

    def store_requirement(self, requirement: Requirement) -> int:
        """Store a new requirement in the database.

        Args:
            requirement: Requirement object to store

        Returns:
            ID of the stored requirement
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check if requirement already exists
            existing = cursor.execute(
                """
                SELECT id FROM requirements 
                WHERE file_path = ? AND code_symbol = ? AND requirement_text = ?
            """,
                (
                    requirement.file_path,
                    requirement.code_symbol,
                    requirement.requirement_text,
                ),
            ).fetchone()

            if existing:
                # Update existing requirement
                cursor.execute(
                    """
                    UPDATE requirements 
                    SET commit_hash = ?, confidence = ?, status = ?, metadata = ?
                    WHERE id = ?
                """,
                    (
                        requirement.commit_hash,
                        requirement.confidence,
                        requirement.status,
                        json.dumps(requirement.metadata),
                        existing[0],
                    ),
                )
                return existing[0]
            else:
                # Insert new requirement
                cursor.execute(
                    """
                    INSERT INTO requirements 
                    (requirement_text, file_path, code_symbol, commit_hash, confidence, status, created_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        requirement.requirement_text,
                        requirement.file_path,
                        requirement.code_symbol,
                        requirement.commit_hash,
                        requirement.confidence,
                        requirement.status,
                        requirement.created_at,
                        json.dumps(requirement.metadata),
                    ),
                )

                return cursor.lastrowid

    def get_requirement(self, requirement_id: int) -> Optional[Requirement]:
        """Get a requirement by ID.

        Args:
            requirement_id: ID of the requirement

        Returns:
            Requirement object or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            row = cursor.execute(
                """
                SELECT * FROM requirements WHERE id = ?
            """,
                (requirement_id,),
            ).fetchone()

            if row:
                return self._row_to_requirement(row)
            return None

    def get_requirements_for_file(
        self, file_path: str, status: str = None
    ) -> List[Requirement]:
        """Get all requirements for a specific file.

        Args:
            file_path: Path to the file
            status: Optional status filter ('approved', 'pending', 'rejected')

        Returns:
            List of requirements for the file
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if status:
                rows = cursor.execute(
                    """
                    SELECT * FROM requirements 
                    WHERE file_path = ? AND status = ?
                    ORDER BY created_at DESC
                """,
                    (file_path, status),
                ).fetchall()
            else:
                rows = cursor.execute(
                    """
                    SELECT * FROM requirements 
                    WHERE file_path = ?
                    ORDER BY created_at DESC
                """,
                    (file_path,),
                ).fetchall()

            return [self._row_to_requirement(row) for row in rows]

    def approve_requirement(self, requirement_id: int) -> bool:
        """Approve a requirement.

        Args:
            requirement_id: ID of the requirement to approve

        Returns:
            True if successful, False otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE requirements 
                SET status = 'approved'
                WHERE id = ?
            """,
                (requirement_id,),
            )

            return cursor.rowcount > 0

    def reject_requirement(self, requirement_id: int) -> bool:
        """Reject a requirement.

        Args:
            requirement_id: ID of the requirement to reject

        Returns:
            True if successful, False otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE requirements 
                SET status = 'rejected'
                WHERE id = ?
            """,
                (requirement_id,),
            )

            return cursor.rowcount > 0

    def update_requirement_text(self, requirement_id: int, new_text: str) -> bool:
        """Update the text of a requirement.

        Args:
            requirement_id: ID of the requirement to update
            new_text: New requirement text

        Returns:
            True if successful, False otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE requirements 
                SET requirement_text = ?
                WHERE id = ?
            """,
                (new_text, requirement_id),
            )

            return cursor.rowcount > 0

    def get_approved_requirements(self) -> List[Requirement]:
        """Get all approved requirements.

        Returns:
            List of approved requirements
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            rows = cursor.execute(
                """
                SELECT * FROM requirements 
                WHERE status = 'approved'
                ORDER BY created_at DESC
            """
            ).fetchall()

            return [self._row_to_requirement(row) for row in rows]

    def get_pending_requirements(self) -> List[Requirement]:
        """Get all pending requirements awaiting approval.

        Returns:
            List of pending requirements
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            rows = cursor.execute(
                """
                SELECT * FROM requirements 
                WHERE status = 'pending'
                ORDER BY created_at DESC
            """
            ).fetchall()

            return [self._row_to_requirement(row) for row in rows]

    def delete_requirement(self, requirement_id: int) -> bool:
        """Delete a requirement.

        Args:
            requirement_id: ID of the requirement to delete

        Returns:
            True if successful, False otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                DELETE FROM requirements WHERE id = ?
            """,
                (requirement_id,),
            )

            return cursor.rowcount > 0

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about stored requirements.

        Returns:
            Dictionary with requirement statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            total = cursor.execute("SELECT COUNT(*) FROM requirements").fetchone()[0]
            approved = cursor.execute(
                "SELECT COUNT(*) FROM requirements WHERE status = 'approved'"
            ).fetchone()[0]
            pending = cursor.execute(
                "SELECT COUNT(*) FROM requirements WHERE status = 'pending'"
            ).fetchone()[0]
            rejected = cursor.execute(
                "SELECT COUNT(*) FROM requirements WHERE status = 'rejected'"
            ).fetchone()[0]

            avg_confidence = cursor.execute(
                "SELECT AVG(confidence) FROM requirements WHERE status = 'approved'"
            ).fetchone()[0]

            return {
                "total": total,
                "approved": approved,
                "pending": pending,
                "rejected": rejected,
                "avg_confidence": avg_confidence or 0.0,
            }

    def _row_to_requirement(self, row) -> Requirement:
        """Convert a database row to a Requirement object.

        Args:
            row: SQLite row object

        Returns:
            Requirement object
        """
        metadata = json.loads(row["metadata"]) if row["metadata"] else {}

        return Requirement(
            id=row["id"],
            requirement_text=row["requirement_text"],
            file_path=row["file_path"],
            code_symbol=row["code_symbol"],
            commit_hash=row["commit_hash"],
            confidence=row["confidence"],
            status=row["status"],
            created_at=row["created_at"],
            metadata=metadata,
        )

    def _get_current_commit_hash(self) -> Optional[str]:
        """Get the current git commit hash.

        Returns:
            Current commit hash or None if not in git repo
        """
        try:
            import subprocess

            result = subprocess.run(
                ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def create_requirement_from_inference(
        self,
        requirement_text: str,
        file_path: str,
        confidence: float,
        metadata: Dict[str, Any] = None,
    ) -> Requirement:
        """Create a new requirement from inference results.

        Args:
            requirement_text: The inferred requirement text
            file_path: Path to the file
            confidence: Confidence score
            metadata: Additional metadata

        Returns:
            New Requirement object (not yet stored)
        """
        # Extract code symbol from file path for simplicity
        code_symbol = os.path.basename(file_path).replace(".py", "")

        return Requirement(
            id=None,
            requirement_text=requirement_text,
            file_path=file_path,
            code_symbol=code_symbol,
            commit_hash=self._get_current_commit_hash(),
            confidence=confidence,
            status="pending",
            created_at=datetime.now().isoformat(),
            metadata=metadata or {},
        )

    def get_all_requirements(self) -> List[Requirement]:
        """Get all requirements regardless of status.

        Returns:
            List of all requirements
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            rows = cursor.execute(
                """
                SELECT * FROM requirements 
                ORDER BY created_at DESC
            """
            ).fetchall()

            return [self._row_to_requirement(row) for row in rows]
