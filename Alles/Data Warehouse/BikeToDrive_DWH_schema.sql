PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date TEXT NOT NULL UNIQUE,
    day_of_month INTEGER NOT NULL,
    month_num INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    quarter_num INTEGER NOT NULL,
    year_num INTEGER NOT NULL,
    week_num INTEGER NOT NULL,
    day_name TEXT NOT NULL,
    is_weekend INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_filiaal (
    filiaal_key INTEGER PRIMARY KEY AUTOINCREMENT,
    filiaal_bk INTEGER NOT NULL UNIQUE,
    naam TEXT,
    adres TEXT,
    provincie TEXT
);

CREATE TABLE IF NOT EXISTS dim_klant (
    klant_key INTEGER PRIMARY KEY AUTOINCREMENT,
    klant_bk INTEGER NOT NULL,
    naam TEXT,
    adres TEXT,
    woonplaats TEXT,
    geslacht TEXT,
    geboortedatum TEXT,
    leeftijd INTEGER,
    leeftijdsklasse TEXT,
    valid_from TEXT NOT NULL,
    valid_to TEXT,
    is_current INTEGER NOT NULL DEFAULT 1,
    UNIQUE (klant_bk, valid_from)
);

CREATE TABLE IF NOT EXISTS dim_monteur (
    monteur_key INTEGER PRIMARY KEY AUTOINCREMENT,
    monteur_bk INTEGER NOT NULL,
    naam TEXT,
    woonplaats TEXT,
    uurloon REAL,
    looncategorie TEXT,
    filiaal_bk INTEGER,
    valid_from TEXT NOT NULL,
    valid_to TEXT,
    is_current INTEGER NOT NULL DEFAULT 1,
    UNIQUE (monteur_bk, valid_from)
);

CREATE TABLE IF NOT EXISTS dim_leverancier (
    leverancier_key INTEGER PRIMARY KEY AUTOINCREMENT,
    leverancier_bk INTEGER NOT NULL UNIQUE,
    naam TEXT,
    adres TEXT,
    woonplaats TEXT
);

CREATE TABLE IF NOT EXISTS dim_fabrikant (
    fabrikant_key INTEGER PRIMARY KEY AUTOINCREMENT,
    fabrikant_bk INTEGER NOT NULL UNIQUE,
    naam TEXT,
    adres TEXT,
    plaats TEXT
);

CREATE TABLE IF NOT EXISTS dim_product (
    product_key INTEGER PRIMARY KEY AUTOINCREMENT,
    product_bk TEXT NOT NULL UNIQUE,
    product_type TEXT NOT NULL,
    source_domain TEXT NOT NULL,
    natural_key INTEGER NOT NULL,
    naam TEXT,
    soort TEXT,
    merk TEXT,
    model_type TEXT,
    kleur TEXT,
    standaardprijs REAL,
    inkoopprijs REAL,
    prijssegment TEXT,
    winstmarge_pct REAL,
    leverancier_bk INTEGER,
    fabrikant_bk INTEGER
);

CREATE TABLE IF NOT EXISTS fact_verkoop (
    verkoop_key INTEGER PRIMARY KEY AUTOINCREMENT,
    verkoop_bk TEXT NOT NULL UNIQUE,
    date_key INTEGER NOT NULL,
    klant_key INTEGER NOT NULL,
    monteur_key INTEGER NOT NULL,
    filiaal_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    verkoop_type TEXT NOT NULL,
    aantal INTEGER NOT NULL,
    verkoopprijs_eenheid REAL NOT NULL,
    omzet_bedrag REAL NOT NULL,
    kostprijs_eenheid REAL,
    brutowinst_bedrag REAL,
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (klant_key) REFERENCES dim_klant(klant_key),
    FOREIGN KEY (monteur_key) REFERENCES dim_monteur(monteur_key),
    FOREIGN KEY (filiaal_key) REFERENCES dim_filiaal(filiaal_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key)
);

CREATE TABLE IF NOT EXISTS fact_inkoop (
    inkoop_key INTEGER PRIMARY KEY AUTOINCREMENT,
    inkoop_bk TEXT NOT NULL UNIQUE,
    date_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    leverancier_key INTEGER,
    fabrikant_key INTEGER,
    inkoop_type TEXT NOT NULL,
    aantal INTEGER NOT NULL,
    inkoopprijs_eenheid REAL,
    inkoopbedrag REAL,
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    FOREIGN KEY (leverancier_key) REFERENCES dim_leverancier(leverancier_key),
    FOREIGN KEY (fabrikant_key) REFERENCES dim_fabrikant(fabrikant_key)
);

CREATE TABLE IF NOT EXISTS fact_onderhoud (
    onderhoud_key INTEGER PRIMARY KEY AUTOINCREMENT,
    onderhoud_bk TEXT NOT NULL UNIQUE,
    date_key INTEGER NOT NULL,
    monteur_key INTEGER NOT NULL,
    filiaal_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    starttijd TEXT,
    eindtijd TEXT,
    duur_uren REAL,
    uurloon REAL,
    arbeidskosten REAL,
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (monteur_key) REFERENCES dim_monteur(monteur_key),
    FOREIGN KEY (filiaal_key) REFERENCES dim_filiaal(filiaal_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key)
);