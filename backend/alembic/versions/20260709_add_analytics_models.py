"""add analytics models and coding session error counters

Revision ID: c5f4a7e9b2c8
Revises: b3c3f447a01b
Create Date: 2026-07-09 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "c5f4a7e9b2c8"
down_revision = "b3c3f447a01b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add error counters to coding_sessions
    op.add_column("coding_sessions", sa.Column("wrong_answer_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("coding_sessions", sa.Column("compilation_error_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("coding_sessions", sa.Column("runtime_error_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("coding_sessions", sa.Column("time_limit_count", sa.Integer(), nullable=False, server_default="0"))

    # Create student_daily_analytics table
    op.create_table(
        "student_daily_analytics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("analytics_date", sa.Date(), nullable=False),
        sa.Column("problems_attempted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("problems_solved", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("submissions_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("runs_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("active_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("wrong_answer_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("compilation_error_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("runtime_error_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("time_limit_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("easy_attempted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("easy_solved", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("medium_attempted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("medium_solved", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("hard_attempted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("hard_solved", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unique_topics_attempted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_student_daily_analytics_analytics_date"), "student_daily_analytics", ["analytics_date"], unique=False)
    op.create_index(op.f("ix_student_daily_analytics_id"), "student_daily_analytics", ["id"], unique=False)
    op.create_index(op.f("ix_student_daily_analytics_student_id"), "student_daily_analytics", ["student_id"], unique=False)
    op.create_unique_constraint("uq_daily_analytics_student_date", "student_daily_analytics", ["student_id", "analytics_date"])

    # Create student_weekly_analytics table
    op.create_table(
        "student_weekly_analytics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("week_end", sa.Date(), nullable=False),
        sa.Column("problems_attempted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("problems_solved", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("solve_rate", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("submissions_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("runs_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("active_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("active_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("average_attempts_to_solve", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("average_solve_time_minutes", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("error_recovery_rate", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("easy_solve_rate", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("medium_solve_rate", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("hard_solve_rate", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("unique_topics_attempted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("difficulty_progression_delta", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_student_weekly_analytics_id"), "student_weekly_analytics", ["id"], unique=False)
    op.create_index(op.f("ix_student_weekly_analytics_student_id"), "student_weekly_analytics", ["student_id"], unique=False)
    op.create_index(op.f("ix_student_weekly_analytics_week_start"), "student_weekly_analytics", ["week_start"], unique=False)
    op.create_unique_constraint("uq_weekly_analytics_student_week", "student_weekly_analytics", ["student_id", "week_start"])


def downgrade() -> None:
    op.drop_constraint("uq_weekly_analytics_student_week", "student_weekly_analytics", type_="unique")
    op.drop_index(op.f("ix_student_weekly_analytics_week_start"), table_name="student_weekly_analytics")
    op.drop_index(op.f("ix_student_weekly_analytics_student_id"), table_name="student_weekly_analytics")
    op.drop_index(op.f("ix_student_weekly_analytics_id"), table_name="student_weekly_analytics")
    op.drop_table("student_weekly_analytics")

    op.drop_constraint("uq_daily_analytics_student_date", "student_daily_analytics", type_="unique")
    op.drop_index(op.f("ix_student_daily_analytics_student_id"), table_name="student_daily_analytics")
    op.drop_index(op.f("ix_student_daily_analytics_analytics_date"), table_name="student_daily_analytics")
    op.drop_index(op.f("ix_student_daily_analytics_id"), table_name="student_daily_analytics")
    op.drop_table("student_daily_analytics")

    op.drop_column("coding_sessions", "time_limit_count")
    op.drop_column("coding_sessions", "runtime_error_count")
    op.drop_column("coding_sessions", "compilation_error_count")
    op.drop_column("coding_sessions", "wrong_answer_count")
