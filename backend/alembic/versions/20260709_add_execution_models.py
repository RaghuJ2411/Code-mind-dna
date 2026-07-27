"""add execution, submission, session, and coding event tables

Revision ID: b3c3f447a01b
Revises: 9dd9d2e8ff61
Create Date: 2026-07-09 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b3c3f447a01b"
down_revision = "9dd9d2e8ff61"
branch_labels = None
depends_on = None


def upgrade() -> None:
    verdict_enum = sa.Enum("ACCEPTED", "WRONG_ANSWER", "COMPILATION_ERROR", "RUNTIME_ERROR", "TIME_LIMIT_EXCEEDED", "MEMORY_LIMIT_EXCEEDED", "INTERNAL_ERROR", name="submissionverdict")
    verdict_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "submissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("problem_id", sa.Integer(), nullable=False),
        sa.Column("language", sa.String(length=50), nullable=False),
        sa.Column("source_code", sa.Text(), nullable=False),
        sa.Column("verdict", verdict_enum, nullable=False),
        sa.Column("passed_test_cases", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_test_cases", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("runtime_ms", sa.Integer(), nullable=True),
        sa.Column("memory_kb", sa.Integer(), nullable=True),
        sa.Column("attempt_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("error_type", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["problem_id"], ["problems.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_submissions_created_at"), "submissions", ["created_at"], unique=False)
    op.create_index(op.f("ix_submissions_id"), "submissions", ["id"], unique=False)
    op.create_index(op.f("ix_submissions_problem_id"), "submissions", ["problem_id"], unique=False)
    op.create_index(op.f("ix_submissions_student_id"), "submissions", ["student_id"], unique=False)
    op.create_index(op.f("ix_submissions_verdict"), "submissions", ["verdict"], unique=False)

    op.create_table(
        "coding_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("problem_id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=True),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("language", sa.String(length=50), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["problem_id"], ["problems.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_coding_events_created_at"), "coding_events", ["created_at"], unique=False)
    op.create_index(op.f("ix_coding_events_event_type"), "coding_events", ["event_type"], unique=False)
    op.create_index(op.f("ix_coding_events_id"), "coding_events", ["id"], unique=False)

    op.create_table(
        "coding_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("problem_id", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("language", sa.String(length=50), nullable=False),
        sa.Column("run_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("submit_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_solved", sa.Boolean(), nullable=False, server_default="false"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["problem_id"], ["problems.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("coding_sessions")
    op.drop_index(op.f("ix_coding_events_id"), table_name="coding_events")
    op.drop_index(op.f("ix_coding_events_event_type"), table_name="coding_events")
    op.drop_index(op.f("ix_coding_events_created_at"), table_name="coding_events")
    op.drop_table("coding_events")
    op.drop_index(op.f("ix_submissions_verdict"), table_name="submissions")
    op.drop_index(op.f("ix_submissions_student_id"), table_name="submissions")
    op.drop_index(op.f("ix_submissions_problem_id"), table_name="submissions")
    op.drop_index(op.f("ix_submissions_id"), table_name="submissions")
    op.drop_index(op.f("ix_submissions_created_at"), table_name="submissions")
    op.drop_table("submissions")
    sa.Enum(name="submissionverdict").drop(op.get_bind(), checkfirst=True)
