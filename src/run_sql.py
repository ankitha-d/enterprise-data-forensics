import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "enterprise_forensics.db"

SQL_FILES = [
    BASE_DIR / "sql" / "reconciliation_queries.sql",
    BASE_DIR / "sql" / "investigation_queries.sql",
]


def run_queries():
    print("=" * 60)
    print("ENTERPRISE DATA FORENSICS")
    print("SQL Investigation Engine")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)

    total_queries = 0

    for sql_path in SQL_FILES:

        if not sql_path.exists():
            raise FileNotFoundError(
                f"SQL file not found: {sql_path}"
            )

        print(f"\nFile: {sql_path.name}")

        sql_text = sql_path.read_text(
            encoding="utf-8"
        )

        statements = [
            statement.strip()
            for statement in sql_text.split(";")
            if statement.strip()
        ]

        print(
            f"Queries found: {len(statements)}"
        )
        print("-" * 60)

        for number, statement in enumerate(
            statements,
            start=1
        ):
            lines = [
                line.strip()
                for line in statement.splitlines()
                if line.strip()
                and not line.strip().startswith("--")
            ]

            query = " ".join(lines)

            try:
                cursor = conn.execute(query)
                rows = cursor.fetchall()

                print(
                    f"Query {number:02d}: "
                    f"{len(rows):,} rows returned"
                )

                total_queries += 1

            except sqlite3.Error as error:
                print(
                    f"Query {number:02d}: FAILED"
                )
                print(f"Error: {error}")
                conn.close()
                raise

    conn.close()

    print("\n" + "=" * 60)
    print(
        f"All {total_queries} SQL investigation queries "
        "executed successfully."
    )
    print("=" * 60)


if __name__ == "__main__":
    run_queries()