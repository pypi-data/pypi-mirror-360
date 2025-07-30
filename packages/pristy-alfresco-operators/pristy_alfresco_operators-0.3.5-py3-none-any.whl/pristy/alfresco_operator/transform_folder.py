from airflow.exceptions import AirflowSkipException
from airflow.models.baseoperator import BaseOperator


class TransformFolderOperator(BaseOperator):
    """
    Opérateur en charge de créer un fichier Json pour chaque dossier.

    Pour chaque nœud Folder, créé un object `node` représentant un nœud au format `node_injector`.

    Le nœud est enrichie par l'appel de la fonction `pristy.alfresco_operator.update_node_path.update_node_path`
    et la fonction `mapping_func`

    :param mapping_func: Function use to bind medata or aspect. Will receive 2 parameters:  src_node, new_node
        (for exemple: reprise_dossier_usager)
    """

    def __init__(self, *, child, mapping_func=None, **kwargs):
        super().__init__(**kwargs)
        self.child = child  # TODO rename to nodes
        self.mapping_func = mapping_func
        """Children nodes to transform"""

    def execute(self, context):
        from pristy.alfresco_operator.update_node_path import update_node_path

        nodes = []
        for c in self.child:
            self.log.debug(c)
            if not c['isFolder']:
                continue
            self.log.debug(f"transform {c['id']} ({c['name']})")

            created_at = c['createdAt'].replace("+0000", "Z")
            modified_at = c['modifiedAt'].replace("+0000", "Z")
            node = {
                "name": c['name'],
                "type": c['nodeType'],
                "dateCreated": created_at,
                "owner": c['createdByUser']['id'],
                "path": {},
                "properties": {
                    "cm:created": created_at,
                    "cm:creator": c['createdByUser']['id'],
                    "cm:modified": modified_at,
                    "cm:modifier": c['modifiedByUser']['id']
                }
            }
            update_node_path(c, node)
            if self.mapping_func is not None:
                self.mapping_func(c, node)
            nodes.append(node)

        if len(nodes) == 0:
            raise AirflowSkipException('No folder transformed, mark as skip')
        return nodes
