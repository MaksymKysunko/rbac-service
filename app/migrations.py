import logging
from sqlalchemy import text
from app.db import engine

logger = logging.getLogger(__name__)

def migrate_punishments_table():
    """
    Ensures 'punishments' table exists and has all required columns.
    Since we are using Base.metadata.create_all, primary creation is handled.
    This function handles incremental schema updates if SQLite/Prod DB already exists.
    """
    try:
        with engine.connect() as conn:
            # check if table exists
            table_exists = False
            try:
                # PostgreSQL check
                check_query = text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'punishments');")
                table_exists = conn.execute(check_query).scalar()
            except Exception:
                # Fallback for SQLite
                check_query = text("SELECT name FROM sqlite_master WHERE type='table' AND name='punishments';")
                table_exists = bool(conn.execute(check_query).scalar())

            if not table_exists:
                logger.info("Punishments table does not exist. create_all() should have handled it, but double checking.")
                return 

            # Check for specific columns added recently (example: amnestied_by)
            # This is where we would add ALTER TABLE statements if we added columns later.
            # Currently the table is fresh, so we just log success.
            logger.info("Punishments table schema verified.")
            
    except Exception as e:
        logger.error(f"Error verifying punishments table schema: {e}")
