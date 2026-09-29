from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./fitbuddy.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# Safely add new columns to the existing database
with engine.connect() as connection:

    # Check users table
    result = connection.execute(
        text("PRAGMA table_info(users)")
    )

    user_columns = [row[1] for row in result]

    if user_columns:

        if "name" not in user_columns:
            connection.execute(
                text("ALTER TABLE users ADD COLUMN name TEXT")
            )

        if "user_code" not in user_columns:
            connection.execute(
                text("ALTER TABLE users ADD COLUMN user_code TEXT")
            )

        if "weight" not in user_columns:
            connection.execute(
                text("ALTER TABLE users ADD COLUMN weight REAL")
            )

        if "intensity" not in user_columns:
            connection.execute(
                text("ALTER TABLE users ADD COLUMN intensity TEXT")
            )

        connection.commit()


    # Check fitness_plans table
    result = connection.execute(
        text("PRAGMA table_info(fitness_plans)")
    )

    plan_columns = [row[1] for row in result]

    if plan_columns and "updated_plan" not in plan_columns:

        connection.execute(
            text(
                "ALTER TABLE fitness_plans "
                "ADD COLUMN updated_plan TEXT"
            )
        )

        connection.commit()