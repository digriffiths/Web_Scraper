from sqlalchemy.orm import DeclarativeBase
import sqlalchemy  # type: ignore
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update
from sqlalchemy import MetaData

class Base(DeclarativeBase):
    pass

class SQLDB:
    """Class for handling SQL connections, as well as creating, inserting into, and querying tables."""

    def __init__(
        self,
        user: str,
        password: str,
        host: str,
        port: str,
        dbname: str,
        models: list[Base] | None = None,
        
    ):
        """
        Initializes an instance of SQLDB and establishes a connection to the SQL database.

        :param user: The username used to connect to the SQL database.
        :type user: str
        :param password: The password used to connect to the SQL database.
        :type password: str
        :param host: The hostname used to connect to the SQL database.
        :type host: str
        :param dbname: The name of the database that a connection will be established with.
        :type dbname: str
        :param models: A list of SQLAlchemy models to register with the database. Default is None.
        :type models: Optional[list[Base]]
        """
        # connection string to the postgres db
        conn_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        # conn_string = 'sqlite:///data/utils_interactions.sqlite' # for temporary use

        #the engine that will be used to connect
        self.engine = sqlalchemy.create_engine(conn_string)

        #establish a connection to the db
        self.conn = self.engine.connect()

        #autocommit set to true, commit() not necessary
        self.conn.autocommit = True  # type: ignore

        #cobject to create sessions
        self.Session = sessionmaker(bind=self.engine)

        # Create tables from sqlachemy models if provided
        if models:
            for model in models:
                self.create_table_from_model(model)

    def create_table_from_model(self, model) -> None:
        """
        Creates a table in the SQL database based on the provided SQLAlchemy model.

        :param model: The SQLAlchemy model representing the table structure.
        """
        model.metadata.create_all(self.engine)

    def add_data(self, data: list[Base]):
        """
        Adds data to the SQL database.

        :param data: A list of SQLAlchemy model instances representing the data to be added.
        :type data: list[Base]
        :raises Exception: If there's an error during data addition, a rollback is performed, and the original exception is raised.
        """
#create a instance of a session
        with self.Session() as session:

            try:
                #method used to prepare data and adds data to the staging area
                session.bulk_save_objects(data)
                #commits data to database
                session.commit()
                
            except Exception as e:
                #removes data from staging area
                session.rollback()
                raise e

    def delete_table(self, table_name: str):
        """
        Deletes a table from the SQL database.

        :param table_name: The name of the table to delete.
        :type table_name: str
        """
        #use .text to create SQL statements
        drop_statement = sqlalchemy.text(f'DROP TABLE "{table_name}"')

        with self.Session() as session:
            try:
                #execute the sql statement
                session.execute(drop_statement)
                #apply to the database
                session.commit()
            except Exception as e:
                # Rollback the transaction if an error occurs
                session.rollback()
                raise e

    def query(self, sql: str) -> str:
        """
        Executes a SQL query and returns the results.

        :param sql: The SQL query to execute.
        :type sql: str
        :return: The results of the SQL query.
        :rtype: str
        """
        return self.conn.execute(sql).fetchall()  # type: ignore

    def update_record(self, table_name: str, condition: dict, new_values: dict):
        """
        Updates a record in the SQL database.

        :param table_name: The name of the table where the record is located.
        :type table_name: str
        :param condition: The condition to select the record to update.
        :type condition: dict
        :param new_values: The new values to set in the record.
        :type new_values: dict
        """
        # Create a table object
        metadata = MetaData()
        table = sqlalchemy.Table(table_name, metadata, autoload_with=self.engine)

        # Create the update statement
        stmt = update(table).where(
            sqlalchemy.and_(
                *(getattr(table.c, key) == value for key, value in condition.items())
            )
        ).values(new_values)

        # Execute the update statement
        with self.Session() as session:
            try:
                session.execute(stmt)
                session.commit()
            except Exception as e:
                session.rollback()
                raise e