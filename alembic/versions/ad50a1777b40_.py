"""empty message

Revision ID: ad50a1777b40
Revises:
Create Date: 2024-09-13 17:48:53.071694

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ad50a1777b40"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("CREATE SCHEMA IF NOT EXISTS demarches_simplifiees")
    op.create_table(
        "dossier",
        sa.Column("date_created", sa.DateTime(), nullable=True),
        sa.Column(
            "id", sa.Integer(), nullable=False, comment="Identifiant unique du dossier."
        ),
        sa.Column(
            "archive",
            sa.Boolean(),
            nullable=True,
            comment="Indique si le dossier est archivé",
        ),
        sa.Column(
            "etat_dossier",
            sa.Enum(
                "ACCEPTE",
                "EN_CONSTRUCTION",
                "EN_INSTRUCTION",
                "REFUSE",
                "SANS_SUITE",
                name="dossieretatenum",
            ),
            nullable=True,
            comment="Etat d’avancement du dossier",
        ),
        sa.Column(
            "sous_etat_dossier",
            sa.Enum("EN_ATTENTE_DE_CORRECTION", "CORRIGE", name="dossiersousetatenum"),
            nullable=True,
            comment="Sous-état d’avancement du dossier",
        ),
        sa.Column(
            "derniere_mise_a_jour",
            sa.DateTime(),
            nullable=True,
            comment="Date de dernière mise à jour du dossier (notamment les avis, la messagerie…)",
        ),
        sa.Column(
            "date_depot",
            sa.DateTime(),
            nullable=True,
            comment="Date de dépôt du dossier",
        ),
        sa.Column(
            "date_passage_instruction",
            sa.DateTime(),
            nullable=True,
            comment="Date de passage en instruction",
        ),
        sa.Column(
            "date_derniere_correction_en_attente",
            sa.DateTime(),
            nullable=True,
            comment="Date de la dernière correction en attente",
        ),
        sa.Column(
            "date_traitement",
            sa.DateTime(),
            nullable=True,
            comment="Date de traitement par l’instructeur",
        ),
        sa.Column(
            "motivation_decision",
            sa.String(),
            nullable=True,
            comment="Motivation de la décision par l’instructeur",
        ),
        sa.Column(
            "instructeurs",
            sa.String(),
            nullable=True,
            comment="Instructeurs affectés à la démarche",
        ),
        sa.Column(
            "groupe_instructeur",
            sa.String(),
            nullable=True,
            comment="Groupe d’instructeurs affecté à la démarche",
        ),
        sa.Column(
            "adresse_email_connexion",
            sa.String(),
            nullable=True,
            comment="Email de connexion associé au compte Démarches simplifiées du déclarant",
        ),
        sa.Column(
            "civilite_declarant",
            sa.Enum("M", "Mme", name="civilite"),
            nullable=True,
            comment="Civilité du déclarant",
        ),
        sa.Column(
            "nom_declarant", sa.String(), nullable=True, comment="Nom du déclarant"
        ),
        sa.Column(
            "prenom_declarant",
            sa.String(),
            nullable=True,
            comment="Prénom du déclarant",
        ),
        sa.Column(
            "nom_mandataire", sa.String(), nullable=True, comment="Nom du mandataire"
        ),
        sa.Column(
            "prenom_mandataire",
            sa.String(),
            nullable=True,
            comment="Prénom du mandataire",
        ),
        sa.Column(
            "depot_pour_mandataire",
            sa.Boolean(),
            nullable=True,
            comment="Indique si le déclarant dépose pour un mantataire",
        ),
        sa.Column(
            "adresse_email_declarant",
            sa.String(),
            nullable=True,
            comment="Adresse email du déclarant",
        ),
        sa.Column(
            "numero_telephone_declarant",
            sa.String(),
            nullable=True,
            comment="Numéro de téléphone du déclarant",
        ),
        sa.Column(
            "statut_declarant",
            sa.String(),
            nullable=True,
            comment="Statut du déclarant (particulier ou représentant d’une structure)",
        ),
        sa.Column(
            "raison_sociale_structure",
            sa.String(),
            nullable=True,
            comment="Raison sociale de la structure",
        ),
        sa.Column(
            "type_prelevement",
            sa.Enum(
                "PRELEVEMENT_CAMION_CITERNE",
                "PRELEVEMENT_APE_ZRE",
                "PRELEVEMENT_ICPE_HORS_ZRE",
                "PRELEVEMENT_AUTRE",
                name="typeprelevementenum",
            ),
            nullable=True,
            comment="Type de prélèvement",
        ),
        sa.Column(
            "numero_arrete_aot",
            sa.String(),
            nullable=True,
            comment="Numéro de l’arrêté préfectoral d’AOT",
        ),
        sa.Column(
            "annee_prelevement_camion_citerne",
            sa.Integer(),
            nullable=True,
            comment="Pour les camions citernes, année de prélèvement (permet de définir le niveau de précision attendu dans la déclaration)",
        ),
        sa.Column(
            "mois_prelevement_camion_citerne",
            sa.String(),
            nullable=True,
            comment="En quel mois les prélèvements que vous allez déclarer ont-ils été réalisés ?",
        ),
        sa.Column(
            "prelevement_sur_periode_camion_citerne",
            sa.Boolean(),
            nullable=True,
            comment="Pour les AOT de camions citernes, indique si des prélèvements ont été réalisés sur la période concernée par la déclaration (mois précédent)",
        ),
        sa.Column(
            "declaration_plusieurs_mois_camion_citerne",
            sa.Boolean(),
            nullable=True,
            comment="Indique si la déclaration concerne plusieurs mois (seules les régularisations peuvent faire l'objet d'une déclaration portant sur plusieurs mois)",
        ),
        sa.Column(
            "mois_debut_declaration_camion_citerne",
            sa.String(),
            nullable=True,
            comment="Mois de début de déclaration pour les AOT de camions citernes",
        ),
        sa.Column(
            "mois_fin_declaration_camion_citerne",
            sa.String(),
            nullable=True,
            comment="Mois de fin de déclaration pour les AOT de camions citernes",
        ),
        sa.Column(
            "mois_declaration_camion_citerne",
            sa.String(),
            nullable=True,
            comment="Mois de déclaration pour les AOT de camions citernes",
        ),
        sa.Column(
            "volumes_pompes_tableau_suivi_camion_citerne",
            sa.Boolean(),
            nullable=True,
            comment="Indique si les volumes pompés sont renseignés dans un tableau de suivi pour les AOT de camions citernes",
        ),
        sa.Column(
            "prelevement_points_autorises_aot_2023",
            sa.Boolean(),
            nullable=True,
            comment="Avez-vous prélevé sur au moins un des points autorisés par votre AOT durant l'année 2023 ?",
        ),
        sa.Column(
            "mode_transmission_donnees_camion_citerne",
            sa.Enum(
                "TABLEAU_SUIVI", "VALEUR_PAR_VALEUR", name="typetransmissiondonneesenum"
            ),
            nullable=True,
            comment="Mode de transmission des données pour les AOT camion citerne (une à une, ou au format tableur)",
        ),
        sa.Column(
            "fichier_tableau_suivi_camion_citerne_filename",
            sa.String(),
            nullable=True,
            comment="Nom du fichier de tableau de suivi des prélèvements par camion citerne",
        ),
        sa.Column(
            "fichier_tableau_suivi_camion_citerne_url",
            sa.String(),
            nullable=True,
            comment="URL du fichier de tableau de suivi des prélèvements par camion citerne",
        ),
        sa.Column(
            "fichier_tableau_suivi_camion_citerne_object_storage",
            sa.String(),
            nullable=True,
            comment="Nom du fichier de tableau de suivi des prélèvements par camion citerne dans l'object storage",
        ),
        sa.Column(
            "details_prelevements_camion_citerne",
            sa.Boolean(),
            nullable=True,
            comment="Indique si le déclarant connait précisément les dates et volumes de prélèvement sur chaque point de prélèvement",
        ),
        sa.Column(
            "nom_point_prelevement",
            sa.String(),
            nullable=True,
            comment="Nom du point de prélèvement concerné par la déclaration",
        ),
        sa.Column(
            "date_activation_point_prelevement",
            sa.String(),
            nullable=True,
            comment="Date d'activation du point de prélèvement",
        ),
        sa.Column(
            "prelevement_sur_periode_aot_agricole",
            sa.Boolean(),
            nullable=True,
            comment="Indique si des prélèvements ont été réalisés sur la période concernée par la déclaration (mois précédent)",
        ),
        sa.Column(
            "donnees_compteur_volumetrique",
            sa.Boolean(),
            nullable=True,
            comment="Indique sur les données sont issues d’un compteur volumétrique (pour les AOT agricoles)",
        ),
        sa.Column(
            "panne_compteur",
            sa.Boolean(),
            nullable=True,
            comment="Indique si une panne ou un changement de compteur est déclarée (pour les AOT agricoles)",
        ),
        sa.Column(
            "index_avant_la_panne_ou_changement_de_compteur",
            sa.Float(),
            nullable=True,
            comment="Index avant la panne ou le changement de compteur (pour les AOT agricoles)",
        ),
        sa.Column(
            "index_apres_la_panne_ou_changement_de_compteur",
            sa.Float(),
            nullable=True,
            comment="Index après la réparation ou le changement de compteur (pour les AOT agricoles)",
        ),
        sa.Column(
            "numero_serie_compteur",
            sa.String(),
            nullable=True,
            comment="Numéro de série du compteur (pour les AOT agricoles)",
        ),
        sa.Column(
            "compteur_lecture_directe",
            sa.Boolean(),
            nullable=True,
            comment="Indique s’il s’agit d’un compteur à lecture directe (pour les AOT agricoles)",
        ),
        sa.Column(
            "coefficient_multiplicateur_compteur",
            sa.String(),
            nullable=True,
            comment="Coefficient multiplicateur du compteur (pour les AOT agricoles)",
        ),
        sa.Column(
            "commentaire",
            sa.String(),
            nullable=True,
            comment="Commentaire libre du déclarant sur la déclaration",
        ),
        sa.Column(
            "note_facilite_utilisation",
            sa.String(),
            nullable=True,
            comment="Donnez une note sur la facilité de prise en main de l’outil démarches simplifiées",
        ),
        sa.Column(
            "remarque_note",
            sa.String(),
            nullable=True,
            comment="Souhaitez-vous apporter une remarque à cette note ?",
        ),
        sa.Column(
            "temps_remplissage_questionnaire",
            sa.String(),
            nullable=True,
            comment="Combien de temps avez-vous passé à remplir ce questionnaire ?",
        ),
        sa.Column(
            "amelioration_temps_remplissage",
            sa.String(),
            nullable=True,
            comment="Avez-vous une idée ce que qui pourrait être amélioré pour réduire ce temps ?",
        ),
        sa.Column(
            "temps_formatage_donnees",
            sa.String(),
            nullable=True,
            comment="Combien de temps avez-vous passé au formatage des données (utilisation du modèle de tableur imposé) ?",
        ),
        sa.Column(
            "declarant_demarche_simplifiee",
            sa.String(),
            nullable=True,
            comment="Qui est la personne qui a fait la déclaration sur Démarches Simplifiées ?",
        ),
        sa.Column(
            "televerseur_tableur_brutes",
            sa.String(),
            nullable=True,
            comment="Qui est la personne qui a téléversé le tableur de données brutes dans l’outil Démarches Simplifiées ?",
        ),
        sa.Column(
            "acces_formulaire",
            sa.String(),
            nullable=True,
            comment="Comment cette personne a-t-elle eu accès au formulaire ?",
        ),
        sa.Column(
            "raison_non_declaration_preleveur",
            sa.String(),
            nullable=True,
            comment="Pour quelles raisons la personne en charge du prélèvement n'a-t-elle pas pu faire la déclaration elle-même ?",
        ),
        sa.Column(
            "rappel_obligation_mensuelle_declaration",
            sa.Boolean(),
            nullable=True,
            comment="Souhaiteriez-vous recevoir le 1er de chaque mois un mail vous rappelant l'obligation mensuelle de déclaration ?",
        ),
        sa.Column(
            "demande_documentation",
            sa.String(),
            nullable=True,
            comment="Souhaiteriez-vous disposer d’une documentation sur le remplissage de ce formulaire et la façon de remplir le modèle de tableau de données ?",
        ),
        sa.Column(
            "amelioration_documentation",
            sa.String(),
            nullable=True,
            comment="Sous quelle forme une documentation d’utilisation vous semble la plus utile ?",
        ),
        sa.Column(
            "suggestion_informations_visualisation",
            sa.String(),
            nullable=True,
            comment="Si vous le souhaitez, vous pouvez nous faire part des informations que vous aimeriez voir figurer dans cet outil de visualisation de données, et qui pourraient vous être utiles pour mieux suivre vos prélèvements au fil du temps.",
        ),
        sa.Column(
            "acceptation_contact_deal",
            sa.Boolean(),
            nullable=True,
            comment="Accepteriez-vous d’être recontacté.e par la DEAL pour échanger davantage sur le sujet ?",
        ),
        sa.Column(
            "validation_informations",
            sa.Boolean(),
            nullable=True,
            comment="Déclaration par le préleveur que les informations sont exactes",
        ),
        sa.Column(
            "date_debut_periode_declaree",
            sa.DateTime(),
            nullable=True,
            comment="Date du début de la période concernée par la déclaration",
        ),
        sa.Column(
            "date_fin_periode_declaree",
            sa.DateTime(),
            nullable=True,
            comment="Date de fin de la période concernée par la déclaration",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="demarches_simplifiees",
    )
    op.create_index(
        op.f("ix_demarches_simplifiees_dossier_date_created"),
        "dossier",
        ["date_created"],
        unique=False,
        schema="demarches_simplifiees",
    )
    op.create_table(
        "error_mail",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("date_created", sa.DateTime(), nullable=True),
        sa.Column(
            "id_dossier",
            sa.Integer(),
            nullable=True,
            comment="Identifiant unique du dossier.",
        ),
        sa.Column(
            "email", sa.String(), nullable=True, comment="Adresse email du déclarant"
        ),
        sa.Column("message", sa.String(), nullable=True, comment="Message d'erreur"),
        sa.PrimaryKeyConstraint("id"),
        schema="demarches_simplifiees",
    )
    op.create_index(
        op.f("ix_demarches_simplifiees_error_mail_date_created"),
        "error_mail",
        ["date_created"],
        unique=False,
        schema="demarches_simplifiees",
    )
    op.create_index(
        op.f("ix_demarches_simplifiees_error_mail_id_dossier"),
        "error_mail",
        ["id_dossier"],
        unique=False,
        schema="demarches_simplifiees",
    )
    op.create_table(
        "avis",
        sa.Column("date_created", sa.DateTime(), nullable=True),
        sa.Column(
            "id", sa.Integer(), nullable=False, comment="Identifiant unique de l'avis"
        ),
        sa.Column("question", sa.String(), nullable=True, comment="Question de l'avis"),
        sa.Column(
            "reponse",
            sa.String(),
            nullable=True,
            comment="Réponse à la question de l'avis",
        ),
        sa.Column(
            "date_question", sa.DateTime(), nullable=True, comment="Date de la question"
        ),
        sa.Column(
            "date_reponse", sa.DateTime(), nullable=True, comment="Date de la réponse"
        ),
        sa.Column(
            "email_claimant", sa.String(), nullable=True, comment="Email du demandeur"
        ),
        sa.Column(
            "email_expert", sa.String(), nullable=True, comment="Email de l'expert"
        ),
        sa.Column(
            "id_dossier", sa.Integer(), nullable=True, comment="Identifiant du dossier"
        ),
        sa.ForeignKeyConstraint(
            ["id_dossier"], ["demarches_simplifiees.dossier.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="demarches_simplifiees",
    )
    op.create_index(
        op.f("ix_demarches_simplifiees_avis_date_created"),
        "avis",
        ["date_created"],
        unique=False,
        schema="demarches_simplifiees",
    )
    op.create_table(
        "donnees_point_de_prelevement_aep_zre",
        sa.Column("date_created", sa.DateTime(), nullable=True),
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
            comment="Identifiant unique du prélèvement",
        ),
        sa.Column(
            "nom_point_prelevement",
            sa.String(),
            nullable=True,
            comment="Nom du point de prélèvement",
        ),
        sa.Column(
            "prelevement_realise",
            sa.Boolean(),
            nullable=True,
            comment="Indique si un prélèvement a été réalisé",
        ),
        sa.Column(
            "ligne",
            sa.Integer(),
            nullable=True,
            comment="Ordre dans lequel l’index a été déclaré pour une même déclaration",
        ),
        sa.Column(
            "fichier_prelevement_filename",
            sa.String(),
            nullable=True,
            comment="Nom du fichier de prélèvement",
        ),
        sa.Column(
            "fichier_prelevement_url",
            sa.String(),
            nullable=True,
            comment="URL du fichier de prélèvement",
        ),
        sa.Column(
            "fichier_prelevement_object_storage",
            sa.String(),
            nullable=True,
            comment="Nom du fichier de prélèvement dans l'object storage",
        ),
        sa.Column(
            "autre_document_suivi_filename",
            sa.String(),
            nullable=True,
            comment="Nom du fichier de suivi",
        ),
        sa.Column(
            "autre_document_suivi_url",
            sa.String(),
            nullable=True,
            comment="URL du fichier de suivi",
        ),
        sa.Column(
            "autre_document_suivi_object_storage",
            sa.String(),
            nullable=True,
            comment="Nom du fichier de suivi dans l'object storage",
        ),
        sa.Column(
            "id_dossier", sa.Integer(), nullable=True, comment="Identifiant du dossier"
        ),
        sa.ForeignKeyConstraint(
            ["id_dossier"], ["demarches_simplifiees.dossier.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="demarches_simplifiees",
    )
    op.create_index(
        op.f(
            "ix_demarches_simplifiees_donnees_point_de_prelevement_aep_zre_date_created"
        ),
        "donnees_point_de_prelevement_aep_zre",
        ["date_created"],
        unique=False,
        schema="demarches_simplifiees",
    )
    op.create_table(
        "donnees_prelevement_citerne",
        sa.Column("date_created", sa.DateTime(), nullable=True),
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
            comment="Identifiant unique du prélèvement",
        ),
        sa.Column(
            "date_releve", sa.DateTime(), nullable=True, comment="Date du relevé"
        ),
        sa.Column("volume", sa.Float(), nullable=True, comment="Volume prélevé"),
        sa.Column(
            "nom_point_prelevement",
            sa.String(),
            nullable=True,
            comment="Point de prélèvement",
        ),
        sa.Column(
            "id_dossier", sa.Integer(), nullable=True, comment="Identifiant du dossier"
        ),
        sa.ForeignKeyConstraint(
            ["id_dossier"], ["demarches_simplifiees.dossier.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="demarches_simplifiees",
    )
    op.create_index(
        op.f("ix_demarches_simplifiees_donnees_prelevement_citerne_date_created"),
        "donnees_prelevement_citerne",
        ["date_created"],
        unique=False,
        schema="demarches_simplifiees",
    )
    op.create_table(
        "message",
        sa.Column("date_created", sa.DateTime(), nullable=True),
        sa.Column(
            "id", sa.Integer(), nullable=False, comment="Identifiant unique du message"
        ),
        sa.Column(
            "date_creation", sa.DateTime(), nullable=True, comment="Date du message"
        ),
        sa.Column("email", sa.String(), nullable=True, comment="Email de l'expéditeur"),
        sa.Column("body", sa.String(), nullable=True, comment="Contenu du message"),
        sa.Column(
            "id_dossier", sa.Integer(), nullable=True, comment="Identifiant du dossier"
        ),
        sa.ForeignKeyConstraint(
            ["id_dossier"], ["demarches_simplifiees.dossier.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="demarches_simplifiees",
    )
    op.create_index(
        op.f("ix_demarches_simplifiees_message_date_created"),
        "message",
        ["date_created"],
        unique=False,
        schema="demarches_simplifiees",
    )
    op.create_table(
        "prelevement_citerne_valeur_par_valeur",
        sa.Column("date_created", sa.DateTime(), nullable=True),
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
            comment="Identifiant unique du prélèvement",
        ),
        sa.Column("date", sa.DateTime(), nullable=True, comment="Date du prélèvement"),
        sa.Column("annee", sa.Integer(), nullable=True, comment="Annee du prélèvement"),
        sa.Column("valeur", sa.Float(), nullable=True, comment="Volume prélevé"),
        sa.Column(
            "nom_point_prelevement",
            sa.String(),
            nullable=True,
            comment="Point de prélèvement",
        ),
        sa.Column(
            "id_dossier", sa.Integer(), nullable=True, comment="Identifiant du dossier"
        ),
        sa.ForeignKeyConstraint(
            ["id_dossier"], ["demarches_simplifiees.dossier.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="demarches_simplifiees",
    )
    op.create_index(
        op.f(
            "ix_demarches_simplifiees_prelevement_citerne_valeur_par_valeur_date_created"
        ),
        "prelevement_citerne_valeur_par_valeur",
        ["date_created"],
        unique=False,
        schema="demarches_simplifiees",
    )
    op.create_table(
        "relever_index",
        sa.Column("date_created", sa.DateTime(), nullable=True),
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
            comment="Identifiant unique du relevé d'index",
        ),
        sa.Column(
            "date", sa.DateTime(), nullable=True, comment="Date du relevé d'index"
        ),
        sa.Column("valeur", sa.Float(), nullable=True, comment="Index relevé"),
        sa.Column(
            "id_dossier", sa.Integer(), nullable=True, comment="Identifiant du dossier"
        ),
        sa.ForeignKeyConstraint(
            ["id_dossier"], ["demarches_simplifiees.dossier.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="demarches_simplifiees",
    )
    op.create_index(
        op.f("ix_demarches_simplifiees_relever_index_date_created"),
        "relever_index",
        ["date_created"],
        unique=False,
        schema="demarches_simplifiees",
    )
    op.create_table(
        "avis_piece_jointe",
        sa.Column("date_created", sa.DateTime(), nullable=True),
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
            comment="Identifiant unique de la pièce jointe",
        ),
        sa.Column("filename", sa.String(), nullable=True, comment="Nom du fichier"),
        sa.Column("url", sa.String(), nullable=True, comment="URL du fichier"),
        sa.Column(
            "object_storage",
            sa.String(),
            nullable=True,
            comment="Nom du fichier dans l'object storage",
        ),
        sa.Column(
            "id_avis", sa.Integer(), nullable=True, comment="Identifiant de l'avis"
        ),
        sa.ForeignKeyConstraint(
            ["id_avis"], ["demarches_simplifiees.avis.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="demarches_simplifiees",
    )
    op.create_index(
        op.f("ix_demarches_simplifiees_avis_piece_jointe_date_created"),
        "avis_piece_jointe",
        ["date_created"],
        unique=False,
        schema="demarches_simplifiees",
    )
    op.create_table(
        "donnees_prelevement_aep_zre",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("date_created", sa.DateTime(), nullable=True),
        sa.Column(
            "date", sa.DateTime(), nullable=True, comment="Date et Heure du relevé"
        ),
        sa.Column("valeur", sa.Float(), nullable=True, comment="Valeur du relevé"),
        sa.Column(
            "nom_parametre", sa.String(), nullable=True, comment="Nom du paramètre"
        ),
        sa.Column("type", sa.String(), nullable=True, comment="Type de relevé"),
        sa.Column(
            "frequence", sa.String(), nullable=True, comment="Fréquence de relevé"
        ),
        sa.Column("unite", sa.String(), nullable=True, comment="Unité de relevé"),
        sa.Column(
            "detail_point_suivi",
            sa.String(),
            nullable=True,
            comment="Détail du point de suivi",
        ),
        sa.Column(
            "profondeur",
            sa.Float(),
            nullable=True,
            comment="Profondeur du point de suivi",
        ),
        sa.Column(
            "date_debut",
            sa.DateTime(),
            nullable=True,
            comment="Date de début de relevé",
        ),
        sa.Column(
            "date_fin", sa.DateTime(), nullable=True, comment="Date de fin de relevé"
        ),
        sa.Column(
            "remarque", sa.String(), nullable=True, comment="Remarque sur le relevé"
        ),
        sa.Column(
            "remarque_serie_donnees",
            sa.String(),
            nullable=True,
            comment="Remarque sur la série de données",
        ),
        sa.Column(
            "nom_point_prelevement",
            sa.String(),
            nullable=True,
            comment="Nom du point de prélèvement",
        ),
        sa.Column(
            "nom_point_de_prelevement_associe",
            sa.String(),
            nullable=True,
            comment="Nom du point de prélèvement associé",
        ),
        sa.Column(
            "remarque_fonctionnement_point_de_prelevement",
            sa.String(),
            nullable=True,
            comment="Remarque sur le fonctionnement du point de prélèvement",
        ),
        sa.Column(
            "donnees_point_de_prelevement_aep_zre_id",
            sa.Integer(),
            nullable=True,
            comment="Identifiant du point de prélèvement",
        ),
        sa.ForeignKeyConstraint(
            ["donnees_point_de_prelevement_aep_zre_id"],
            ["demarches_simplifiees.donnees_point_de_prelevement_aep_zre.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="demarches_simplifiees",
    )
    op.create_index(
        op.f("ix_demarches_simplifiees_donnees_prelevement_aep_zre_date_created"),
        "donnees_prelevement_aep_zre",
        ["date_created"],
        unique=False,
        schema="demarches_simplifiees",
    )
    op.create_table(
        "message_piece_jointe",
        sa.Column("date_created", sa.DateTime(), nullable=True),
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
            comment="Identifiant unique de la pièce jointe",
        ),
        sa.Column("filename", sa.String(), nullable=True, comment="Nom du fichier"),
        sa.Column("url", sa.String(), nullable=True, comment="URL du fichier"),
        sa.Column(
            "object_storage",
            sa.String(),
            nullable=True,
            comment="Nom du fichier dans l'object storage",
        ),
        sa.Column(
            "id_message", sa.Integer(), nullable=True, comment="Identifiant du message"
        ),
        sa.ForeignKeyConstraint(
            ["id_message"], ["demarches_simplifiees.message.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="demarches_simplifiees",
    )
    op.create_index(
        op.f("ix_demarches_simplifiees_message_piece_jointe_date_created"),
        "message_piece_jointe",
        ["date_created"],
        unique=False,
        schema="demarches_simplifiees",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_demarches_simplifiees_message_piece_jointe_date_created"),
        table_name="message_piece_jointe",
        schema="demarches_simplifiees",
    )
    op.drop_table("message_piece_jointe", schema="demarches_simplifiees")
    op.drop_index(
        op.f("ix_demarches_simplifiees_donnees_prelevement_aep_zre_date_created"),
        table_name="donnees_prelevement_aep_zre",
        schema="demarches_simplifiees",
    )
    op.drop_table("donnees_prelevement_aep_zre", schema="demarches_simplifiees")
    op.drop_index(
        op.f("ix_demarches_simplifiees_avis_piece_jointe_date_created"),
        table_name="avis_piece_jointe",
        schema="demarches_simplifiees",
    )
    op.drop_table("avis_piece_jointe", schema="demarches_simplifiees")
    op.drop_index(
        op.f("ix_demarches_simplifiees_relever_index_date_created"),
        table_name="relever_index",
        schema="demarches_simplifiees",
    )
    op.drop_table("relever_index", schema="demarches_simplifiees")
    op.drop_index(
        op.f(
            "ix_demarches_simplifiees_prelevement_citerne_valeur_par_valeur_date_created"
        ),
        table_name="prelevement_citerne_valeur_par_valeur",
        schema="demarches_simplifiees",
    )
    op.drop_table(
        "prelevement_citerne_valeur_par_valeur", schema="demarches_simplifiees"
    )
    op.drop_index(
        op.f("ix_demarches_simplifiees_message_date_created"),
        table_name="message",
        schema="demarches_simplifiees",
    )
    op.drop_table("message", schema="demarches_simplifiees")
    op.drop_index(
        op.f("ix_demarches_simplifiees_donnees_prelevement_citerne_date_created"),
        table_name="donnees_prelevement_citerne",
        schema="demarches_simplifiees",
    )
    op.drop_table("donnees_prelevement_citerne", schema="demarches_simplifiees")
    op.drop_index(
        op.f(
            "ix_demarches_simplifiees_donnees_point_de_prelevement_aep_zre_date_created"
        ),
        table_name="donnees_point_de_prelevement_aep_zre",
        schema="demarches_simplifiees",
    )
    op.drop_table(
        "donnees_point_de_prelevement_aep_zre", schema="demarches_simplifiees"
    )
    op.drop_index(
        op.f("ix_demarches_simplifiees_avis_date_created"),
        table_name="avis",
        schema="demarches_simplifiees",
    )
    op.drop_table("avis", schema="demarches_simplifiees")
    op.drop_index(
        op.f("ix_demarches_simplifiees_error_mail_id_dossier"),
        table_name="error_mail",
        schema="demarches_simplifiees",
    )
    op.drop_index(
        op.f("ix_demarches_simplifiees_error_mail_date_created"),
        table_name="error_mail",
        schema="demarches_simplifiees",
    )
    op.drop_table("error_mail", schema="demarches_simplifiees")
    op.drop_index(
        op.f("ix_demarches_simplifiees_dossier_date_created"),
        table_name="dossier",
        schema="demarches_simplifiees",
    )
    op.drop_table("dossier", schema="demarches_simplifiees")
    # ### end Alembic commands ###
