import os
from dotenv import load_dotenv
from pathlib import Path

# Obtener la ruta absoluta al directorio del proyecto
BASE_DIR = Path(__file__).resolve().parent

# Cargar variables de entorno
print(f"Buscando archivo .env en: {BASE_DIR}")
load_dotenv(BASE_DIR / ".env")

# Verificar variables importantes
print("\nVariables de entorno:")
print(f"OPENAI_API_KEY: {'✅ Existe' if os.getenv('OPENAI_API_KEY') else '❌ No existe'}")
print(f"OPENAI_BASE_URL: {'✅ Existe' if os.getenv('OPENAI_BASE_URL') else '❌ No existe'}")
print(f"DATABASE_URL: {'✅ Existe' if os.getenv('DATABASE_URL') else '❌ No existe'}")
print(f"SUPABASE_DB_URL: {'✅ Existe' if os.getenv('SUPABASE_DB_URL') else '❌ No existe'}")

# Imprimir valores (ocultando parte de las claves por seguridad)
if os.getenv('OPENAI_API_KEY'):
    key = os.getenv('OPENAI_API_KEY')
    print(f"\nValor de OPENAI_API_KEY: {key[:10]}...{key[-4:]}")
if os.getenv('DATABASE_URL'):
    db_url = os.getenv('DATABASE_URL')
    print(f"\nValor de DATABASE_URL: {db_url[:20]}...{db_url[-20:]}") 