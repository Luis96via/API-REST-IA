import psycopg2
import sys
import socket
import dns.resolver
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

# Cargar variables de entorno
load_dotenv()

def resolve_host(hostname):
    """Intenta resolver el hostname usando diferentes métodos"""
    try:
        # Intentar con Google DNS
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ['8.8.8.8', '8.8.4.4']
        answers = resolver.resolve(hostname, 'A')
        if answers:
            return str(answers[0])
    except Exception as e:
        print(f"Error al resolver con Google DNS: {str(e)}")
    
    try:
        # Intentar con DNS del sistema
        return socket.gethostbyname(hostname)
    except Exception as e:
        print(f"Error al resolver con DNS del sistema: {str(e)}")
    
    return None

def test_connection(host, port, user, dbname, use_ssl=True, timeout=10):
    print(f"\nProbando conexión a {host}:{port} (SSL: {use_ssl})")
    print(f"Usuario: {user}")
    print(f"Base de datos: {dbname}")
    try:
        # Obtener la contraseña del .env
        db_url = os.getenv("SUPABASE_DB_URL")
        if not db_url:
            raise ValueError("No se encontró SUPABASE_DB_URL en el .env")
        
        # Extraer la contraseña de la URL
        parsed = urlparse(db_url)
        password = parsed.password
        
        # Primero conectar a postgres para poder crear la base de datos si no existe
        conn_params = {
            'dbname': 'postgres',  # Siempre conectar primero a postgres
            'user': user,
            'password': password,
            'host': host,
            'port': port,
            'connect_timeout': timeout,
            'application_name': 'test_connection'
        }
        
        if use_ssl:
            conn_params['sslmode'] = 'require'
        else:
            conn_params['sslmode'] = 'disable'
        
        # Función auxiliar para conectar
        def connect_to_db(params):
            try:
                return psycopg2.connect(**params)
            except Exception as e:
                print(f"Error al conectar con parámetros: {dict(params, password='***')}")
                raise e
        
        # Conectar a postgres
        conn = connect_to_db(conn_params)
        with conn:
            with conn.cursor() as cur:
                # Verificar la conexión
                cur.execute("SELECT version();")
                version = cur.fetchone()
                print(f"✅ Conexión exitosa!")
                print(f"Versión de PostgreSQL: {version[0]}")
                
                # Verificar permisos
                cur.execute("""
                    SELECT 
                        current_user,
                        current_setting('role'),
                        (SELECT string_agg(privilege_type, ', ')
                         FROM information_schema.role_table_grants
                         WHERE grantee = current_user) as privileges;
                """)
                user_info = cur.fetchone()
                print(f"\nInformación de usuario:")
                print(f"Usuario actual: {user_info[0]}")
                print(f"Rol actual: {user_info[1]}")
                print(f"Privilegios: {user_info[2] or 'Ninguno'}")
                
                # Listar las bases de datos disponibles
                cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
                databases = [row[0] for row in cur.fetchall()]
                print(f"\nBases de datos disponibles: {databases}")
                
                # Si la base de datos objetivo no existe, intentar crearla
                if dbname != 'postgres' and dbname not in databases:
                    print(f"\nLa base de datos '{dbname}' no existe. Intentando crearla...")
                    try:
                        # Cerrar la conexión actual para poder crear la base de datos
                        conn.close()
                        
                        # Conectar como superusuario para crear la base de datos
                        conn = connect_to_db(conn_params)
                        conn.autocommit = True  # Necesario para crear base de datos
                        with conn.cursor() as cur:
                            cur.execute(f"CREATE DATABASE {dbname};")
                            print(f"✅ Base de datos '{dbname}' creada exitosamente")
                            
                            # Verificar que la base de datos se creó
                            cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
                            databases = [row[0] for row in cur.fetchall()]
                            if dbname in databases:
                                print(f"✅ Verificación: '{dbname}' está en la lista de bases de datos")
                            else:
                                print(f"❌ Error: '{dbname}' no aparece en la lista de bases de datos")
                                return False
                    except Exception as e:
                        print(f"❌ Error al crear la base de datos: {str(e)}")
                        return False
                    finally:
                        if conn:
                            conn.close()
                
                # Si la base de datos objetivo es diferente a postgres, reconectar a ella
                if dbname != 'postgres':
                    print(f"\nConectando a la base de datos '{dbname}'...")
                    try:
                        # Crear nuevos parámetros de conexión para la base de datos objetivo
                        target_params = conn_params.copy()
                        target_params['dbname'] = dbname
                        
                        # Intentar conectar a la base de datos objetivo
                        conn = connect_to_db(target_params)
                        with conn.cursor() as cur:
                            cur.execute("SELECT current_database();")
                            current_db = cur.fetchone()
                            print(f"✅ Conectado a la base de datos: {current_db[0]}")
                            
                            # Verificar tablas existentes
                            cur.execute("""
                                SELECT table_name 
                                FROM information_schema.tables 
                                WHERE table_schema = 'public';
                            """)
                            tables = [row[0] for row in cur.fetchall()]
                            print(f"Tablas en la base de datos: {tables or 'Ninguna'}")
                            
                            return True
                    except Exception as e:
                        print(f"❌ Error al conectar a '{dbname}': {str(e)}")
                        return False
                
                return True
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return False

def main():
    # Configuración del pooler de Supabase
    pooler_configs = [
        {
            'name': 'Session Pooler (puerto 5432)',
            'host': 'aws-0-us-east-2.pooler.supabase.com',
            'port': 5432,
            'user': 'postgres.ssibgfbnjfzkayiixqsd',
            'dbname': 'postgres'
        },
        {
            'name': 'Transaction Pooler (puerto 6543)',
            'host': 'aws-0-us-east-2.pooler.supabase.com',
            'port': 6543,
            'user': 'postgres.ssibgfbnjfzkayiixqsd',
            'dbname': 'postgres'
        }
    ]
    
    print("Iniciando pruebas de conexión...")
    print("=" * 50)
    
    for config in pooler_configs:
        print(f"\nProbando {config['name']}...")
        print("-" * 30)
        
        # Crear una copia del config sin el campo 'name'
        conn_config = {k: v for k, v in config.items() if k != 'name'}
        
        # Probar primero con SSL
        if test_connection(**conn_config, use_ssl=True):
            print(f"\n✅ ¡Conexión exitosa encontrada con {config['name']}!")
            print(f"Host: {config['host']}")
            print(f"Puerto: {config['port']}")
            print(f"Usuario: {config['user']}")
            print(f"Base de datos: {config['dbname']}")
            
            # Obtener la contraseña actual del .env
            db_url = os.getenv("SUPABASE_DB_URL")
            parsed = urlparse(db_url)
            password = parsed.password
            
            print("\nActualiza tu .env con estos valores:")
            print(f"SUPABASE_DB_URL=postgresql://{config['user']}:{password}@{config['host']}:{config['port']}/{config['dbname']}?sslmode=require")
            
            # Si la conexión fue exitosa, probar con db_integrada_con_mvc
            print(f"\nProbando conexión a db_integrada_con_mvc con {config['name']}...")
            conn_config['dbname'] = 'db_integrada_con_mvc'
            if test_connection(**conn_config, use_ssl=True):
                print(f"\n✅ ¡Conexión exitosa a db_integrada_con_mvc con {config['name']}!")
                print("\nActualiza tu .env con estos valores:")
                print(f"SUPABASE_DB_URL=postgresql://{config['user']}:{password}@{config['host']}:{config['port']}/{config['dbname']}?sslmode=require")
            return
        
        # Si falla con SSL, intentar sin SSL
        if test_connection(**conn_config, use_ssl=False):
            print(f"\n✅ ¡Conexión exitosa encontrada con {config['name']} (sin SSL)!")
            print(f"Host: {config['host']}")
            print(f"Puerto: {config['port']}")
            print(f"Usuario: {config['user']}")
            print(f"Base de datos: {config['dbname']}")
            print("\nActualiza tu .env con estos valores:")
            print(f"SUPABASE_DB_URL=postgresql://{config['user']}:Mara96via@{config['host']}:{config['port']}/{config['dbname']}")
            return
    
    print("\n❌ No se pudo establecer conexión con ningún pooler")
    print("\nSugerencias:")
    print("1. Verifica que las credenciales sean correctas")
    print("2. Asegúrate de que el firewall no esté bloqueando la conexión")
    print("3. Verifica que la base de datos esté activa en Supabase")
    print("4. Intenta usar una VPN si estás en una región restringida")
    print("5. Verifica en el panel de Supabase la URL correcta de conexión")
    print("6. Asegúrate de que la base de datos esté en la región correcta")
    print("7. Verifica que el pooler esté habilitado en tu proyecto de Supabase")
    print("8. Intenta deshabilitar temporalmente el firewall de Windows")
    print("9. Verifica si tu ISP está bloqueando los puertos 5432 y 6543")

if __name__ == "__main__":
    main() 