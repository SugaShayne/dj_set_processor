"""
Database initialization for the Tracklist Generator module.
"""

import mysql.connector
from mysql.connector import errorcode

def create_database(config):
    """
    Create the database for storing audio fingerprints.
    
    Args:
        config: Database configuration dictionary
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Connect to MySQL server
        conn = mysql.connector.connect(
            host=config["database"]["host"],
            user=config["database"]["user"],
            password=config["database"]["password"]
        )
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        try:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config['database']['database']}")
            print(f"Database {config['database']['database']} created successfully.")
        except mysql.connector.Error as err:
            print(f"Failed creating database: {err}")
            return False
            
        # Use the database
        cursor.execute(f"USE {config['database']['database']}")
        
        # Create tables
        tables = {}
        tables['songs'] = (
            "CREATE TABLE IF NOT EXISTS `songs` ("
            "  `id` INT AUTO_INCREMENT,"
            "  `name` VARCHAR(255) NOT NULL,"
            "  `file_path` VARCHAR(500),"
            "  `fingerprinted` TINYINT DEFAULT 0,"
            "  `date_created` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "  `date_modified` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,"
            "  PRIMARY KEY (`id`)"
            ") ENGINE=InnoDB"
        )
        
        tables['fingerprints'] = (
            "CREATE TABLE IF NOT EXISTS `fingerprints` ("
            "  `id` INT AUTO_INCREMENT,"
            "  `song_id` INT NOT NULL,"
            "  `hash` BINARY(20) NOT NULL,"
            "  `offset` INT NOT NULL,"
            "  `date_created` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "  `date_modified` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,"
            "  PRIMARY KEY (`id`),"
            "  KEY `idx_fingerprints_hash` (`hash`),"
            "  KEY `idx_fingerprints_song_id` (`song_id`),"
            "  CONSTRAINT `fk_fingerprints_song_id` FOREIGN KEY (`song_id`) "
            "     REFERENCES `songs` (`id`) ON DELETE CASCADE"
            ") ENGINE=InnoDB"
        )
        
        # Create tables
        for table_name in tables:
            table_description = tables[table_name]
            try:
                print(f"Creating table {table_name}: ", end='')
                cursor.execute(table_description)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print("already exists.")
                else:
                    print(err.msg)
                    return False
            else:
                print("OK")
        
        cursor.close()
        conn.close()
        return True
        
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        return False

if __name__ == "__main__":
    from config import DATABASE_CONFIG
    create_database(DATABASE_CONFIG)
