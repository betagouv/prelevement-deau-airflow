"""empty message

Revision ID: a5b6baf1d3f6
Revises: d63fdf68a0af
Create Date: 2024-05-16 05:00:05.367345

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a5b6baf1d3f6'
down_revision: Union[str, None] = 'd63fdf68a0af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('donnees_point_de_prelevement',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.Column('dossier_id', sa.Integer(), nullable=True),
    sa.Column('demarche_data_brute_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('ligne', sa.Integer(), nullable=True),
    sa.Column('point_prelevement', sa.String(), nullable=True),
    sa.Column('donnees_standardisees', sa.String(), nullable=True),
    sa.Column('autres_documents', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['demarche_data_brute_id'], ['demarche_data_brute.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_donnees_point_de_prelevement_date_created'), 'donnees_point_de_prelevement', ['date_created'], unique=False)
    op.create_table('extrait_de_registre',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.Column('dossier_id', sa.Integer(), nullable=True),
    sa.Column('demarche_data_brute_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('ligne', sa.Integer(), nullable=True),
    sa.Column('extrait_registre', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['demarche_data_brute_id'], ['demarche_data_brute.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_extrait_de_registre_date_created'), 'extrait_de_registre', ['date_created'], unique=False)
    op.create_table('preprocessed_dossier',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.Column('number', sa.Integer(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('civilite', sa.String(), nullable=True),
    sa.Column('nom', sa.String(), nullable=True),
    sa.Column('prenom', sa.String(), nullable=True),
    sa.Column('deposeParUnTiers', sa.Boolean(), nullable=True),
    sa.Column('nomMandataire', sa.String(), nullable=True),
    sa.Column('prenomMandataire', sa.String(), nullable=True),
    sa.Column('archived', sa.Boolean(), nullable=True),
    sa.Column('state', sa.String(), nullable=True),
    sa.Column('dateDerniereModification', sa.DateTime(), nullable=True),
    sa.Column('dateDepot', sa.DateTime(), nullable=True),
    sa.Column('datePassageEnInstruction', sa.DateTime(), nullable=True),
    sa.Column('dateTraitement', sa.DateTime(), nullable=True),
    sa.Column('motivation', sa.String(), nullable=True),
    sa.Column('instructeurs', sa.String(), nullable=True),
    sa.Column('groupe_instructeur', sa.String(), nullable=True),
    sa.Column('coordonnees', sa.String(), nullable=True),
    sa.Column('adresse_email', sa.String(), nullable=True),
    sa.Column('numero_telephone', sa.String(), nullable=True),
    sa.Column('statut_declarant', sa.String(), nullable=True),
    sa.Column('raison_sociale_structure', sa.String(), nullable=True),
    sa.Column('point_prelevement_eau', sa.String(), nullable=True),
    sa.Column('type_prelevement', sa.String(), nullable=True),
    sa.Column('numero_arrete_aot', sa.String(), nullable=True),
    sa.Column('prelevement_citerne', sa.String(), nullable=True),
    sa.Column('volume_preleve', sa.String(), nullable=True),
    sa.Column('mode_transmission_donnees', sa.String(), nullable=True),
    sa.Column('volumes_pompes_jour', sa.String(), nullable=True),
    sa.Column('copie_registre_papier', sa.String(), nullable=True),
    sa.Column('conclusion', sa.String(), nullable=True),
    sa.Column('commentaire', sa.String(), nullable=True),
    sa.Column('volumes_annuels_pompes', sa.String(), nullable=True),
    sa.Column('transmission_extrait_numerique_registre', sa.String(), nullable=True),
    sa.Column('declaration_point_prelevement', sa.String(), nullable=True),
    sa.Column('date_activation_point_prelevement', sa.String(), nullable=True),
    sa.Column('type_autre_prelevement', sa.String(), nullable=True),
    sa.Column('releve_index_compteur', sa.String(), nullable=True),
    sa.Column('informations_compteur', sa.String(), nullable=True),
    sa.Column('numero_serie_compteur', sa.String(), nullable=True),
    sa.Column('prelevement_icpe', sa.String(), nullable=True),
    sa.Column('donnees_standardisees', sa.String(), nullable=True),
    sa.Column('prelevement_aep_zre', sa.String(), nullable=True),
    sa.Column('validation_informations', sa.Boolean(), nullable=True),
    sa.Column('details_prelevements', sa.Boolean(), nullable=True),
    sa.Column('donnees_compteur_volumetrique', sa.Boolean(), nullable=True),
    sa.Column('compteur_lecture_directe', sa.Boolean(), nullable=True),
    sa.Column('signalement_panne_compteur', sa.Boolean(), nullable=True),
    sa.Column('prelevement_autorise_mois_precedent', sa.Boolean(), nullable=True),
    sa.Column('au_moins_un_prelevement', sa.Boolean(), nullable=True),
    sa.Column('date_debut_declaration', sa.DateTime(), nullable=True),
    sa.Column('date_fin_declaration', sa.DateTime(), nullable=True),
    sa.Column('annee_prelevement', sa.Integer(), nullable=True),
    sa.Column('nom_point_prelevement', sa.String(), nullable=True),
    sa.Column('demarche_data_brute_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['demarche_data_brute_id'], ['demarche_data_brute.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_preprocessed_dossier_date_created'), 'preprocessed_dossier', ['date_created'], unique=False)
    op.create_index(op.f('ix_preprocessed_dossier_number'), 'preprocessed_dossier', ['number'], unique=False)
    op.create_table('releve_index',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.Column('ligne', sa.Integer(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('index', sa.Float(), nullable=True),
    sa.Column('dossier_id', sa.Integer(), nullable=True),
    sa.Column('demarche_data_brute_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['demarche_data_brute_id'], ['demarche_data_brute.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_releve_index_date_created'), 'releve_index', ['date_created'], unique=False)
    op.create_table('volumes_pompes',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.Column('dossier_id', sa.Integer(), nullable=True),
    sa.Column('demarche_data_brute_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('ligne', sa.Integer(), nullable=True),
    sa.Column('point_prelevement', sa.String(), nullable=True),
    sa.Column('annee', sa.Integer(), nullable=True),
    sa.Column('volume_pompe', sa.Float(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['demarche_data_brute_id'], ['demarche_data_brute.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_volumes_pompes_date_created'), 'volumes_pompes', ['date_created'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_volumes_pompes_date_created'), table_name='volumes_pompes')
    op.drop_table('volumes_pompes')
    op.drop_index(op.f('ix_releve_index_date_created'), table_name='releve_index')
    op.drop_table('releve_index')
    op.drop_index(op.f('ix_preprocessed_dossier_number'), table_name='preprocessed_dossier')
    op.drop_index(op.f('ix_preprocessed_dossier_date_created'), table_name='preprocessed_dossier')
    op.drop_table('preprocessed_dossier')
    op.drop_index(op.f('ix_extrait_de_registre_date_created'), table_name='extrait_de_registre')
    op.drop_table('extrait_de_registre')
    op.drop_index(op.f('ix_donnees_point_de_prelevement_date_created'), table_name='donnees_point_de_prelevement')
    op.drop_table('donnees_point_de_prelevement')
    # ### end Alembic commands ###
