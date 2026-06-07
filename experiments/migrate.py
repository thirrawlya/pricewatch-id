from database import init_db, migrate_db_schema


if __name__ == "__main__":
    init_db()
    migrate_db_schema()
    print("✅ Migration complete. Legacy data has been converted to the new schema.")
