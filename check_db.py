import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

print("Script de vérification de la base de données PostgreSQL")
print("=" * 50)

# Tester la connexion à PostgreSQL
try:
    # D'abord se connecter à la base par défaut 'postgres'
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="root"  # Utilisez le même mot de passe que dans votre .env
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    print(" Connexion à PostgreSQL réussie!")
    
    # Vérifier si la base de données todolist_db existe
    cursor = conn.cursor()
    cursor.execute("SELECT datname FROM pg_database WHERE datname='todolist_db';")
    result = cursor.fetchone()
    
    if result:
        print(" La base de données 'todolist_db' existe déjà.")
    else:
        print(" La base de données 'todolist_db' n'existe pas.")
        print("🔄 Création de la base de données 'todolist_db'...")
        
        # Créer la base de données
        cursor.execute("CREATE DATABASE todolist_db;")
        print(" Base de données 'todolist_db' créée avec succès!")
    
    cursor.close()
    conn.close()
    
    # Tester la connexion à la nouvelle base de données
    test_conn = psycopg2.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="root",
        database="todolist_db"
    )
    print(" Connexion à 'todolist_db' réussie!")
    test_conn.close()
    
    print("\n Configuration PostgreSQL terminée avec succès! Vous pouvez maintenant lancer l'application principale.")
    
except Exception as e:
    print(f" Erreur: {str(e)}")
    print("\n Conseils de débogage:")
    print("  1. Vérifiez que PostgreSQL est installé et en cours d'exécution")
    print("  2. Vérifiez que le mot de passe 'root' est correct pour l'utilisateur 'postgres'")
    print("  3. Si le mot de passe est différent, modifiez-le dans le fichier .env")
    print("  4. Assurez-vous que le port 5432 est bien celui utilisé par PostgreSQL")

input("\nAppuyez sur Entrée pour quitter...")