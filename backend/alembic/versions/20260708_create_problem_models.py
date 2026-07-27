"""create problems, test_cases, and code_drafts tables

Revision ID: 9dd9d2e8ff61
Revises: 4e72ce1f6f6b
Create Date: 2026-07-08 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "9dd9d2e8ff61"
down_revision = "4e72ce1f6f6b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    difficulty_enum = sa.Enum("EASY", "MEDIUM", "HARD", name="difficultylevel")
    topic_enum = sa.Enum(
        "ARRAYS",
        "STRINGS",
        "HASHING",
        "LINKED_LISTS",
        "STACKS",
        "QUEUES",
        "TREES",
        "GRAPHS",
        "RECURSION",
        "BACKTRACKING",
        "DYNAMIC_PROGRAMMING",
        "SEARCHING",
        "SORTING",
        name="topictype",
    )
    difficulty_enum.create(op.get_bind(), checkfirst=True)
    topic_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "problems",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("difficulty", difficulty_enum, nullable=False),
        sa.Column("topic", topic_enum, nullable=False),
        sa.Column("constraints", sa.Text(), nullable=False),
        sa.Column("input_format", sa.Text(), nullable=False),
        sa.Column("output_format", sa.Text(), nullable=False),
        sa.Column("starter_code", sa.JSON(), nullable=False),
        sa.Column("time_limit_ms", sa.Integer(), nullable=False),
        sa.Column("memory_limit_mb", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_problems_created_by"), "problems", ["created_by"], unique=False)
    op.create_index(op.f("ix_problems_id"), "problems", ["id"], unique=False)
    op.create_index(op.f("ix_problems_slug"), "problems", ["slug"], unique=True)

    op.create_table(
        "test_cases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("problem_id", sa.Integer(), nullable=False),
        sa.Column("input_data", sa.Text(), nullable=False),
        sa.Column("expected_output", sa.Text(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("is_sample", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["problem_id"], ["problems.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_test_cases_id"), "test_cases", ["id"], unique=False)
    op.create_index(op.f("ix_test_cases_problem_id"), "test_cases", ["problem_id"], unique=False)

    op.create_table(
        "code_drafts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("problem_id", sa.Integer(), nullable=False),
        sa.Column("language", sa.String(length=50), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["problem_id"], ["problems.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("student_id", "problem_id", "language", name="uq_code_draft_student_problem_language"),
    )
    op.create_index(op.f("ix_code_drafts_id"), "code_drafts", ["id"], unique=False)
    op.create_index(op.f("ix_code_drafts_problem_id"), "code_drafts", ["problem_id"], unique=False)
    op.create_index(op.f("ix_code_drafts_student_id"), "code_drafts", ["student_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_code_drafts_student_id"), table_name="code_drafts")
    op.drop_index(op.f("ix_code_drafts_problem_id"), table_name="code_drafts")
    op.drop_index(op.f("ix_code_drafts_id"), table_name="code_drafts")
    op.drop_table("code_drafts")
    op.drop_index(op.f("ix_test_cases_problem_id"), table_name="test_cases")
    op.drop_index(op.f("ix_test_cases_id"), table_name="test_cases")
    op.drop_table("test_cases")
    op.drop_index(op.f("ix_problems_slug"), table_name="problems")
    op.drop_index(op.f("ix_problems_id"), table_name="problems")
    op.drop_index(op.f("ix_problems_created_by"), table_name="problems")
    op.drop_table("problems")
    sa.Enum(name="difficultylevel").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="topictype").drop(op.get_bind(), checkfirst=True)
