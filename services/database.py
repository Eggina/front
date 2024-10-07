import os
from sqlalchemy import create_engine, engine
from sqlalchemy.orm import sessionmaker

# ssl_args = {'sslrootcert': 'certificates/server-ca.pem','sslcert': 'certificates/client-cert.pem', 'sslkey': 'certificates/client-key.pem'}

# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=ssl_args)


def get_local():
    SQLALCHEMY_DATABASE_URL = 'postgresql://read_only_datos_sube:sudoku@localhost:5432/datos_sube'
    return create_engine(SQLALCHEMY_DATABASE_URL)


def get_pool():
    if 'DB_HOST' in os.environ:
        return pool_from_tcp()
    if 'CLOUD_SQL_CONNECTION_NAME' in os.environ:
        return pool_from_socket()
    return get_local()


def pool_from_tcp():
    print('creando engine mediante tcp')
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASS"]
    db_name = os.environ["DB_NAME"]
    db_host = os.environ["DB_HOST"]

    host_args = db_host.split(":")
    db_hostname, db_port = host_args[0], int(host_args[1])

    ssl_args = {'sslrootcert': 'certificates/server-ca.pem',
                'sslcert': 'certificates/client-cert.pem', 'sslkey': 'certificates/client-key.pem'}

    pool = create_engine(engine.url.URL(
        drivername="postgres",
        username=db_user,  # e.g. "my-database-user"
        password=db_pass,  # e.g. "my-database-password"
        host=db_hostname,  # e.g. "127.0.0.1"
        port=db_port,  # e.g. 5432
        database=db_name  # e.g. "my-database-name"
    ),
        connect_args=ssl_args
    )
    return pool


def pool_from_socket():
    print("Creando engine mediante unix-socket")
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASS"]
    db_name = os.environ["DB_NAME"]
    db_socket_dir = os.environ.get("DB_SOCKET_DIR", "/cloudsql")
    cloud_sql_connection_name = os.environ["CLOUD_SQL_CONNECTION_NAME"]

    pool = create_engine(
        engine.url.URL(
            drivername="postgres+pg8000",
            username=db_user,  # e.g. "my-database-user"
            password=db_pass,  # e.g. "my-database-password"
            database=db_name,  # e.g. "my-database-name"
            query={
                "unix_sock": "{}/{}/.s.PGSQL.5432".format(
                    db_socket_dir,  # e.g. "/cloudsql"
                    cloud_sql_connection_name)  # i.e "<PROJECT-NAME>:<INSTANCE-REGION>:<INSTANCE-NAME>"
            }
        ),
    )
    pool.dialect.description_encoding = None

    return pool


pool = get_pool()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=pool)
