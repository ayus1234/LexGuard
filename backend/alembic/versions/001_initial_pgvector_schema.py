"""Initial PostgreSQL pgvector schema for documents and chunks

Revision ID: 001_initial_pgvector_schema
Revises: 
Create Date: 2026-09-23 20:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '001_initial_pgvector_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 2. Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('document_id', sa.String(length=64), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('document_type', sa.String(length=16), nullable=False),
        sa.Column('source_type', sa.String(length=32), server_default='upload', nullable=False),
        sa.Column('mime_type', sa.String(length=64), nullable=False),
        sa.Column('word_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('character_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('page_count', sa.Integer(), server_default='1', nullable=False),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('processing_status', sa.String(length=32), server_default='uploaded', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id')
    )
    op.create_index('ix_documents_document_id', 'documents', ['document_id'], unique=True)
    op.create_index('ix_documents_content_hash', 'documents', ['content_hash'], unique=False)

    # 3. Create document_chunks table with 3072-dim Vector
    op.create_table(
        'document_chunks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('document_id', sa.String(length=64), nullable=False),
        sa.Column('chunk_id', sa.String(length=64), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', Vector(3072), nullable=False),
        sa.Column('page_start', sa.Integer(), server_default='1', nullable=False),
        sa.Column('page_end', sa.Integer(), server_default='1', nullable=False),
        sa.Column('char_start', sa.Integer(), server_default='0', nullable=False),
        sa.Column('char_end', sa.Integer(), server_default='0', nullable=False),
        sa.Column('section', sa.String(length=255), nullable=True),
        sa.Column('heading', sa.String(length=255), nullable=True),
        sa.Column('chunk_index', sa.Integer(), server_default='0', nullable=False),
        sa.Column('token_estimate', sa.Integer(), server_default='0', nullable=False),
        sa.Column('chunk_metadata', sa.JSON(), server_default='{}', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.document_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('chunk_id')
    )
    op.create_index('ix_document_chunks_document_id', 'document_chunks', ['document_id'], unique=False)
    op.create_index('ix_document_chunks_chunk_id', 'document_chunks', ['chunk_id'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_document_chunks_chunk_id', table_name='document_chunks')
    op.drop_index('ix_document_chunks_document_id', table_name='document_chunks')
    op.drop_table('document_chunks')
    op.drop_index('ix_documents_content_hash', table_name='documents')
    op.drop_index('ix_documents_document_id', table_name='documents')
    op.drop_table('documents')
