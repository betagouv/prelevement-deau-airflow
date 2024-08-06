from sqlalchemy import select

from utils.demarchessimplifiees.last_snapshot.models import PieceJointeLastSnapshot

LIST_FILES_ATTRIBUTS = [
    "fichiers_tableurs",
    "fichiers_autres_documents",
    "extraits_registres_papiers",
    "pieces_jointes",
    "fichier_tableau_suivi_camion_citerne",
]


def copy_table_to_last_snapshot(
    model, model_last_snapshot, demarche_data_brute_id, session
):
    all_rows = (
        session.execute(
            select(model).filter_by(demarche_data_brute_id=demarche_data_brute_id)
        )
        .scalars()
        .all()
    )
    all_rows_last_snapshot = []
    for row in all_rows:
        row_data = {
            key: value
            for key, value in row.__dict__.items()
            if key != "_sa_instance_state"
        }
        row_last_snapshot = model_last_snapshot(**row_data)

        for list_files_attribut in LIST_FILES_ATTRIBUTS:
            if hasattr(row, list_files_attribut):
                list_files = getattr(row, list_files_attribut)
                list_files_last_snapshot = []
                for file in list_files:
                    file_data = {
                        key: value
                        for key, value in file.__dict__.items()
                        if key != "_sa_instance_state"
                    }
                    file_last_snapshot = PieceJointeLastSnapshot(**file_data)
                    list_files_last_snapshot.append(file_last_snapshot)
                setattr(
                    row_last_snapshot, list_files_attribut, list_files_last_snapshot
                )
        all_rows_last_snapshot.append(row_last_snapshot)

    session.add_all(all_rows_last_snapshot)
    session.commit()

    return all_rows_last_snapshot
