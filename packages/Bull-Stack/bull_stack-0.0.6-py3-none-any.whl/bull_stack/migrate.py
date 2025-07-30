import os
import io
from contextlib import redirect_stdout
from flask_migrate import Migrate, upgrade, migrate as migrate_command
from alembic.script import ScriptDirectory
from alembic.config import Config

def has_model_changes(app, db) -> bool:
    """Run `migrate` and check if it results in a new revision."""
    Migrate(app, db, render_as_batch=True, compare_type=False)

    migrate_dir = os.path.join(os.path.dirname(__file__), 'migrations')
    alembic_cfg = Config(os.path.join(migrate_dir, 'alembic.ini'))
    alembic_cfg.set_main_option("script_location", migrate_dir)

    # Capture output of the migration command
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        try:
            migrate_command(message='Auto migration')
        except Exception as e:
            print(f"Migration failed: {e}")
            return False

    output = buffer.getvalue()

    # No changes = Alembic says "Target database is up to date"
    if "No changes in schema detected" in output:
        return False

    return True

def run_conditional_migration(app, db):
    with app.app_context():
        if has_model_changes(app, db):
            if os.environ.get("AUTO_DB_MIGRATION") == "true":
                print("Changes detected—running upgrade")
                upgrade()
            else:
                print("No migration allowed")
        else:
            print("No changes detected—no migration needed")
