"""Supabase optimization and indexes

Revision ID: 002_supabase_setup
Revises: 001_complete_schema_initial
Create Date: 2025-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_supabase_setup'
down_revision = '001_complete_schema_initial'
branch_labels = None
depends_on = None


def upgrade():
    # Create indexes for better performance on Supabase
    
    # User table indexes
    op.create_index('ix_user_email', 'user', ['email'], unique=True)
    op.create_index('ix_user_username', 'user', ['username'], unique=True)
    op.create_index('ix_user_created_at', 'user', ['created_at'])
    op.create_index('ix_user_is_admin', 'user', ['is_admin'])
    op.create_index('ix_user_is_superuser', 'user', ['is_superuser'])
    
    # Photo table indexes
    op.create_index('ix_photo_user_id', 'photo', ['user_id'])
    op.create_index('ix_photo_uploaded_at', 'photo', ['uploaded_at'])
    op.create_index('ix_photo_album_id', 'photo', ['album_id'])
    op.create_index('ix_photo_photo_date', 'photo', ['photo_date'])
    
    # Album table indexes
    op.create_index('ix_album_user_id', 'album', ['user_id'])
    op.create_index('ix_album_created_at', 'album', ['created_at'])
    op.create_index('ix_album_date_start', 'album', ['date_start'])
    op.create_index('ix_album_date_end', 'album', ['date_end'])
    
    # Person table indexes
    op.create_index('ix_person_user_id', 'person', ['user_id'])
    op.create_index('ix_person_name', 'person', ['name'])
    op.create_index('ix_person_birth_year', 'person', ['birth_year'])
    
    # PhotoPerson table indexes
    op.create_index('ix_photo_people_photo_id', 'photo_people', ['photo_id'])
    op.create_index('ix_photo_people_person_id', 'photo_people', ['person_id'])
    op.create_index('ix_photo_people_manually_tagged', 'photo_people', ['manually_tagged'])
    op.create_index('ix_photo_people_verified', 'photo_people', ['verified'])
    
    # Add PostgreSQL-specific optimizations
    try:
        # Enable extension for better text search (if admin privileges allow)
        op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
        
        # Add text search indexes for photo descriptions and tags
        op.create_index(
            'ix_photo_description_gin', 'photo', 
            [sa.text('description gin_trgm_ops')], 
            postgresql_using='gin'
        )
        op.create_index(
            'ix_photo_tags_gin', 'photo', 
            [sa.text('tags gin_trgm_ops')], 
            postgresql_using='gin'
        )
        
        # Add text search for person names
        op.create_index(
            'ix_person_name_gin', 'person', 
            [sa.text('name gin_trgm_ops')], 
            postgresql_using='gin'
        )
        
    except Exception as e:
        # If extensions fail (insufficient privileges), continue without them
        print(f"Warning: Could not create GIN indexes: {e}")
    
    # Add constraints for data integrity
    op.create_check_constraint(
        'ck_photo_dimensions_positive',
        'photo',
        'width > 0 AND height > 0'
    )
    
    op.create_check_constraint(
        'ck_photo_file_size_positive',
        'photo',
        'file_size > 0'
    )
    
    op.create_check_constraint(
        'ck_person_birth_year_reasonable',
        'person',
        'birth_year IS NULL OR (birth_year >= 1800 AND birth_year <= 2100)'
    )
    
    op.create_check_constraint(
        'ck_album_date_order',
        'album',
        'date_start IS NULL OR date_end IS NULL OR date_start <= date_end'
    )
    
    # Add comment for Supabase RLS (Row Level Security) preparation
    op.execute("""
        COMMENT ON TABLE "user" IS 'PhotoVault users - RLS enabled for tenant isolation';
        COMMENT ON TABLE photo IS 'User photos with metadata - RLS by user_id';
        COMMENT ON TABLE album IS 'Photo albums - RLS by user_id';
        COMMENT ON TABLE person IS 'People for photo tagging - RLS by user_id';
        COMMENT ON TABLE photo_people IS 'Photo-person associations - RLS via photo.user_id';
    """)


def downgrade():
    # Remove constraints
    try:
        op.drop_constraint('ck_album_date_order', 'album')
        op.drop_constraint('ck_person_birth_year_reasonable', 'person')
        op.drop_constraint('ck_photo_file_size_positive', 'photo')
        op.drop_constraint('ck_photo_dimensions_positive', 'photo')
    except:
        pass
    
    # Remove GIN indexes
    try:
        op.drop_index('ix_person_name_gin', 'person')
        op.drop_index('ix_photo_tags_gin', 'photo')
        op.drop_index('ix_photo_description_gin', 'photo')
    except:
        pass
    
    # Remove regular indexes
    op.drop_index('ix_photo_people_verified', 'photo_people')
    op.drop_index('ix_photo_people_manually_tagged', 'photo_people')
    op.drop_index('ix_photo_people_person_id', 'photo_people')
    op.drop_index('ix_photo_people_photo_id', 'photo_people')
    
    op.drop_index('ix_person_birth_year', 'person')
    op.drop_index('ix_person_name', 'person')
    op.drop_index('ix_person_user_id', 'person')
    
    op.drop_index('ix_album_date_end', 'album')
    op.drop_index('ix_album_date_start', 'album')
    op.drop_index('ix_album_created_at', 'album')
    op.drop_index('ix_album_user_id', 'album')
    
    op.drop_index('ix_photo_photo_date', 'photo')
    op.drop_index('ix_photo_album_id', 'photo')
    op.drop_index('ix_photo_uploaded_at', 'photo')
    op.drop_index('ix_photo_user_id', 'photo')
    
    op.drop_index('ix_user_is_superuser', 'user')
    op.drop_index('ix_user_is_admin', 'user')
    op.drop_index('ix_user_created_at', 'user')
    op.drop_index('ix_user_username', 'user')
    op.drop_index('ix_user_email', 'user')