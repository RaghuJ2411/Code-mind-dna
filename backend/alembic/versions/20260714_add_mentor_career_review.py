"""add mentor career review table

Revision ID: 20260714_add_mentor_career_review
Revises: 20260713_add_career_models
Create Date: 2026-07-14 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "20260714_add_mentor_career_review"
down_revision = "20260713_add_career_models"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("mentor_career_reviews"):
        op.create_table(
            "mentor_career_reviews",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("mentor_id", sa.Integer(), nullable=False, index=True),
            sa.Column("student_id", sa.Integer(), nullable=False, index=True),
            sa.Column("role_id", sa.Integer(), nullable=True, index=True),
            sa.Column("review_type", sa.String(length=50), nullable=False, default="CAREER"),
            sa.Column("note", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
        )


def downgrade() -> None:
    op.drop_table("mentor_career_reviews")
