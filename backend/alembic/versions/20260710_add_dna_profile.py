"""add dna profile table

Revision ID: 20260710_add_dna_profile
Revises: b3c3f447a01b
Create Date: 2026-07-10 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "20260710_add_dna_profile"
down_revision = "b3c3f447a01b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "coding_dna_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("overall_score", sa.Float(), nullable=True),
        sa.Column("overall_confidence", sa.Float(), nullable=True),
        sa.Column("logic_score", sa.Float(), nullable=True),
        sa.Column("logic_confidence", sa.Float(), nullable=True),
        sa.Column("debugging_score", sa.Float(), nullable=True),
        sa.Column("debugging_confidence", sa.Float(), nullable=True),
        sa.Column("optimization_score", sa.Float(), nullable=True),
        sa.Column("optimization_confidence", sa.Float(), nullable=True),
        sa.Column("consistency_score", sa.Float(), nullable=True),
        sa.Column("consistency_confidence", sa.Float(), nullable=True),
        sa.Column("learning_velocity_score", sa.Float(), nullable=True),
        sa.Column("learning_velocity_confidence", sa.Float(), nullable=True),
        sa.Column("breadth_score", sa.Float(), nullable=True),
        sa.Column("breadth_confidence", sa.Float(), nullable=True),
        sa.Column("evidence_status", sa.String(length=50), nullable=False),
        sa.Column("scoring_version", sa.String(length=20), nullable=False),
        sa.Column("feature_snapshot_json", sa.JSON(), nullable=False, default={}),
        sa.Column("explanation_snapshot_json", sa.JSON(), nullable=False, default={}),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_coding_dna_profiles_student_id"), "coding_dna_profiles", ["student_id"], unique=False)
    op.create_index(op.f("ix_coding_dna_profiles_calculated_at"), "coding_dna_profiles", ["calculated_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_coding_dna_profiles_calculated_at"), table_name="coding_dna_profiles")
    op.drop_index(op.f("ix_coding_dna_profiles_student_id"), table_name="coding_dna_profiles")
    op.drop_table("coding_dna_profiles")
