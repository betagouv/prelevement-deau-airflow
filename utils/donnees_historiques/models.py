import uuid

from geoalchemy2.types import Geometry
from sqlalchemy import (
    ARRAY,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    PrimaryKeyConstraint,
    Sequence,
    String,
    Text,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import as_declarative, declared_attr


@as_declarative()
class HistoricalDBBase:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    date_created = Column(DateTime, index=True, default=func.now())


class JddAnalyse(HistoricalDBBase):
    __tablename__ = "jdd_analyse"
    __table_args__ = {"comment": "Analyse des différents jeux de données testés"}

    id = Column(
        Integer,
        Sequence("jdd_analyse_id_seq"),
        primary_key=True,
        autoincrement=True,
        nullable=False,
        comment="Identifiant auto-généré",
    )
    jdd_nom = Column(
        Text, nullable=True, comment="Nom du jeu de données (c'est-à-dire de la table)"
    )
    ordre = Column(
        Integer, nullable=True, comment="Ordre du champ dans le jeu de données"
    )
    champ = Column(Text, nullable=True, comment="Nom du champ dans le jdd")
    type = Column(Text, nullable=True, comment="Type du champ")
    nb_char = Column(Integer, nullable=True, comment="Nombre maximal de caractères")
    nb_valeurs = Column(
        Integer, nullable=True, comment="Nombre de valeurs uniques du champ"
    )
    valeurs = Column(
        JSONB, nullable=True, comment="Valeurs uniques du champ et occurences"
    )
    date = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Date à laquelle l'analyse a été réalisée",
    )


class Bss(HistoricalDBBase):
    __tablename__ = "bss"
    __table_args__ = {
        "schema": "referentiel",
        "comment": "Référentiel de la banque du sous-sol (BSS), transmise le 28/07/2022 apar le BRGM Réunion. Le fichier a été retravaillé pour les colonnes lien_infoterre et google_maps afin d"
        "avoir les URL en dur (à l"
        "enregistrement du CSV, c"
        "est la formule qui avait été enregistrée, pas la valeur)",
    }

    id_bss = Column(String, primary_key=True)
    code_bss_ancien = Column(String, unique=True)
    indice = Column(String)
    designation = Column(String)
    nom_abrege = Column(String)
    libelle = Column(String)
    lien_infoterre = Column(String)
    google_maps = Column(String)
    coupe_geologique = Column(String)
    coupe_autre = Column(String)
    log_geol_verifie = Column(String)
    nb_scans = Column(String)
    nb_scans_coupe = Column(String)
    lex_organisme = Column(String)
    lex_type_declaration = Column(String)
    point_eau = Column(String)
    lex_sgr = Column(String)
    lex_num_departement = Column(String)
    lex_nom_departement = Column(String)
    lex_num_commune = Column(String)
    lex_insee_commune = Column(String)
    lex_nom_commune = Column(String)
    lieu_dit = Column(String)
    x_saisie = Column(String)
    y_saisie = Column(String)
    lex_projection_saisie = Column(String)
    lex_unite_saisie = Column(String)
    x_ref06 = Column(String)
    y_ref06 = Column(String)
    lex_projection_ref06 = Column(String)
    lex_precision_xy = Column(String)
    lex_qual_position = Column(String)
    z_sol = Column(String)
    lex_prec_z_sol = Column(String)
    lex_mode_obtention_z = Column(String)
    z_bdalti = Column(String)
    lex_nature = Column(String)
    prof_investigation = Column(String)
    prof_accessible = Column(String)
    diametre_tubage = Column(String)
    prof_eau_sol = Column(String)
    lex_type_prof_eau_sol = Column(String)
    date_eau_sol = Column(String)
    z_origine_coupe = Column(String)
    lex_prec_z_origine_coupe = Column(String)
    date_coupe = Column(String)
    date_fin_travaux = Column(String)
    nombre_observations = Column(String)
    lex_num_carte_geol = Column(String)
    lex_nom_carte_geol = Column(String)
    coupure_huitieme = Column(String)
    lex_etat_physique = Column(String)
    lex_etat = Column(String)
    lex_execution = Column(String)
    lex_utilisation = Column(String)
    lex_recherche = Column(String)
    lex_exploitation = Column(String)
    lex_reconnaissance = Column(String)
    lex_fonction = Column(String)
    deb_fonction = Column(String)
    lex_usage = Column(String)
    deb_usage = Column(String)
    lex_gisement = Column(String)
    lex_documents = Column(String)
    reference = Column(String)
    date_dossier = Column(String)
    date_saisie = Column(String)
    date_dern_maj = Column(String)
    procede_geothermique = Column(String)
    categorie_geothermie = Column(String)
    usage_geothermie = Column(String)
    relation_aquifere = Column(String)


class Commune(HistoricalDBBase):
    __tablename__ = "commune"
    __table_args__ = (
        {
            "schema": "referentiel",
            "comment": "Table des communes, issue de la couche COMMUNE.TAB issue du référentiel ADMIN-EXPRESS_3-2 traitement du 2023-05-12  de l'IGN",
        },
    )

    code_insee = Column(Integer, primary_key=True)
    nom_commune = Column(Text)
    nom_commune_majuscule = Column(Text)
    geom = Column(Geometry("GEOMETRY"))


class Meso(HistoricalDBBase):
    __tablename__ = "meso"
    __table_args__ = (
        Index("meso_geom_gist", "geom", postgresql_using="gist"),
        {
            "schema": "referentiel",
            "comment": "Table des masses d'eau souterraines définies dans létat des lieux du SDAGE 2019, indiquant le statut ZRE de certaines d'entre elles. La table est issue de la couche SIG ME_ES.shp récupérée sur le répertoire G par VLT le 03/05/2023",
        },
    )

    wkt = Column(Text)
    geom = Column(Geometry("GEOMETRY"))
    numero = Column(Text)
    code = Column(Text, primary_key=True)
    niveau = Column(Text)
    theme_geol = Column(Text)
    nature = Column(Text)
    milieu = Column(Text)
    etat_hydro = Column(Text)
    in_10p6_m3 = Column(Text)
    infiltrati = Column(Text)
    infil_2019 = Column(Text)
    prelev2014 = Column(Text)
    ratio_p_r = Column(Text)
    taux_inf = Column(Text)
    haut_infil = Column(Text)
    lame_infil = Column(Text)
    inf_uau = Column(Text)
    classratio = Column(Text)
    test_esu = Column(Text)
    tendances = Column(Text)
    qualite_ge = Column(Text)
    test_aep = Column(Text)
    classprele = Column(Text)
    modeles = Column(Text)
    etat_quant = Column(Text)
    etat_chimi = Column(Text)
    eta_global = Column(Text)
    nom_provis = Column(Text)
    classe_zre = Column(Text)


class BvBdCarthage(HistoricalDBBase):
    __tablename__ = "bv_bdcarthage"
    __table_args__ = (
        Index("bv_bdcarthage_geom_gist", "geom", postgresql_using="gist"),
        {
            "schema": "referentiel",
            "comment": "Table des 126 bassins versants de cours d'eau de la BD Carthage,"
            + "modélisés à partir du MNT de la BD Topo. Quelques zones sont non couvertes"
            + "(petites ravines littorales, volcan, grand étang. La table est issue de la couche G:\\2_DONNEES\\F_EAU\\F9_ZONAGES_EAU\\BASSINS-VERSANTS\\bv_bdcarthage_fleuves.shp "
            + "récupérée sur le répertoire G par VLT le 03/05/2023",
        },
    )

    wkt = Column(Text)
    area = Column(Text)
    pluvio_moy = Column(Text)
    code_cours = Column(Text, primary_key=True)
    toponyme_t = Column(Text)
    geom = Column(Geometry("GEOMETRY"))


class MeContinentalesBV(HistoricalDBBase):
    __tablename__ = "me_continentales_bv"
    __table_args__ = (
        Index("me_continentales_bv_geom_gist", "geom", postgresql_using="gist"),
        {
            "schema": "referentiel",
            "comment": "Table des bassins versants des masses d'eau continentales : La couche comporte 33 polygones (24 ME cours d'eau + 3 ME plans d'eau + 6 étangs/ravines). "
            + "La table est issue de la couche BV_ME_Continentale.tab fournie le 13/12/2022 par l'office de l'eau (Alexandre Moullama, qui la tenait lui-même du BE ayant réalisé le schéma départemental d'assainissement), puis importée dans la BDD par VLT le 03/05/2023",
        },
    )

    wkt = Column(Text)
    code_dce = Column(Text, primary_key=True)
    nom = Column(Text)
    type_mil = Column(Text)
    intitule = Column(Text)
    sensi_env = Column(Text)
    sensi_sani = Column(Text)
    surf_bv = Column(Text)
    action203 = Column(Text)
    action2021 = Column(Text)
    geom = Column(Geometry("GEOMETRY"))


class Nomenclature(HistoricalDBBase):
    __tablename__ = "nomenclature"
    __table_args__ = (
        UniqueConstraint("variable", "valeur", name="unique_variable_valeur"),
        {
            "schema": "referentiel",
            "comment": "Table stockant de manière générique les valeurs possibles pour les champs dont le vocabulaire est contrôlé",
        },
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    thematique = Column(Text)
    variable = Column(Text)
    valeur = Column(Text)
    definition = Column(Text)


class OuvrageBNPE(HistoricalDBBase):
    __tablename__ = "ouvrage_bnpe"
    __table_args__ = {
        "schema": "bnpe",
        "comment": "Table des ouvrages de prélèvements téléchargée par la DEAL (Valentin Le Tellier) depuis l'API de la BNPE le 30/11/2023 via "
        + "l'URL https://hubeau.eaufrance.fr/api/v1/prelevements/referentiel/ouvrages.csv?code_departement=974. Un ouvrage peut correspondre à 1 ou plusieurs points de prélèvements",
    }

    code_ouvrage = Column(Text, primary_key=True)
    nom_ouvrage = Column(Text)
    id_local_ouvrage = Column(Text)
    date_exploitation_debut = Column(Text)
    date_exploitation_fin = Column(Text)
    code_precision_coord = Column(Text)
    libelle_precision_coord = Column(Text)
    commentaire = Column(Text)
    code_commune_insee = Column(Text)
    nom_commune = Column(Text)
    code_departement = Column(Text)
    libelle_departement = Column(Text)
    code_type_milieu = Column(Text)
    libelle_type_milieu = Column(Text)
    code_entite_hydro_cours_eau = Column(Text)
    uri_entite_hydro_cours_eau = Column(Text)
    code_entite_hydro_plan_eau = Column(Text)
    uri_entite_hydro_plan_eau = Column(Text)
    code_mer_ocean = Column(Text)
    ressource_cont_non_referencee = Column(Text)
    ressource_cont_non_referencee_info = Column(Text)
    code_point_referent = Column(Text)
    code_bdlisa = Column(Text)
    uri_bdlisa = Column(Text)
    longitude = Column(Text)
    latitude = Column(Text)
    uri_ouvrage = Column(Text)


class PointPrelevementBNPE(HistoricalDBBase):
    __tablename__ = "point_prelevement_bnpe"
    __table_args__ = {
        "schema": "bnpe",
        "comment": "Table des points de prélèvements téléchargée par la DEAL (Valentin Le Tellier) depuis l'API de la BNPE le 30/11/2023 via "
        + "l'URL https://hubeau.eaufrance.fr/api/v1/prelevements/referentiel/points_prelevement.csv?code_departement=974. Un point de prélèvement est associé à un unique ouvrage de prélèvement",
    }

    code_point_prelevement = Column(Text, primary_key=True)
    nom_point_prelevement = Column(Text)
    date_exploitation_debut = Column(Text)
    date_exploitation_fin = Column(Text)
    code_type_milieu = Column(Text)
    libelle_type_milieu = Column(Text)
    code_nature = Column(Text)
    libelle_nature = Column(Text)
    lieu_dit = Column(Text)
    commentaire = Column(Text)
    code_commune_insee = Column(Text)
    nom_commune = Column(Text)
    code_departement = Column(Text)
    libelle_departement = Column(Text)
    code_entite_hydro_cours_eau = Column(Text)
    uri_entite_hydro_cours_eau = Column(Text)
    code_entite_hydro_plan_eau = Column(Text)
    uri_entite_hydro_plan_eau = Column(Text)
    code_zone_hydro = Column(Text)
    uri_zone_hydro = Column(Text)
    code_mer_ocean = Column(Text)
    nappe_accompagnement = Column(Text)
    uri_bss_point_eau = Column(Text)
    code_ouvrage = Column(Text)
    uri_ouvrage = Column(Text)


class PrelevementBNPE(HistoricalDBBase):
    __tablename__ = "prelevement_bnpe"
    __table_args__ = (
        PrimaryKeyConstraint(
            "code_sandre_ouvrage",
            "annee",
            "code_usage_bnpe",
            "mode_obtention_volume",
            "debut",
            "fin",
            "volume_m3",
            name="pk_prelevement_bnpe",
        ),
        {
            "schema": "bnpe",
            "comment": "Détail des prélèvements en eau 2012-2021 issus de la BNPE (export grand public le 30/11/2023 depuis la page https://bnpe.eaufrance.fr/acces-donnees). Les données de volumes annuels prélevés sont rattachées aux ouvrages et non aux points de prélèvement.",
        },
    )

    annee = Column(
        Text, comment="Année sur laquelle le prélèvement en eau a été réalisé."
    )
    code_sandre_ouvrage = Column(
        Text,
        comment="Identifiant unique national diffusé par le Sandre. Le code est constitué de 13 caractères et commence par « OPR ».",
    )
    nom_ouvrage = Column(
        Text,
        comment="Nom attribué à un ouvrage de prélèvement. Ce nom n’est pas obligatoire et ne suit pas de règle de nommage particulière.",
    )
    commentaire = Column(
        Text,
        comment="Texte libre pour tout complément d'information non prévu dans le format d'échange",
    )
    code_alternatif_ouvrage = Column(
        Text,
        comment="Identifiant local de l’ouvrage de prélèvement, interne à l’organisme qui gère cet ouvrage (agences de l’eau, office de l’eau ou DEAL Mayotte). Ce code est pérenne dans le temps.",
    )
    origine_code_alternatif = Column(
        Text,
        comment="Organisme qui gère le code alternatif. La liste des valeurs possibles est définie dans la nomenclature Sandre n°820 : http://id.eaufrance.fr/nsa/820",
    )
    departement = Column(
        Text,
        comment="Code INSEE du département où est localisé l’ouvrage de prélèvement (2 ou 3 caractères)",
    )
    code_insee = Column(
        Text,
        comment="Code INSEE de la commune où est situé l’ouvrage dans le référentiel communal en vigueur (http://www.insee.fr/fr/methodes/nomenclatures/cog/ )",
    )
    commune = Column(
        Text,
        comment="Nom de la commune où est situé l’ouvrage dans le référentiel communal en vigueur (http://www.insee.fr/fr/methodes/nomenclatures/cog/)",
    )
    code_insee_declare = Column(
        Text,
        comment="Code INSEE déclaré. Code INSEE de la commune transmis par le préleveur sur un référentiel potentiellement déprécié et non identifié.",
    )
    lieu_dit = Column(
        Text,
        comment="Lieu-dit ou toponyme précisant la localisation du point de prélèvement. Texte libre.",
    )
    debut = Column(
        Text,
        comment="Date de début de période du prélèvement. Format jj/mm/aaaa. Remarque : le prélèvement a pu potentiellement être réalisé sur une période plus petite que celle indiquée.",
    )
    fin = Column(
        Text,
        comment="Date de fin de période du prélèvement. Format jj/mm/aaaa. Remarque : le prélèvement a pu potentiellement être réalisé sur une période plus petite que celle indiquée.",
    )
    volume_m3 = Column(
        Text, comment="Volume d’eau prélevé en mètre cube. Format : entier."
    )
    code_usage_bnpe = Column(
        Text,
        comment="Code de l’usage « redevance » pour lequel le volume d’eau a été prélevé. AEP : eau potable, BAR : barrage (eau turbinée), CAN : canaux, "
        + "ENE : production d’énergie, EXO : usages exonéré de redevance, IND : industries et autres activités économiques (hors BAR, ENE et IRR), IRR : irrigation.",
    )
    libelle_usage_bnpe = Column(
        Text,
        comment="Libellé de l’usage « redevance » pour lequel le volume d’eau a été prélevé. AEP : eau potable, BAR : barrage (eau turbinée), CAN : canaux, ENE : production d’énergie, "
        + "EXO : usages exonéré de redevance, IND : industries et autres activités économiques (hors BAR, ENE et IRR), IRR : irrigation.",
    )
    code_usage_declare = Column(
        Text,
        comment="Code de l’usage déclaré. Code de l’usage tel que déclaré par le préleveur et qui suit la nomenclature Sandre 481 (http://id.eaufrance.fr/nsa/481). "
        + "On remarque que le code peut être de niveau 1. Exemple 5 : AEP ou de niveau 2, ce qui correspond à des sous-usages ; exemple 5A : Alimentation collective",
    )
    usage_declare = Column(
        Text,
        comment="Libellé de l’usage tel que déclaré par le préleveur et qui suit la nomenclature Sandre 481.  http://id.eaufrance.fr/nsa/481",
    )
    type_eau = Column(
        Text,
        comment="Indique si l’ouvrage prélève en eau continentale de surface (CONT), souterraine (SOUT) ou en eaux de transition (LIT). Ces valeurs sont issues de la nomenclature Sandre 472 et sont les seules acceptées par la BNPE :  http://id.eaufrance.fr/nsa/472",
    )
    longitude = Column(
        Text, comment="Longitude de l’ouvrage en WGS84 (epsg : 4326, Sandre : 31)."
    )
    latitude = Column(
        Text, comment="Latitude de l’ouvrage en WGS84 (epsg : 4326, Sandre : 31)."
    )
    precision_localisation = Column(
        Text,
        comment="Code indiquant le degré de précision des coordonnées géographiques de l’ouvrage. La liste des codes relève de la nomenclature 159 administrée par le SANDRE. http://id.eaufrance.fr/nsa/159. "
        + "L’ouvrage peut être localisé au centroïde de la commune sur laquelle il est situé si sa précision n’est pas connue/transmise (code 5 et 6)",
    )
    mode_obtention_volume = Column(
        Text,
        comment='Indique comment le volume a été obtenu sur le terrain. Il est soit mesuré (par compteur par exemple) : "MED", connu par forfait "FOR", "+ \
        "calculé ou interprété (ex durée d’utilisation x puissance pompe) : "MEI" ou "EST". Plus d\'information : http://id.eaufrance.fr/nsa/473',
    )
    code_du_statut_volume_eau = Column(
        Text,
        comment="Le statut du volume d'eau permet d'indiquer si les données ont passés un contrôle de qualité. Nomenclature Sandre 609 http://id.eaufrance.fr/nsa/609.",
    )
    libelle_du_statut_volume_eau = Column(
        Text,
        comment="Libellé correspondant au code dans la nomenclature 609 http://id.eaufrance.fr/nsa/609.",
    )
    code_de_qualification_volume_eau = Column(
        Text,
        comment='Le code de qualification indique le résultat des tests de qualité. Cet attribut fonctionne avec l\'attribut précédent "statut". Nomenclature Sandre 414 http://id.eaufrance.fr/nsa/414',
    )
    libelle_qualification_volume_eau = Column(
        Text,
        comment="Libellé correspondant au code dans la nomenclature 414. http://id.eaufrance.fr/nsa/414.",
    )
    debut_exploitation_ouvrage = Column(
        Text,
        comment="Date de la mise en service de l’ouvrage (jj/mm/aaaa). Si la date est inconnue, il est indiqué 01/01/1900",
    )
    fin_exploitation_ouvrage = Column(
        Text, comment="Date de fin de service de l’ouvrage (jj/mm/aaaa)."
    )
    nature_point_prelevement = Column(
        Text,
        comment="La nature indique si la localisation de l’ouvrage est bien celle de l'accès à l'eau (code P) ou d'un autre objet éloigné (compteur) (code F) ou à la localisation incertaine (pompe mobile) (code F)  Nomenclature Sandre : http://id.eaufrance.fr/nsa/471",
    )
    code_bss = Column(
        Text,
        comment="Uniquement pour les ouvrages de type SOUT : code national du point d'eau dans la Banque National du Sous-Sol qui correspond à l’ouvrage BNPE",
    )
    code_zone_hydrographique = Column(
        Text,
        comment="Uniquement pour les ouvrages de type CONT : la zone hydrographique est définie et téléchargeable sur le site du Sandre : http://www.sandre.eaufrance.fr/atlas/srv/fre/catalog.search#/metadata/3409c9c3-9836-43be-bac3-b110c82b3a25",
    )
    nom_zone_hydrographique = Column(
        Text,
        comment="Uniquement pour les ouvrages de type CONT : la zone hydrographique est définie et téléchargeable sur le site du Sandre : http://www.sandre.eaufrance.fr/atlas/srv/fre/catalog.search#/metadata/3409c9c3-9836-43be-bac3-b110c82b3a25",
    )
    code_entite_hydrographique_cours_eau = Column(
        Text,
        comment="Uniquement pour les ouvrages de type CONT :  Le code de la ressource en eau c'est à dire de l'entité hydrographique est issu du référentiel BDCarthage (objet de type \"Cours d'eau\"). "
        + "Si le cours d'eau n'est pas référencé dans la BDCarthage, le code est celui du cours d'eau en aval du point. BDCarthage est téléchargeable du site du Sandre http://www.sandre.eaufrance.fr/atlas/srv/fre/catalog.search#/home",
    )
    code_entite_hydrographique_plan_eau = Column(
        Text,
        comment="Uniquement pour les ouvrages de type CONT :  Le code de la ressource en eau c'est à dire de l'entité hydrographique est issu du référentiel BDCarthage (objet de type \"Plan d'eau\"). "
        + "Si le plan d'eau n'est pas référencé dans la BDCarthage alors le nom du plan d’eau peut être renseigné dans l’attribut \"Information complémentaire de la ressource en eau\". "
        + "BDCarthage est téléchargeable du site du Sandre http://www.sandre.eaufrance.fr/atlas/srv/fre/catalog.search#/home",
    )
    plan_eau_non_reference = Column(
        Text,
        comment="Uniquement pour les ouvrages de type CONT :  OUI : si le plan d'eau n'est pas référencé dans le référentiel BDCarthage,  NON : s’il ne l’est pas.",
    )
    information_complementaire_ressource_en_eau = Column(
        Text,
        comment="Uniquement pour les ouvrages de type CONT :  Nom du plan d'eau non référencé dans la BDCarthage (texte libre)",
    )
    code_bdrhfv1 = Column(
        Text,
        comment="Uniquement pour les ouvrages de type SOUT :  Code de la ressource en eau souterraine dans le référentiel BDRHFV1",
    )
    libelle_entite_hydrologique_bdrhfv1 = Column(
        Text,
        comment="Uniquement pour les ouvrages de type SOUT :  Libellé correspondant au code BDHFV1 dans le référentiel",
    )
    code_bdlisa = Column(
        Text,
        comment="Uniquement pour les ouvrages de type SOUT :  Code de la ressource en eau souterraine dans le référentiel BDLisa. Le référentiel est disponible sur le site du Sandre (entité hydrogéologique)",
    )
    libelle_entite_hydrologique_bdlisa = Column(
        Text,
        comment="Uniquement pour les ouvrages de type SOUT :  Libellé correspondant au code BDLisa dans le référentiel",
    )
    code__mer = Column(
        Text,
        comment="Uniquement pour les ouvrages de type LIT :  code de la ressource en eau issu de la nomenclature 243 du Sandre mer/océan : http://id.eaufrance.fr/nsa/243",
    )
    libelle_mer = Column(
        Text,
        comment="Uniquement pour les ouvrages de type LIT :  Libellé correspondant au code de la mer/océan dans la nomenclature 243 : http://id.eaufrance.fr/nsa/243",
    )


class SerieDonneesPourImport(HistoricalDBBase):
    __tablename__ = "serie_donnees_pour_import"
    __table_args__ = {
        "schema": "donnee_brute",
        "comment": "Table stockant la liste des séries de données transmise telle quelle, pour import manuel dans la table serie_donnees",
    }

    id_serie = Column(Integer, primary_key=True, autoincrement=True)
    code_serie = Column(Text, comment="Code de la série de données")
    id_synthese_principal = Column(Integer, comment="Identifiant synthèse principal")
    nom_cite = Column(Text, comment="Nom du site")
    liste_id_synthese = Column(
        ARRAY(Text), comment="Liste des identifiants de synthèse"
    )
    nom_commune = Column(Text, comment="Nom de la commune")
    detail_point_suivi = Column(Text, comment="Détail du point de suivi")
    profondeur = Column(Integer, comment="Profondeur")
    libelle_parametre = Column(Text, comment="Libellé du paramètre")
    categorie_parametre = Column(Text, comment="Catégorie du paramètre")
    unite = Column(Text, comment="Unité")
    frequence = Column(Text, comment="Fréquence")
    traitement_donnees = Column(Text, comment="Traitement des données")
    appareil = Column(Text, comment="Appareil")
    date_debut = Column(
        Text,
        comment="Date de début de la série de données, format à affiner pour contraindre au format aaaa-mm",
    )
    date_fin = Column(
        Text, comment="Date de fin de la série de données, format à affiner"
    )
    operateur_structure = Column(Text, comment="Structure de l'opérateur")
    operateur_nom = Column(Text, comment="Nom de l'opérateur")
    operateur_prenom = Column(Text, comment="Prénom de l'opérateur")
    operateur_courriel = Column(Text, comment="Courriel de l'opérateur")
    url_deal = Column(Text, comment="URL de la DEAL")
    nom_fichier = Column(Text, comment="Nom du fichier")
    hyperlien_fichier = Column(Text, comment="Hyperlien vers le fichier")
    date_standardisation = Column(Text, comment="Date de standardisation")
    remarque = Column(Text, comment="Remarque")
    remarque_vlt = Column(Text, comment="Remarque VLT")
    date_integration_bdd = Column(Date, comment="Date d'intégration dans la BDD")
    process_import = Column(Text, comment="Processus d'import")


class ResultatSuiviPourImport(HistoricalDBBase):
    __tablename__ = "resultat_suivi_pour_import"
    __table_args__ = {
        "schema": "donnee_brute",
        "comment": "Table listant les valeurs des paramètres à proprement parler, pour chacune des séries de données transmises. Table de données brutes pour import",
    }
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    id_origine = Column(Integer, comment="Identifiant origine")
    id_serie = Column(Integer, comment="Identifiant série")
    date_debut = Column(Date, comment="Date de début")
    heure_debut = Column(Time, comment="Heure de début")
    date_fin = Column(Date, comment="Date de fin")
    heure_fin = Column(Time, comment="Heure de fin")
    type_date = Column(Text, comment="Type de date")
    valeur = Column(Text, comment="Valeur")
    usage = Column(Text, comment="Usage")
    remarque = Column(Text, comment="Remarque")
    code_serie = Column(Text, comment="Code série")
    point_prelevement = Column(Text, comment="Point de prélèvement")
    libelle_parametre = Column(Text, comment="Libellé paramètre")
    categorie_parametre = Column(Text, comment="Catégorie paramètre")
    annee = Column(Integer, comment="Année")
    date_integration_bdd = Column(Date, comment="Date d'intégration dans la BDD")


class PointPrelevement(HistoricalDBBase):
    __tablename__ = "point_prelevement"
    __table_args__ = (
        Index("point_prelevement_geom_gist", "geom", postgresql_using="gist"),
        {
            "schema": "prelevement",
            "comment": "Table listant les points de prélèvements",
        },
    )

    id_synthese = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Identifiant unique et pérenne du point de prélèvement dans la base de données régionale (clef primaire attribuée par la DEAL)",
    )
    lien_dossier_ap = Column(
        Text,
        comment="Lien vers le dossier contenant les arrêté préfectoraux, calculé automatiquement dès qu’un AP est indiqué (ne pas modifier)",
    )
    code_point_prelevement_bnpe = Column(
        Text,
        ForeignKey("bnpe.point_prelevement_bnpe.code_point_prelevement"),
        comment="Code BNPE du point de prélèvement",
    )
    nom_point_prelevement = Column(
        Text,
        comment="Nom retenu localement avec les partenaires pour le point de prélèvement, dans l’hypothèse où les noms issus des différentes sources divergent. Processus de validation locale à prévoir",
    )
    autres_noms = Column(
        Text,
        comment="Autres noms utilisés pour ce point de prélèvement dans d’autres systèmes d’information",
    )
    code_ouvrage_bnpe = Column(
        Text,
        ForeignKey("bnpe.ouvrage_bnpe.code_ouvrage"),
        comment="Identifiant unique national diffusé par le Sandre. Le code est constitué de 13 caractères et commence par « OPR ».",
    )
    id_local_ouvrage = Column(
        Text,
        comment="Identifiant local de l’ouvrage de prélèvement interne à l’organisme qui gère cet ouvrage office de l’eau pour La Réunion). Ce code est pérenne dans le temps.",
    )
    nom_ouvrage_bnpe = Column(
        Text,
        comment="Nom attribué à un ouvrage de prélèvement. Ce nom n’est pas obligatoire et ne suit pas de règle de nommage particulière.",
    )
    uri_ouvrage = Column(Text, comment="URL de la fiche de l’ouvrage dans le SANDRE")
    nb_autres_points_prelevement = Column(
        Integer,
        comment="Dans le cas où plusieurs points de prélèvement sont associés au même ouvrage, nombre de ces points (calcul DEAL d’après la BNPE)",
    )
    liste_autres_points_prelevement = Column(
        Text,
        comment="Dans le cas où plusieurs points de prélèvement sont associés au même ouvrage, liste de ces points (liste DEAL d’après la BNPE)",
    )
    code_point_referent = Column(
        Text,
        comment="Code du point de prélèvement référent pour l’ouvrage dans le cadre où un ouvrage est associé à plusieurs points de prélèvements",
    )
    uri_bss_point_eau = Column(Text, comment="URL du point BSS")
    code_bss_ancien = Column(
        Text,
        ForeignKey("referentiel.bss.code_bss_ancien"),
        comment="Uniquement pour les ouvrages de type SOUT : ancien code national du point d'eau dans la Banque Nationale du Sous-Sol qui correspond à l’ouvrage BNPE.",
    )
    code_bss_nouveau = Column(
        Text,
        ForeignKey("referentiel.bss.id_bss"),
        comment="Uniquement pour les ouvrages de type SOUT : nouveau code national du point d'eau dans la Banque Nationale du Sous-Sol qui correspond à l’ouvrage BNPE. Il prend la forme suivante : BSS000AAAA (cf détail ici: https://id.eaufrance.fr/ddd/PTE/3/CdNationalPTE).",
    )
    code_aiot = Column(
        Text,
        comment="Pour les ICPE, code d'identification, qui suit l'installation même si le site change de propriétaire",
    )
    usage_principal = Column(Text, comment="Usage associé")
    statut_administratif_prelevement = Column(
        Text,
        comment="Statut administratif du prélèvement: autorisé, en cours d’instruction, non autorisé",
    )
    statut = Column(
        Text,
        comment="Indique si l’ouvrage est encore en exploitation ou pas. A vocation à être complété de champs sur les dates de début et fin d’exploitation (par défaut, remplis à partir des chroniques de prélèvement connu",
    )
    statut_ars = Column(Text, comment="Statut du point de prélèvement d’après l’ARS")
    date_debut = Column(
        Text,
        comment="Date de début de prélèvement (correspond à la date de mise en service du point de prélèvement)",
    )
    date_fin = Column(
        Text,
        comment="Date de fin de prélèvement (correspond à la dernière date de prélèvement connu, et peut être différente de la date d’abandon administratif ou de remise en état des lieux)",
    )
    regime = Column(
        Text,
        comment="Régime réglementaire duquel relève le prélèvement (CSP, ICPE, IOTA, hydroélectricité)",
    )
    beneficiaire_principal = Column(
        Text,
        comment="Bénéficiaire principal du prélèvement (en cas de pluralité de bénéficiaires, ou d’une succession au fil du temps, choisir le principal)",
    )
    nature_eau_ars = Column(Text, comment="Nature de l’eau d’après l’ARS")
    debit_reglementaire_m3_j_ars = Column(
        Text, comment="Débit réglementaire en m3/j d’après l’ARS"
    )
    debit_moyen_jour_m3_j_ars = Column(
        Text, comment="Débit moyen en m3/j d’après l’ARS"
    )
    suivi_volume_frequence = Column(
        Text, comment="Fréquence de suivi du volume indiquée dans l’arrêté préfectoral"
    )
    suivi_debit_instantane_frequence = Column(
        Text,
        comment="Fréquence de suivi du débit instantané indiquée dans l’arrêté préfectoral",
    )
    suivi_niveau_eau_frequence = Column(
        Text,
        comment="Fréquence de suivi du niveau d’eau indiquée dans l’arrêté préfectoral",
    )
    suivi_ph_frequence = Column(
        Text, comment="Fréquence de suivi du pH indiquée dans l’arrêté préfectoral"
    )
    suivi_temperature_frequence = Column(
        Text,
        comment="Fréquence de suivi de la température indiquée dans l’arrêté préfectoral",
    )
    suivi_conductivite_frequence = Column(
        Text,
        comment="Fréquence de suivi de la conductivité indiquée dans l’arrêté préfectoral",
    )
    suivi_chlorures_frequence = Column(
        Text,
        comment="Fréquence de suivi de la concentration en chlorures indiquée dans l’arrêté préfectoral",
    )
    suivi_nitrates_frequence = Column(
        Text,
        comment="Fréquence de suivi de la concentration en nitrates indiquée dans l’arrêté préfectoral",
    )
    suivi_sulfates_frequence = Column(
        Text,
        comment="Fréquence de suivi de la concentration en sulfates indiquée dans l’arrêté préfectoral",
    )
    autre_suivi = Column(
        Text, comment="Autre type de suivi prescrit par l’arrêté préfectoral"
    )
    stockage = Column(
        Text,
        comment="Modalités de transmission aux services de l’État des résultats du suivi (registre, base de données…)",
    )
    transmission = Column(
        Text,
        comment="Modalités de transmission aux services de l’État des résultats du suivi (transmission annuelle, quinquennale…)",
    )
    stockage_transmission_detail = Column(
        Text,
        comment="Détail des modalités de stockage des données et de transmission aux services de l’État des résultats du suivi (registre tenu à disposition, envoi annuel…)",
    )
    code_commune_insee = Column(
        Integer,
        ForeignKey("referentiel.commune.code_insee"),
        comment="Code INSEE de la commune où est situé l’ouvrage dans le référentiel communal en vigueur. http://www.insee.fr/fr/methodes/nomenclatures/cog/",
    )
    nom_commune = Column(
        Text,
        comment="Nom de la commune où est situé l’ouvrage dans le référentiel communal en vigueur. http://www.insee.fr/fr/methodes/nomenclatures/cog/",
    )
    nom_commune_ars = Column(Text, comment="Nom de la commune indiqué par l’ARS")
    code_bdlisa = Column(
        Text,
        comment="Uniquement pour les ouvrages de type SOUT : Code de la ressource en eau souterraine dans le référentiel BDLisa. Le référentiel est disponible sur le site du Sandre (entité hydrogéologique)",
    )
    uri_bdlisa = Column(
        Text, comment="URL de la fiche de l’entité hydrogéologique dans le SANDRE"
    )
    libelle_type_milieu = Column(
        Text,
        comment="Indique si l’ouvrage prélève en eau continentale de surface (CONT), souterraine (SOUT) ou en eaux de transition (LIT). Ces valeurs sont issues de la nomenclature Sandre 472 et sont les seules acceptées par la BNPE : http://id.eaufrance.fr/nsa/472",
    )
    code_meso = Column(
        Text,
        ForeignKey("referentiel.meso.code"),
        comment="Code de la masse d’eau souterraine dans laquelle le point de prélèvement est situé",
    )
    nom_meso = Column(
        Text,
        comment="Nom de la masse d’eau souterraine dans laquelle le point de prélèvement est situé",
    )
    zre = Column(
        Text,
        comment="Indique si le point de prélèvement est situé en zone de répartition des eaux (ZRE)",
    )
    code_cours_eau_bdcarthage = Column(
        Text,
        ForeignKey("referentiel.bv_bdcarthage.code_cours"),
        comment="Code du cours d’eau BD Carthage dans le bassin versant duquel le point de prélèvement est situé",
    )
    cours_eau_bdcarthage = Column(
        Text,
        comment="Nom du cours d’eau BD Carthage dans le bassin versant duquel le point de prélèvement est situé",
    )
    code_me_cours_eau = Column(
        Text,
        ForeignKey("referentiel.me_continentales_bv.code_dce"),
        comment="Code de la masse d’eau cours d’eau DCE dans laquelle le point de prélèvement est situé",
    )
    nom_me_cours_eau = Column(
        Text,
        comment="Nom de la masse d’eau cours d’eau DCE dans laquelle le point de prélèvement est situé",
    )
    cours_eau = Column(
        Text,
        comment="Cours d’eau tel qu’indiqué dans l’autorisation, avec le plus de précision géographique possible. Si le prélèvement a lieu dans un affluent, il s’agit du nom de cet affluent lorsqu’il est connu",
    )
    profondeur = Column(
        Numeric,
        comment="Profondeur (pour les forages), telle qu’indiquée dans l’autorisation, dans le dossier de demande ou le rapport de l’hydrogéologue agréé)",
    )
    libelle_nature = Column(
        Text,
        comment="Indique la nature du point de prélèvement:- FICTIF: Point fictif matérialisant un ensemble de points de prélèvements ou  de restitutions "
        + "appartenant à une même ressource en eau, et dont l’identité et la position géographique sont incertaines ou non encore relevés sur le "
        + "terrain - PHYSIQUE: Point de prélèvement ou de restitution ayant bien été individualisé, identifié et géolocaliséNomenclature Sandre : http://id.eaufrance.fr/nsa/471",
    )
    code_zone_hydro = Column(
        Text,
        comment="Uniquement pour les ouvrages de type CONT : la zone hydrographique est définie et téléchargeable sur le site du Sandre : http://www.sandre.eaufrance.fr/atlas/srv/fre/catalog.search#/metadata/3409c9c3-9836-43be-bac3-b110c82b3a25",
    )
    uri_zone_hydro = Column(
        Text, comment="URL de la fiche du cours d’eau dans le SANDRE"
    )
    nappe_accompagnement = Column(Text, comment="Nappe d'accompagnement")
    x_bnpe = Column(
        Numeric,
        comment="Longitude de l’ouvrage en WGS84 (epsg : 4326, Sandre : 31) telle que diffusée au grand public sur la BNPE (floutage pour les captages AEP).",
    )
    y_bnpe = Column(
        Numeric,
        comment="Latitude de l’ouvrage en WGS84 (epsg : 4326, Sandre : 31) telle que diffusée au grand public sur la BNPE (floutage pour les captages AEP).",
    )
    precision_coord_bnpe = Column(
        Text,
        comment="Code indiquant le degré de précision des coordonnées géographiques de l’ouvrage. "
        + "La liste des codes relève de la nomenclature 159 administrée par le SANDRE (http://id.eaufrance.fr/nsa/159). "
        + "L’ouvrage peut être localisé au centroïde de la commune sur laquelle il est situé si sa précision "
        + "n’est pas connue/transmise (code 5 et 6) Liste des codes:  0Précision inconnue  1Coordonnées relevées "
        + "(précision du centimètre)  2Coordonnées mesurées (précision du mètre)  3Coordonnées établies (précision du décamètre) "
        + "4Coordonnées estimées (précision du kilomètre)  5Coordonnées du centroïde de la commune  6Coordonnées du centre administratif de la commune",
    )
    x_sig_aep_2022 = Column(
        Numeric,
        comment="Longitude transmise par l’ARS en 2022. Donnée sensible non publique",
    )
    y_sig_aep_2022 = Column(
        Numeric,
        comment="Latitude transmise par l’ARS en 2022. Donnée sensible non publique",
    )
    detail_localisation = Column(
        Text,
        comment="Détail sur la localisation du point (ex: nom de lieu-dit, modalités d’accès…)",
    )
    wkt_geom_synthese = Column(
        Text,
        comment="Géométrie la plus précise possible retenue in fine dans la base de données régionale, au format WellKnownText. Donnée sensible non publique",
    )
    geom = Column(
        Geometry("POINT", 2975),
        comment="champ rempli automatiquement en base de données",
    )
    precision_coord_synthese = Column(
        Text, comment="Précision de la localisation (à terme, tout devrait être précis)"
    )
    source = Column(Text, comment="Source de la donnée")
    remarque = Column(Text, comment="Remarque libre")
    validation_finale_laurence = Column(
        Text, comment="Date à laquelle Laurence a validé la ligne"
    )
    observations_laurence = Column(Text, comment="Observations de Laurence")
    validation_finale_valentin = Column(
        Text, comment="Date à laquelle Valentin a validé la ligne"
    )
    todo = Column(
        Text,
        comment="Vérifications à réaliser encore sur la ligne avant de pouvoir la déclarer validée",
    )
    contacter_ars = Column(Text, comment="Contacter ARS")
    contacter_sprei = Column(Text, comment="Contacter SPREI")
    contacter_brgm = Column(Text, comment="Contacter BRGM")
    contacter_oe = Column(Text, comment="Contacter OE")


class Document(HistoricalDBBase):
    __tablename__ = "document"
    __table_args__ = {
        "schema": "prelevement",
        "comment": "Table listant les documents associés à chaque point de prélèvement (arrêtés d'autorisation, délibérations d'abandon...)",
    }

    id_doc = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Primary key for the document",
    )
    nom_fichier = Column(Text, comment="Nom du fichier")
    reference_doc = Column(Text, comment="Référence du document")
    nature_doc = Column(Text, comment="Nature du document")
    date_doc = Column(Date, comment="Date du document")
    date_fin_validite = Column(Date, comment="Date de fin de validité")
    beneficiaire_origine = Column(Text, comment="Bénéficiaire d'origine")
    beneficiaire_actuel = Column(Text, comment="Bénéficiaire actuel")
    usage = Column(Text, comment="Usage")
    chemin = Column(Text, comment="Chemin")
    remarque_vlt = Column(Text, comment="Remarque VLT")  # TODO: supprimer à terme
    lien_doc_local = Column(
        Text, comment="Lien vers le document local"
    )  # TODO: supprimer à terme
    lien_doc_web = Column(
        Text, comment="Lien vers le document web"
    )  # TODO: supprimer à terme


class LienDocumentPointPrelevement(HistoricalDBBase):
    __tablename__ = "lien_document_point_prelevement"
    __table_args__ = (
        UniqueConstraint("id_synthese", "id_doc", name="id_synthese_id_doc_unique"),
        {
            "schema": "prelevement",
            "comment": "Table pivot faisant le lien entre les documents et les points de prélèvement",
        },
    )

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Primary key for the lien_document_point_prelevement",
    )
    id_synthese = Column(
        Integer,
        ForeignKey("prelevement.point_prelevement.id_synthese", ondelete="NO ACTION"),
        comment="Foreign key referencing id_synthese in point_prelevement",
    )
    id_doc = Column(
        Integer,
        ForeignKey("prelevement.document.id_doc", ondelete="NO ACTION"),
        comment="Foreign key referencing id_doc in document",
    )
    nature_doc = Column(Text, comment="Nature du document")
    reference_doc = Column(Text, comment="Référence du document")
    date_doc = Column(Date, comment="Date du document")
    annee_doc = Column(Integer, comment="Année du document")
    beneficiaire_origine = Column(Text, comment="Bénéficiaire d'origine")
    beneficiaire_actuel = Column(Text, comment="Bénéficiaire actuel")
    stockage = Column(Text, comment="Stockage")
    nom_fichier = Column(Text, comment="Nom du fichier")
    lien_dossier = Column(Text, comment="Lien vers le dossier")
    lien_doc_local = Column(Text, comment="Lien vers le document local")
    lien_doc_web = Column(Text, comment="Lien vers le document web")
    nom_retenu = Column(Text, comment="Nom retenu")


class Regle(HistoricalDBBase):
    __tablename__ = "regle"
    __table_args__ = {
        "schema": "prelevement",
        "comment": "Table listant les regles associés à chaque point de prélèvement. Il s'agit des valeurs limites définies dans les arrêtés à ne pas dépasser.",
    }

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Primary key for the regle",
    )
    id_synthese = Column(
        Integer,
        ForeignKey("prelevement.point_prelevement.id_synthese", ondelete="NO ACTION"),
        comment="Foreign key referencing id_synthese in point_prelevement",
    )
    id_doc = Column(
        Integer,
        ForeignKey("prelevement.document.id_doc", ondelete="NO ACTION"),
        comment="Foreign key referencing id_doc in document",
    )
    libelle_parametre = Column(Text, comment="Libellé du paramètre")
    unite = Column(Text, comment="Unité")
    valeur = Column(Text, comment="Valeur")
    liste_id_synthese = Column(
        ARRAY(Text), comment="Liste des identifiants de synthèse"
    )
    remarque = Column(Text, comment="Remarque")
    remarque_vlt = Column(Text, comment="Remarque VLT")
    nature_doc = Column(
        Text, comment="Nature du document"
    )  # TODO: champ à supprimer à terme
    date_debut = Column(
        Date, comment="Date de début"
    )  # TODO: champ à supprimer à terme
    date_fin = Column(Date, comment="Date de fin")  # TODO: champ à supprimer à terme
    annee = Column(Integer, comment="Année")  # TODO: champ à supprimer à terme
    beneficiaire_origine = Column(
        Text, comment="Bénéficiaire d'origine"
    )  # TODO: champ à supprimer à terme
    beneficiaire_actuel = Column(
        Text, comment="Bénéficiaire actuel"
    )  # TODO: champ à supprimer à terme
    lien_doc_web = Column(
        Text, comment="Lien vers le document web"
    )  # TODO: champ à supprimer à terme
    lien_dossier = Column(
        Text, comment="Lien vers le dossier"
    )  # TODO: champ à supprimer à terme
    nom_retenu = Column(Text, comment="Nom retenu")  # TODO: champ à supprimer à terme


class SerieDonnees(HistoricalDBBase):
    __tablename__ = "serie_donnees"
    __table_args__ = (
        UniqueConstraint("code_serie", name="code_serie_unique"),
        {
            "schema": "prelevement",
            "comment": "Table stockant la liste des séries de données transmises. "
            + "Elle permet de décrire des éléments de métadonnées utiles à la traçabilité et à l’analyse de la qualité de la donnée. "
            + "Pour un même point de suivi, plusieurs paramètres peuvent faire l’objet de données (ex: T°C, conductivité, volume…), "
            + "chacun avec ses critères propres (pas de temps d’acquisition, matériel utilisé, nom de l’opérateur de mesure). "
            + "En général, un point de prélèvement est concerné par un seul point de suivi, mais dans certains cas il y en a plusieurs "
            + "(ex: sondes placées à différentes profondeurs pour un forage). Cela peut être noté dans le champ detail_point_suivi.",
        },
    )

    id_serie = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Identifiant unique et pérenne de la série de données",
    )
    code_serie = Column(
        Text, unique=True, comment="Code autogénéré de la série de données"
    )
    id_synthese_principal = Column(
        Integer,
        ForeignKey("prelevement.point_prelevement.id_synthese", ondelete="NO ACTION"),
        comment="Identifiant du point de prélèvement dans la base de données régionales 974",
    )
    nom_cite = Column(
        Text,
        comment="Nom du point de prélèvement tel qu’il est cité dans les données source transmises par les préleveurs",
    )
    liste_id_synthese = Column(
        ARRAY(Text),
        comment="Lorsque le paramètre est commun à plusieurs points de prélèvement, liste des id_synthese de ces points (intégrant l’id_synthese_principal)",
    )
    detail_point_suivi = Column(
        Text,
        comment="Détail sur le point de suivi (ex: nom de la sonde ou du puits lorsqu’un même point de prélèvement fait l’objet de plusieurs points de suivi)",
    )
    profondeur = Column(
        Integer,
        comment="Profondeur du point de suivi en mNGR (pour les suivis en eaux souterraines)",
    )
    libelle_parametre = Column(Text, comment="Libellé libre du paramètre")
    categorie_parametre = Column(Text, comment="Catégorie du paramètre")
    unite = Column(Text, comment="Unité de mesure")
    frequence = Column(
        Text, comment="Durée de la période de référence (jour, mois, année)"
    )
    traitement_donnees = Column(
        Text,
        comment="Dans le cas d’une donnée issue d’un calcul (ex: min, max, moy…), indique la nature des traitements appliqués aux données sur la période",
    )
    appareil = Column(Text, comment="Références de l’appareil utilisé")
    date_debut = Column(
        Text,
        comment="Date de début de la chronique de mesures pour ce paramètre dans le jeu de données transmis, au mois prêt (au format aaaa-mm)",
    )
    date_fin = Column(
        Text,
        comment="Date de fin de la chronique de mesures pour ce paramètre dans le jeu de données transmis, au mois prêt (au format aaaa-mm)",
    )
    operateur_structure = Column(Text, comment="Structure ayant réalisé la mesure")
    operateur_nom = Column(Text, comment="Nom de la personne ayant réalisé la mesure")
    operateur_prenom = Column(
        Text, comment="Prénom de la personne ayant réalisé la mesure"
    )
    operateur_courriel = Column(
        Text, comment="Courriel de l’opérateur ayant réalisé la mesure"
    )
    url_deal = Column(
        Text, comment="Chemin d’accès au fichier source sur le serveur de la DEAL"
    )
    nom_fichier = Column(Text, comment="Nom du fichier duquel est issu la série")
    date_standardisation = Column(
        Text,
        comment="Date à laquelle la série de données a été numérisée par le préleveur dans le présent fichier, au format aaaa-mm-jj",
    )
    remarque = Column(
        Text,
        comment="Remarque libre sur la mesure du paramètres, sa retranscription ou la continuité de la série de données",
    )
    date_integration_bdd = Column(
        Date,
        comment="Date à laquelle la donnée a été intégrée à la base de données (pour la traçabilité)",
    )
    process_import = Column(Text, comment="Processus d'import")


class ResultatSuivi(HistoricalDBBase):
    __tablename__ = "resultat_suivi"
    __table_args__ = {
        "schema": "prelevement",
        "comment": "Table listant les valeurs des paramètres à proprement parler, pour chacune des séries de données transmises.",
    }

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Identifiant unique et pérenne de la valeur de suivi",
    )
    id_serie = Column(
        Integer,
        ForeignKey("prelevement.serie_donnees.id_serie", ondelete="NO ACTION"),
        comment="Valeurs récupérées automatiquement depuis la feuille «description_series_donnees»",
    )
    date_debut = Column(
        Date, comment="Date à laquelle a débuté la mesure, au format aaaa/mm/jj"
    )
    heure_debut = Column(
        Time, comment="Heure à laquelle a débuté la mesure, au format aaaa/mm/jj"
    )
    date_fin = Column(
        Date, comment="Date à laquelle s’est terminée la mesure, au format hh:mm:ss"
    )
    heure_fin = Column(
        Time, comment="Heure à laquelle s’est terminée la mesure, au format hh:mm:ss"
    )
    type_date = Column(
        Text,
        comment="Indique si la date est fournie par le producteur ou déduite à partir de la période indiquée",
    )
    valeur = Column(
        Numeric,
        comment="Valeur du paramètre. Lorsque cette valeur est absente du jeu de données d’origine, ne pas remplir la cellule (NULL), et indiquer dans le champ remarque «donnée absente»",
    )
    remarque = Column(Text, comment="Remarque libre sur la valeur")
    code_serie = Column(
        Text,
        ForeignKey("prelevement.serie_donnees.code_serie", ondelete="NO ACTION"),
        comment="Code de la série de données telle que décrite dans la feuille «description_series_donnees»",
    )  # TODO: a supprimer à terme (redondant avec id_serie)
    date_integration_bdd = Column(
        Date,
        comment="Date à laquelle la donnée a été intégrée à la base de données (pour la traçabilité)",
    )
    usage = Column(Text, comment="Pour les données de volume, usage de l'eau prélevée")
    id_origine = Column(
        Text,
        comment="Identifiant unique de la donnée dans la série de données d'origine",
    )


# COMMENTS

COMMENT_NETTOYAGE_VALEURS_NULL_ET_ESPACE = """COMMENT ON FUNCTION public.nettoyage_valeurs_null_et_espaces IS
'Fonction permettant de remplacer toutes les valeurs '''' par une valeur NULL et également (depuis la version 3) d''appliquer à tous les champs une fonction Trim permettant de supprimer les espaces indésirables en bout de chaîne.';
"""

# DROP TABLES

DROP_JDD_ANALYSE_CASCADE = "DROP TABLE IF EXISTS public.jdd_analyse CASCADE;"

DROP_RESULTAT_SUIVI_CASCADE = "DROP TABLE IF EXISTS prelevement.resultat_suivi CASCADE;"

# VIEWS

CREATE_VIEW_JDD_ANALYSE = """

CREATE OR REPLACE VIEW public.v_jdd_analyse AS
 WITH r AS (
         SELECT jdd_analyse.jdd_nom,
            jdd_analyse.ordre,
            jdd_analyse.champ,
            jdd_analyse.nb_valeurs,
            CASE
                WHEN valeurs::TEXT ILIKE '%Nombre de valeurs%' THEN btrim(valeurs::TEXT,'[]"')
                ELSE NULL
            END AS valeurs_trop_nombreuses,
            jsonb_array_elements(jdd_analyse.valeurs) ->> 'valeur'::text AS valeurs,
            jsonb_array_elements(jdd_analyse.valeurs) ->> 'occurence'::text AS occurence
           FROM public.jdd_analyse
          ORDER BY jdd_analyse.jdd_nom, jdd_analyse.ordre
        )

 SELECT r.jdd_nom,
    r.ordre,
    r.champ,
    r.nb_valeurs,
    CASE
        WHEN r.valeurs_trop_nombreuses IS NOT NULL THEN r.valeurs_trop_nombreuses
        ELSE string_agg(((r.valeurs || ' ('::text) || r.occurence) || ' obs.)'::text, ' | '::text)
    END AS valeurs_occurence

   FROM r
  GROUP BY r.jdd_nom, r.ordre, r.champ, r.nb_valeurs, r.valeurs_trop_nombreuses
  ORDER BY r.jdd_nom, r.ordre;
"""

# FUNCTIONS

CREATE_FUNCTION_NETTOYAGE_VALEURS_NULL_ET_ESPACE = """
    CREATE OR REPLACE FUNCTION public.nettoyage_valeurs_null_et_espaces(
    jdd_nom text,
    schema text)
    RETURNS void
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE
AS $BODY$


DECLARE liste_champs RECORD;

BEGIN

FOR liste_champs IN (
    SELECT column_name AS champ
    FROM information_schema.columns
    WHERE table_schema = $2
    AND table_name = $1
    AND column_name <> 'geom' -- l'utilisation de champ nommé 'geom' pose des problèmes d'application de la fonction
    AND (data_type ILIKE 'character varying%' OR data_type ilike 'text') -- l'utilisation de champs d'autres formats ne permet pas l'application de la fonction TRIM)
    ORDER BY ordinal_position
    )

    LOOP

    EXECUTE

    -- Suppression des espaces
    'UPDATE ' || $2 || '.'  || $1||
    ' SET ' || liste_champs.champ || ' = TRIM(' || liste_champs.champ || ') ;'

    -- Remplacement des '' par des NULL
    'UPDATE ' || $2 || '.'  || $1||
    ' SET ' || liste_champs.champ || ' = NULL
    WHERE ' || liste_champs.champ || '::TEXT = ''''	;';

    END LOOP;
    RETURN;

END;
$BODY$;
"""
