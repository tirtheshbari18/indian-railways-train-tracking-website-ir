"""initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-16 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=20), server_default='passenger', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Stations table
    op.create_table(
        'stations',
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('division', sa.String(length=50), nullable=True),
        sa.Column('zone', sa.String(length=20), nullable=True),
        sa.Column('state', sa.String(length=50), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('platforms_count', sa.Integer(), server_default='1', nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('code')
    )
    op.create_index(op.f('ix_stations_code'), 'stations', ['code'], unique=False)
    op.create_index(op.f('ix_stations_name'), 'stations', ['name'], unique=False)
    op.create_index(op.f('ix_stations_zone'), 'stations', ['zone'], unique=False)

    # Trains table
    op.create_table(
        'trains',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('train_number', sa.String(length=10), nullable=False),
        sa.Column('train_name', sa.String(length=150), nullable=False),
        sa.Column('train_type', sa.String(length=50), server_default='Superfast', nullable=False),
        sa.Column('source_station_code', sa.String(length=10), nullable=False),
        sa.Column('destination_station_code', sa.String(length=10), nullable=False),
        sa.Column('running_days', sa.String(length=20), server_default='1111111', nullable=False),
        sa.Column('total_distance_km', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('duration_minutes', sa.Integer(), server_default='0', nullable=False),
        sa.Column('classes', sa.JSON(), nullable=True),
        sa.Column('pantry_car', sa.Boolean(), server_default='true', nullable=True),
        sa.Column('return_train_number', sa.String(length=10), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['destination_station_code'], ['stations.code'], ),
        sa.ForeignKeyConstraint(['source_station_code'], ['stations.code'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trains_id'), 'trains', ['id'], unique=False)
    op.create_index(op.f('ix_trains_train_name'), 'trains', ['train_name'], unique=False)
    op.create_index(op.f('ix_trains_train_number'), 'trains', ['train_number'], unique=True)
    op.create_index(op.f('ix_trains_source_station_code'), 'trains', ['source_station_code'], unique=False)
    op.create_index(op.f('ix_trains_destination_station_code'), 'trains', ['destination_station_code'], unique=False)

    # Stops table
    op.create_table(
        'stops',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('train_id', sa.Integer(), nullable=False),
        sa.Column('station_code', sa.String(length=10), nullable=False),
        sa.Column('stop_sequence', sa.Integer(), nullable=False),
        sa.Column('arrival_time', sa.String(length=10), nullable=True),
        sa.Column('departure_time', sa.String(length=10), nullable=True),
        sa.Column('halt_minutes', sa.Integer(), server_default='0', nullable=True),
        sa.Column('distance_km', sa.Float(), server_default='0.0', nullable=True),
        sa.Column('day_number', sa.Integer(), server_default='1', nullable=True),
        sa.Column('platform', sa.String(length=10), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['station_code'], ['stations.code'], ),
        sa.ForeignKeyConstraint(['train_id'], ['trains.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('train_id', 'stop_sequence', name='uq_train_stop_sequence')
    )
    op.create_index(op.f('ix_stops_id'), 'stops', ['id'], unique=False)
    op.create_index(op.f('ix_stops_station_code'), 'stops', ['station_code'], unique=False)
    op.create_index(op.f('ix_stops_train_id'), 'stops', ['train_id'], unique=False)

    # Service alerts table
    op.create_table(
        'service_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('alert_type', sa.String(length=50), server_default='maintenance', nullable=False),
        sa.Column('severity', sa.String(length=20), server_default='warning', nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('affected_train_numbers', sa.JSON(), nullable=True),
        sa.Column('affected_station_codes', sa.JSON(), nullable=True),
        sa.Column('active_from', sa.DateTime(), nullable=False),
        sa.Column('active_to', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_service_alerts_id'), 'service_alerts', ['id'], unique=False)

    # Audit logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('username', sa.String(length=50), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.String(length=50), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_audit_logs_created_at'), 'audit_logs', ['created_at'], unique=False)
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)

    # Saved trains table
    op.create_table(
        'saved_trains',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('train_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['train_id'], ['trains.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'train_id', name='uq_user_saved_train')
    )
    op.create_index(op.f('ix_saved_trains_id'), 'saved_trains', ['id'], unique=False)
    op.create_index(op.f('ix_saved_trains_user_id'), 'saved_trains', ['user_id'], unique=False)
    op.create_index(op.f('ix_saved_trains_train_id'), 'saved_trains', ['train_id'], unique=False)

def downgrade() -> None:
    op.drop_table('saved_trains')
    op.drop_table('audit_logs')
    op.drop_table('service_alerts')
    op.drop_table('stops')
    op.drop_table('trains')
    op.drop_table('stations')
    op.drop_table('users')
