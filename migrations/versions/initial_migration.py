"""initial migration

Revision ID: initial
Revises: 
Create Date: 2024-04-02 18:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Omitir la creación del tipo ENUM ya que ya existe
    # userrole = postgresql.ENUM('admin', 'user', 'chef', name='userrole')
    # userrole.create(op.get_bind(), checkfirst=True)

    # Crear la tabla users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=False), # Usar String en lugar de ENUM
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # Crear tabla ingredients
    op.create_table(
        'ingredients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('usda_id', sa.String(), nullable=True),
        sa.Column('calories_per_100g', sa.Float(), nullable=True),
        sa.Column('protein_per_100g', sa.Float(), nullable=True),
        sa.Column('carbs_per_100g', sa.Float(), nullable=True),
        sa.Column('fat_per_100g', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('usda_id')
    )
    op.create_index(op.f('ix_ingredients_category'), 'ingredients', ['category'], unique=False)
    op.create_index(op.f('ix_ingredients_name'), 'ingredients', ['name'], unique=True)
    op.create_index(op.f('ix_ingredients_usda_id'), 'ingredients', ['usda_id'], unique=True)
    
    # Crear tabla recipes
    op.create_table(
        'recipes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('instructions', sa.Text(), nullable=False),
        sa.Column('preparation_time', sa.Integer(), nullable=True),
        sa.Column('cooking_time', sa.Integer(), nullable=True),
        sa.Column('servings', sa.Integer(), nullable=True),
        sa.Column('difficulty', sa.String(), nullable=True),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recipes_name'), 'recipes', ['name'], unique=False)
    
    # Crear tabla recipe_ingredients
    op.create_table(
        'recipe_ingredients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('recipe_id', sa.Integer(), nullable=False),
        sa.Column('ingredient_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(), nullable=False),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ),
        sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear tabla user_preferences
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('dietary_restrictions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('favorite_cuisines', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('disliked_ingredients', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('allergies', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('preferred_cooking_time', sa.Integer(), nullable=True),
        sa.Column('skill_level', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    # Crear tabla recipe_ratings
    op.create_table(
        'recipe_ratings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('recipe_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('comment', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    # Eliminar tablas en orden inverso
    op.drop_table('recipe_ratings')
    op.drop_table('user_preferences')
    op.drop_table('recipe_ingredients')
    op.drop_table('recipes')
    op.drop_table('ingredients')
    op.drop_table('users')
    
    # No eliminamos el tipo ENUM ya que podría ser usado por otras tablas
    # op.execute('DROP TYPE userrole') 