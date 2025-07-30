from airflow.exceptions import AirflowSkipException
from airflow.models import Variable
from airflow.models.baseoperator import BaseOperator


class TransformFileOperator(BaseOperator):
    """
    Opérateur en charge de créer un fichier Json pour chaque fichier Alfresco.

    Pour chaque nœud File, créé un object `node` représentant un nœud au format `node_injector`.

    Le nœud est enrichie par l'appel de la fonction `pristy.alfresco_operator.update_node_path.update_node_path`
    et la fonction `mapping_func`

    :param mapping_func: Function use to bind medata or aspect. Will receive 2 parameters:  src_node, new_node
        (for exemple: reprise_fichier_usager)
    """

    def __init__(self, *, child, mapping_func=None, **kwargs):
        super().__init__(**kwargs)
        self.child = child  # TODO rename to nodes
        self.mapping_func = mapping_func
        """Children nodes to transform"""

    def execute(self, context, mapping_func=None):
        """
        :param context: Airflow context
        """
        from pristy.alfresco_operator.update_node_path import update_node_path

        nodes = []
        for c in self.child:
            if not c['isFile']:
                continue
            self.log.info(f"transform {c['id']} ({c['name']})")
            source_server = Variable.get('alfresco_source_server')
            created_at = c['createdAt'].replace("+0000", "Z")
            modified_at = c['modifiedAt'].replace("+0000", "Z")
            if c['nodeType'] == 'app:filelink':
                source = {
                    "type": "alfresco",
                    "server": source_server,
                    "uuid": c['id']
                }
            else:
                source = {
                    "type": "alfresco",
                    "server": source_server,
                    "uuid": c['id'],
                    "mimetype": c['content']['mimeType'],
                    "size": c['content']['sizeInBytes']
                }
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
                },
                "source": source
            }

            update_node_path(c, node)
            if self.mapping_func is not None:
                self.mapping_func(c, node)
            nodes.append(node)

        if len(nodes) == 0:
            raise AirflowSkipException('No file transformed, mark as skip')
        return nodes
