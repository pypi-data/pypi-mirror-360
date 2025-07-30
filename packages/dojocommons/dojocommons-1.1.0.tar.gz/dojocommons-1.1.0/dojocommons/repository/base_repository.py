from typing import Generic, TypeVar, Type, List, Optional
from dojocommons.service.db_service import DbService
from dojocommons.model.app_configuration import AppConfiguration

# Define um TypeVar para representar o tipo genérico
T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    BaseRepository
    ==============

    Uma classe genérica para manipulação de entidades em um banco de dados.
     Esta classe utiliza o `DbService` para executar operações no
      banco de dados e é projetada para trabalhar com modelos que seguem
       o padrão de validação do Pydantic.

    Classes
    -------
    BaseRepository
        Classe genérica para operações CRUD em um banco de dados.

    Parâmetros
    ----------
    cfg : AppConfiguration
        Configuração da aplicação, utilizada para inicializar o serviço de
         banco de dados.
    model : Type[T]
        O modelo da entidade que será manipulado. Deve ser uma classe que
         segue o padrão de validação do Pydantic.
    table_name : str
        O nome da tabela no banco de dados onde as entidades serão armazenadas.

    Métodos
    -------
    create(entity: T) -> T
        Insere uma nova entidade no banco de dados.
    find_by_id(entity_id: int) -> Optional[T]
        Busca uma entidade pelo ID.
    find_all() -> List[T]
        Retorna todas as entidades cadastradas no banco de dados.
    update(entity_id: int, updates: dict) -> Optional[T]
        Atualiza uma entidade pelo ID com os valores fornecidos.
    delete(entity_id: int) -> None
        Deleta uma entidade pelo ID.

    Exemplo de Uso
    --------------
    .. code-block:: python

        from typing import Optional
        from pydantic import BaseModel
        from dojocommons.model.app_configuration import AppConfiguration
        from dojocommons.repository.base_repository import BaseRepository

        # Definição do modelo
        class User(BaseModel):
            id: Optional[int]
            name: str
            email: str

        # Definição do repositório
        class UserRepository(BaseRepository[User]):
            def __init__(self, cfg: AppConfiguration):
                super().__init__(cfg, User, "users")

        # Configuração da aplicação
        app_cfg = AppConfiguration(
            app_name="MyApp",
            app_version="1.0.0",
            s3_bucket="my-bucket",
            s3_path="db",
            aws_region="us-east-1",
            aws_endpoint="http://localhost:9000",
            aws_access_key_id="my-access-key",
            aws_secret_access_key="my-secret-key",
        )

        # Instanciação do repositório
        user_repository = Go.pRepository(cfg=app_cfg)

        # Criação de um novo usuário
        new_user = User(name="John Doe", email="john.doe@example.com")
        user_repository.create(new_user)

        # Busca de um usuário pelo ID
        user = user_repository.find_by_id(1)
        if user:
            print(f"Usuário encontrado: {user.name} - {user.email}")

        # Atualização de um usuário
        updated_user = user_repository.update(1, {"name": "John Smith"})
        if updated_user:
            print(f"Usuário atualizado: {updated_user.name}")

        # Listagem de todos os usuários
        all_users = user_repository.find_all()
        for user in all_users:
            print(f"{user.id}: {user.name} - {user.email}")

        # Deleção de um usuário
        user_repository.delete(1)
    """

    def __init__(self, cfg: AppConfiguration, model: Type[T], table_name: str):
        self._db = DbService(cfg)
        self._model = model
        self._table_name = table_name

    def create(self, entity: T) -> T:
        """
        Insere uma nova entidade no banco.

        :param T entity: A entidade a ser inserida no banco de dados.
        :return: A entidade inserida no banco de dados.
        :rtype: T
        """
        # Filtra as colunas e valores para ignorar os que são None
        filtered_data = {
            k: v for k, v in entity.__dict__.items() if v is not None
        }

        columns = ", ".join(filtered_data.keys())
        placeholders = ", ".join(["?"] * len(filtered_data))
        values = tuple(filtered_data.values())

        query = (
            f"INSERT INTO {self._table_name} ({columns})"
            f" VALUES ({placeholders})"
        )
        self._db.execute_query(query, values)
        return entity

    def find_by_id(self, entity_id: int) -> Optional[T]:
        """
        Busca uma entidade pelo ID.

        :param int entity_id: O ID da entidade a ser buscada.
        :return: A entidade encontrada ou None se não existir.
        :rtype: Optional[T]
        """
        row = self._db.execute_query(
            f"SELECT * FROM {self._table_name} WHERE id = ?",
            (entity_id,),
        ).fetchone()

        if row:
            return self._model.model_validate(
                dict(zip(self._model.__annotations__.keys(), row))
            )
        return None

    def find_all(self) -> List[T]:
        """
        Retorna todas as entidades cadastradas.

        :return: Uma lista de todas as entidades cadastradas
         no banco de dados.
        :rtype: List[T]
        """
        rows = self._db.execute_query(
            f"SELECT * FROM {self._table_name}"
        ).fetchall()
        return [
            self._model.model_validate(
                dict(zip(self._model.__annotations__.keys(), row))
            )
            for row in rows
        ]

    def update(self, entity_id: int, updates: dict) -> Optional[T]:
        """
        Atualiza uma entidade pelo ID.

        :param int entity_id: O ID da entidade a ser atualizada.
        :param dict updates: Um dicionário com os campos a serem atualizados
         e seus novos valores.
        :return: A entidade atualizada ou None se não existir.
        :rtype: Optional[T]
        """
        # Filtra as colunas e valores para ignorar os que são None
        filtered_data = {k: v for k, v in updates.items() if v is not None}

        updates_sql = ", ".join([f"{key} = ?" for key in filtered_data.keys()])
        values = list(filtered_data.values()) + [entity_id]

        self._db.execute_query(
            f"UPDATE {self._table_name} SET {updates_sql} WHERE id = ?",
            tuple(values),
        )

        return self.find_by_id(entity_id)

    def delete(self, entity_id: int) -> None:
        """
        Deleta uma entidade pelo ID.

        :param int entity_id: O ID da entidade a ser deletada.
        """
        self._db.execute_query(
            f"DELETE FROM {self._table_name} WHERE id = ?",
            (entity_id,),
        )
