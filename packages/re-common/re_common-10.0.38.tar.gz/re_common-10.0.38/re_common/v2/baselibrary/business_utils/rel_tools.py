def assign_group_id(rows: list, sub_db_order: list):
    subdb_keyid_map = {row.sub_db_id: row.keyid for row in rows}
    for sub_db_id in sub_db_order:
        if keyid := subdb_keyid_map.get(sub_db_id):
            return keyid, len(rows), rows
    return rows[0].keyid, len(rows), rows
