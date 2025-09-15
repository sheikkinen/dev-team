"""
Database models for face-changer pipeline

IMPORTANT: Changes via Change Management, see CLAUDE.md
"""
import sqlite3
import json
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class Database:
    """SQLite database manager for face-changer pipeline"""
    
    def __init__(self, db_path: str = "data/pipeline.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._ensure_tables()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _ensure_tables(self):
        """Create database tables if they don't exist"""
        with self._get_connection() as conn:
            # Jobs table - replaces data/queue.json
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT UNIQUE NOT NULL,
                    input_image_path TEXT NOT NULL,
                    user_prompt TEXT,
                    padding_factor REAL DEFAULT 1.5,
                    mask_padding_factor REAL DEFAULT 1.2,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    error_message TEXT
                )
            """)
            
            # Pipeline results - replaces log parsing
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pipeline_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL,
                    step_name TEXT NOT NULL,
                    step_number INTEGER NOT NULL,
                    face_coordinates TEXT,
                    crop_dimensions TEXT,
                    file_paths TEXT,
                    metadata TEXT,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (job_id) REFERENCES jobs (job_id)
                )
            """)
            
            # Pipeline state - replaces log file communication
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pipeline_state (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL,
                    base_filename TEXT NOT NULL,
                    current_step INTEGER DEFAULT 1,
                    step_name TEXT,
                    input_file TEXT,
                    output_file TEXT,
                    face_coords_raw TEXT,
                    crop_geometry TEXT,
                    extracted_prompt TEXT,
                    processing_notes TEXT,
                    success BOOLEAN DEFAULT 1,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (job_id) REFERENCES jobs (job_id)
                )
            """)
            
            # Research results - stores LLM-generated research content
            conn.execute("""
                CREATE TABLE IF NOT EXISTS research_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT UNIQUE NOT NULL,
                    research_topic TEXT NOT NULL,
                    generated_content TEXT NOT NULL,
                    prompt_used TEXT,
                    llm_model TEXT,
                    completion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    word_count INTEGER,
                    metadata TEXT,
                    FOREIGN KEY (job_id) REFERENCES jobs (job_id)
                )
            """)
            
            # Create indexes for better query performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs (status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_created ON jobs (created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_results_job ON pipeline_results (job_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_state_job ON pipeline_state (job_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_state_base ON pipeline_state (job_id, base_filename)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_research_job ON research_results (job_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_research_timestamp ON research_results (completion_timestamp)")
            
            conn.commit()

class JobModel:
    """Model for job management"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def create_job(self, job_id: str, input_image_path: str, 
                   user_prompt: str = "make this person more attractive",
                   padding_factor: float = 1.5,
                   mask_padding_factor: float = 1.2) -> int:
        """Create a new job"""
        with self.db._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO jobs (job_id, input_image_path, user_prompt, 
                                padding_factor, mask_padding_factor)
                VALUES (?, ?, ?, ?, ?)
            """, (job_id, input_image_path, user_prompt, padding_factor, mask_padding_factor))
            return cursor.lastrowid
    
    def get_next_job(self) -> Optional[Dict[str, Any]]:
        """Get next pending job (replaces queue.get())"""
        with self.db._get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM jobs 
                WHERE status = 'pending' 
                ORDER BY created_at 
                LIMIT 1
            """).fetchone()
            
            if row:
                # Mark as processing
                conn.execute("""
                    UPDATE jobs 
                    SET status = 'processing', started_at = CURRENT_TIMESTAMP
                    WHERE job_id = ?
                """, (row['job_id'],))
                conn.commit()
                return dict(row)
            return None
    
    def complete_job(self, job_id: str):
        """Mark job as completed"""
        with self.db._get_connection() as conn:
            conn.execute("""
                UPDATE jobs 
                SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                WHERE job_id = ?
            """, (job_id,))
            conn.commit()
    
    def fail_job(self, job_id: str, error_message: str):
        """Mark job as failed"""
        with self.db._get_connection() as conn:
            conn.execute("""
                UPDATE jobs 
                SET status = 'failed', error_message = ?, completed_at = CURRENT_TIMESTAMP
                WHERE job_id = ?
            """, (error_message, job_id))
            conn.commit()
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID"""
        with self.db._get_connection() as conn:
            row = conn.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
            return dict(row) if row else None
    
    def list_jobs(self, status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """List jobs with optional status filter"""
        with self.db._get_connection() as conn:
            if status:
                rows = conn.execute("""
                    SELECT * FROM jobs WHERE status = ? 
                    ORDER BY created_at DESC LIMIT ?
                """, (status, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM jobs 
                    ORDER BY created_at DESC LIMIT ?
                """, (limit,)).fetchall()
            return [dict(row) for row in rows]
    
    def count_jobs(self, status: Optional[str] = None) -> int:
        """Count jobs by status"""
        with self.db._get_connection() as conn:
            if status:
                return conn.execute("SELECT COUNT(*) FROM jobs WHERE status = ?", (status,)).fetchone()[0]
            else:
                return conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    
    def reset_job_to_pending(self, job_id: str, reason: str = "Reset to pending"):
        """Reset a specific job from processing back to pending"""
        with self.db._get_connection() as conn:
            conn.execute("""
                UPDATE jobs 
                SET status = 'pending', started_at = NULL, error_message = ?
                WHERE job_id = ? AND status = 'processing'
            """, (reason, job_id))
            conn.commit()
            logger.info(f"Reset job {job_id} to pending: {reason}")
    
    def get_processing_jobs_with_missing_files(self) -> List[Dict[str, Any]]:
        """Find processing jobs that reference non-existent input files"""
        with self.db._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM jobs WHERE status = 'processing'
                ORDER BY started_at
            """).fetchall()
            
            problem_jobs = []
            for row in rows:
                job_dict = dict(row)
                input_path = Path(job_dict['input_image_path'])
                if not input_path.exists():
                    problem_jobs.append(job_dict)
            
            return problem_jobs

class PipelineResultModel:
    """Model for pipeline step results"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def record_step(self, job_id: str, step_name: str, step_number: int,
                   face_coordinates: Optional[Dict] = None,
                   crop_dimensions: Optional[Dict] = None,
                   file_paths: Optional[Dict] = None,
                   metadata: Optional[Dict] = None):
        """Record completion of a pipeline step"""
        with self.db._get_connection() as conn:
            conn.execute("""
                INSERT INTO pipeline_results 
                (job_id, step_name, step_number, face_coordinates, 
                 crop_dimensions, file_paths, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                job_id, step_name, step_number,
                json.dumps(face_coordinates) if face_coordinates else None,
                json.dumps(crop_dimensions) if crop_dimensions else None,
                json.dumps(file_paths) if file_paths else None,
                json.dumps(metadata) if metadata else None
            ))
            conn.commit()
    
    def get_job_results(self, job_id: str) -> List[Dict[str, Any]]:
        """Get all pipeline results for a job"""
        with self.db._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM pipeline_results 
                WHERE job_id = ? 
                ORDER BY step_number
            """, (job_id,)).fetchall()
            
            results = []
            for row in rows:
                result = dict(row)
                # Parse JSON fields
                for field in ['face_coordinates', 'crop_dimensions', 'file_paths', 'metadata']:
                    if result[field]:
                        result[field] = json.loads(result[field])
                results.append(result)
            return results
    
    def get_face_coordinates(self, job_id: str) -> Optional[Dict]:
        """Get face coordinates for a job"""
        with self.db._get_connection() as conn:
            row = conn.execute("""
                SELECT face_coordinates FROM pipeline_results 
                WHERE job_id = ? AND step_name = 'coordinate_extraction'
                ORDER BY completed_at DESC LIMIT 1
            """, (job_id,)).fetchone()
            
            if row and row['face_coordinates']:
                return json.loads(row['face_coordinates'])
            return None
    
    def get_crop_dimensions(self, job_id: str) -> Optional[Dict]:
        """Get crop dimensions for a job"""
        with self.db._get_connection() as conn:
            row = conn.execute("""
                SELECT crop_dimensions FROM pipeline_results 
                WHERE job_id = ? AND step_name = 'cropping_faces'
                ORDER BY completed_at DESC LIMIT 1
            """, (job_id,)).fetchone()
            
            if row and row['crop_dimensions']:
                return json.loads(row['crop_dimensions'])
            return None

# Global database instance
_db_instance = None

def get_database() -> Database:
    """Get singleton database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance

def get_job_model() -> JobModel:
    """Get job model instance"""
    return JobModel(get_database())

def get_pipeline_model() -> PipelineResultModel:
    """Get pipeline result model instance"""
    return PipelineResultModel(get_database())

class PipelineStateModel:
    """Model for shell script communication via database"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def store_coordinates(self, job_id: str, base_filename: str, coordinates: str, 
                         step_name: str = "coordinate_extraction", success: bool = True):
        """Store face coordinates for shell script communication"""
        with self.db._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO pipeline_state 
                (job_id, base_filename, step_name, face_coords_raw, success, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (job_id, base_filename, step_name, coordinates, success))
            conn.commit()
    
    def get_coordinates(self, job_id: str, base_filename: str) -> Optional[str]:
        """Get face coordinates for shell script communication"""
        with self.db._get_connection() as conn:
            row = conn.execute("""
                SELECT face_coords_raw FROM pipeline_state 
                WHERE job_id = ? AND base_filename = ? AND face_coords_raw IS NOT NULL
                ORDER BY updated_at DESC LIMIT 1
            """, (job_id, base_filename)).fetchone()
            return row['face_coords_raw'] if row else None
    
    def store_crop_geometry(self, job_id: str, base_filename: str, geometry: str,
                           step_name: str = "cropping_faces", success: bool = True):
        """Store crop geometry for shell script communication"""
        with self.db._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO pipeline_state 
                (job_id, base_filename, step_name, crop_geometry, success, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (job_id, base_filename, step_name, geometry, success))
            conn.commit()
    
    def get_crop_geometry(self, job_id: str, base_filename: str) -> Optional[str]:
        """Get crop geometry for shell script communication"""
        with self.db._get_connection() as conn:
            row = conn.execute("""
                SELECT crop_geometry FROM pipeline_state 
                WHERE job_id = ? AND base_filename = ? AND crop_geometry IS NOT NULL
                ORDER BY updated_at DESC LIMIT 1
            """, (job_id, base_filename)).fetchone()
            return row['crop_geometry'] if row else None
    
    def store_prompt(self, job_id: str, base_filename: str, prompt: str,
                    step_name: str = "prompt_extraction", success: bool = True):
        """Store extracted prompt for shell script communication"""
        with self.db._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO pipeline_state 
                (job_id, base_filename, step_name, extracted_prompt, success, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (job_id, base_filename, step_name, prompt, success))
            conn.commit()
    
    def get_prompt(self, job_id: str, base_filename: str) -> Optional[str]:
        """Get extracted prompt for shell script communication"""
        with self.db._get_connection() as conn:
            row = conn.execute("""
                SELECT extracted_prompt FROM pipeline_state 
                WHERE job_id = ? AND base_filename = ? AND extracted_prompt IS NOT NULL
                ORDER BY updated_at DESC LIMIT 1
            """, (job_id, base_filename)).fetchone()
            return row['extracted_prompt'] if row else None
    
    def store_step_result(self, job_id: str, base_filename: str, step_name: str,
                         input_file: str = None, output_file: str = None, 
                         processing_notes: str = None, success: bool = True):
        """Store general step result for shell script communication"""
        with self.db._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO pipeline_state 
                (job_id, base_filename, step_name, input_file, output_file, 
                 processing_notes, success, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (job_id, base_filename, step_name, input_file, output_file, 
                  processing_notes, success))
            conn.commit()
    
    def get_step_result(self, job_id: str, base_filename: str, step_name: str) -> Optional[Dict[str, Any]]:
        """Get step result for shell script communication"""
        with self.db._get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM pipeline_state 
                WHERE job_id = ? AND base_filename = ? AND step_name = ?
                ORDER BY updated_at DESC LIMIT 1
            """, (job_id, base_filename, step_name)).fetchone()
            return dict(row) if row else None

class ResearchResultModel:
    """Model for research result management"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def create_result(self, job_id: str, research_topic: str, generated_content: str,
                     prompt_used: str = None, llm_model: str = None, 
                     metadata: str = None) -> int:
        """Create a new research result"""
        word_count = len(generated_content.split()) if generated_content else 0
        
        with self.db._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO research_results 
                (job_id, research_topic, generated_content, prompt_used, llm_model, word_count, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (job_id, research_topic, generated_content, prompt_used, llm_model, word_count, metadata))
            return cursor.lastrowid
    
    def get_result_by_job_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get research result by job ID"""
        with self.db._get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM research_results WHERE job_id = ?
            """, (job_id,)).fetchone()
            return dict(row) if row else None
    
    def list_results(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """List all research results with pagination"""
        with self.db._get_connection() as conn:
            rows = conn.execute("""
                SELECT id, job_id, research_topic, word_count, completion_timestamp, llm_model
                FROM research_results 
                ORDER BY completion_timestamp DESC 
                LIMIT ? OFFSET ?
            """, (limit, offset)).fetchall()
            return [dict(row) for row in rows]
    
    def update_result(self, job_id: str, **kwargs) -> bool:
        """Update research result fields"""
        if not kwargs:
            return False
        
        # Build dynamic update query
        set_clauses = []
        params = []
        for key, value in kwargs.items():
            if key in ['research_topic', 'generated_content', 'prompt_used', 'llm_model', 'metadata']:
                set_clauses.append(f"{key} = ?")
                params.append(value)
        
        if not set_clauses:
            return False
        
        params.append(job_id)
        query = f"UPDATE research_results SET {', '.join(set_clauses)} WHERE job_id = ?"
        
        with self.db._get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.rowcount > 0
    
    def delete_result(self, job_id: str) -> bool:
        """Delete research result by job ID"""
        with self.db._get_connection() as conn:
            cursor = conn.execute("DELETE FROM research_results WHERE job_id = ?", (job_id,))
            return cursor.rowcount > 0
    
    def search_results(self, search_term: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search research results by topic or content"""
        with self.db._get_connection() as conn:
            rows = conn.execute("""
                SELECT id, job_id, research_topic, word_count, completion_timestamp, llm_model
                FROM research_results 
                WHERE research_topic LIKE ? OR generated_content LIKE ?
                ORDER BY completion_timestamp DESC 
                LIMIT ?
            """, (f"%{search_term}%", f"%{search_term}%", limit)).fetchall()
            return [dict(row) for row in rows]

def get_pipeline_state_model() -> PipelineStateModel:
    """Get pipeline state model instance"""
    return PipelineStateModel(get_database())

def get_research_result_model() -> ResearchResultModel:
    """Get research result model instance"""
    return ResearchResultModel(get_database())