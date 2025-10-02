import sqlite3

# Connect to SQLite database
connection = sqlite3.connect('monopoly_game.db')
cursor = connection.cursor()

# SQL commands
sql_script = '''
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS Player;
DROP TABLE IF EXISTS Property;
DROP TABLE IF EXISTS Game;
DROP TABLE IF EXISTS Board;

-- Create a single Player table instead of separate ones
CREATE TABLE Player (
    player_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    position INTEGER DEFAULT 0,
    balance INTEGER DEFAULT 1500,
    in_jail BOOLEAN DEFAULT 0
);

-- Property table with correct foreign key reference
CREATE TABLE Property (
    property_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price INTEGER NOT NULL,
    owner_id INTEGER DEFAULT NULL,
    mortgaged BOOLEAN DEFAULT 0,
    FOREIGN KEY (owner_id) REFERENCES Player(player_id) ON DELETE SET NULL
);

CREATE TABLE Game (
    game_id INTEGER PRIMARY KEY,
    current_turn INTEGER,
    num_players INTEGER,
    FOREIGN KEY (current_turn) REFERENCES Player(player_id)
);

CREATE TABLE Board (
    position INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

-- Insert board positions
INSERT INTO Board (position, name) VALUES
    (0, 'Start'), (1, 'Old Trafford'), (2, '256 Club'), (3, 'Gay Village'),
    (4, 'Kilburn'), (5, 'RNCM'), (6, 'Jail'), (7, 'Piccadilly Gardens'), 
    (8, 'Square Gardens'), (9, 'Aquatic Centre'), (10, 'Stopford Building'), 
    (11, 'Nancy Rothwell Building'), (12, 'Free Parking'), 
    (13, 'University Place'), (14, 'Student Union'), (15, 'Crawford Building'),
    (16, 'Gorilla Club'), (17, 'Sugden Sports Centre'), (18, 'Go to Jail'),
    (19, 'Etihad Stadium'), (20, 'Alan Gilbert Learning Commons'), 
    (21, 'Vita Living'), (22, 'Oxford Road Railway Station'), (23, 'Main Library');

-- Insert properties
INSERT INTO Property (name, price, owner_id, mortgaged) VALUES
    ('Old Trafford', 20, NULL, 0), ('256 Club', 50, NULL, 0), ('Gay Village', 60, NULL, 0),
    ('Kilburn', 75, NULL, 0), ('RNCM', 65, NULL, 0), ('Piccadilly Gardens', 70, NULL, 0),
    ('Aquatic Centre', 25, NULL, 0), ('Stopford Building', 80, NULL, 0), ('University Place', 50, NULL, 0),
    ('Square Gardens', 70, NULL, 0), ('Nancy Rothwell Building', 75, NULL, 0),
    ('Student Union', 50, NULL, 0), ('Crawford Building', 70, NULL, 0), ('Gorilla Club', 40, NULL, 0),
    ('Sugden Sports Centre', 80, NULL, 0), ('Arndale', 100, NULL, 0), ('Etihad Stadium', 100, NULL, 0),
    ('Alan Gilbert Learning Commons', 80, NULL, 0), ('Vita Living', 70, NULL, 0),
    ('Oxford Road Station', 90, NULL, 0);
'''

# Execute the SQL script
try:
    cursor.executescript(sql_script)
    connection.commit()
    print("Database setup successful!")
except Exception as e:
    print(f"Error: {e}")
finally:
    connection.close()
