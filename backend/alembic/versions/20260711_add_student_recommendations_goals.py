"""add student goals and recommendations tables

Revision ID: 20260711_add_student_recommendations_goals
Revises: 20260710_add_dna_profile
Create Date: 2026-07-11 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "20260711_add_student_recommendations_goals"
down_revision = "20260710_add_dna_profile"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "student_goals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("goal_type", sa.String(length=50), nullable=False),
        sa.Column("target_value", sa.Integer(), nullable=False),
        sa.Column("current_value", sa.Integer(), nullable=False, default=0),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_student_goals_student_id"), "student_goals", ["student_id"], unique=False)

    op.create_table(
        "student_recommendations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("recommendation_type", sa.String(length=100), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("action_json", sa.JSON(), nullable=False, default={}),
        sa.Column("source_snapshot_json", sa.JSON(), nullable=False, default={}),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("dismissed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_student_recommendations_student_id"), "student_recommendations", ["student_id"], unique=False)
    op.create_index(op.f("ix_student_recommendations_generated_at"), "student_recommendations", ["generated_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_student_recommendations_generated_at"), table_name="student_recommendations")
    op.drop_index(op.f("ix_student_recommendations_student_id"), table_name="student_recommendations")
    op.drop_table("student_recommendations")
    op.drop_index(op.f("ix_student_goals_student_id"), table_name="student_goals")
    op.drop_table("student_goals")
