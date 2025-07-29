def apply_transco(transco_matrix, txt: str):
    res: str = txt
    if res is not None:
        for transco in transco_matrix:
            res = res.replace(transco["package_object_id"], transco["tenant_object_id"])
    return res