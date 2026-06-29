-- =====================================================================================
--  Great Outdoors - Source Data Model (SDM): NIEUWE KLASSEN voor knelpunt 2 & 4
-- =====================================================================================
--  Herkansing Data Engineering - Opdracht 2
--
--  Dit script beschrijft de SDM-klassen (CREATE TABLE met PK/FK) die nodig zijn voor de
--  twee nieuwe knelpunten:
--     * Knelpunt 2 - Retourstromen
--     * Knelpunt 4 - Cursussen / effect van training
--
--  De bron-data hiervoor wordt al door de bestaande SDM-pijplijn
--  (GO_SDM_Pipeline_Notebook.ipynb) ingeladen in GO_SDM.db (tabellen met prefix
--  sales_ / staff_). Dit script legt de FORMELE structuur + sleutels + de
--  database-OVERSCHRIJDENDE associaties vast, zoals gevraagd in de criteria.
--
--  Inlaadstrategie: het SDM wordt volledig gereset en opnieuw gevuld (truncate & load),
--  consistent met de bestaande SDM-pijplijn.
-- =====================================================================================

PRAGMA foreign_keys = ON;

-- -------------------------------------------------------------------------------------
--  KNELPUNT 2 - RETOUREN
-- -------------------------------------------------------------------------------------
--  Bron: GO_SALES-data.sqlite -> tabellen return_reason en returned_item.

-- Reden van retour (referentietabel).
CREATE TABLE IF NOT EXISTS return_reason (
    return_reason_code      INTEGER PRIMARY KEY,
    return_description_en   TEXT NOT NULL
);

-- Eén geretourneerde orderregel.
CREATE TABLE IF NOT EXISTS returned_item (
    return_code         INTEGER PRIMARY KEY,
    return_date         TEXT,           -- tekst in bron (bv. '01-Aug-2024 04:10:24 AM')
    order_detail_code   INTEGER NOT NULL,
    return_reason_code  INTEGER NOT NULL,
    return_quantity     INTEGER,
    -- Database-OVERSCHRIJDENDE associatie binnen de sales-bron:
    FOREIGN KEY (order_detail_code)  REFERENCES order_details(order_detail_code),
    FOREIGN KEY (return_reason_code) REFERENCES return_reason(return_reason_code)
);

-- -------------------------------------------------------------------------------------
--  KNELPUNT 4 - CURSUSSEN / TRAINING
-- -------------------------------------------------------------------------------------
--  Bron: GO_STAFF-data.sqlite -> course, training, satisfaction, satisfaction_type,
--        sales_representative, sales_office.

-- Cursus (referentietabel).
CREATE TABLE IF NOT EXISTS course (
    course_code         INTEGER PRIMARY KEY,
    course_description  TEXT NOT NULL
);

-- Type tevredenheid (referentietabel, 1..5).
CREATE TABLE IF NOT EXISTS satisfaction_type (
    satisfaction_type_code         INTEGER PRIMARY KEY,
    satisfaction_type_description  TEXT NOT NULL
);

-- Verkoopkantoor (locatie van een medewerker).
CREATE TABLE IF NOT EXISTS sales_office (
    sales_office_code   INTEGER PRIMARY KEY,
    street              TEXT,
    addition            TEXT,
    city                TEXT,
    region              TEXT,
    zipcode             TEXT,
    country_code        INTEGER
);

-- Medewerker / sales representative.
-- LET OP: dit is dezelfde persoon als 'sales_staff' in de SALES-database, maar de
-- tabel- en sleutelnaam verschillen per database (de casus-uitdaging).
CREATE TABLE IF NOT EXISTS sales_representative (
    sales_representative_code  INTEGER PRIMARY KEY,
    first_name                 TEXT,
    last_name                  TEXT,
    position_en                TEXT,
    work_phone                 TEXT,
    extension                  TEXT,
    fax                        TEXT,
    email                      TEXT,
    date_hired                 TEXT,
    sales_office_code          INTEGER,
    manager_code               INTEGER,
    FOREIGN KEY (sales_office_code) REFERENCES sales_office(sales_office_code),
    FOREIGN KEY (manager_code)      REFERENCES sales_representative(sales_representative_code)
);

-- Gevolgde cursus per medewerker per jaar (koppel-/feitachtige klasse).
CREATE TABLE IF NOT EXISTS training (
    year                       INTEGER NOT NULL,
    sales_representative_code  INTEGER NOT NULL,
    course_code                INTEGER NOT NULL,
    PRIMARY KEY (year, sales_representative_code, course_code),
    FOREIGN KEY (sales_representative_code) REFERENCES sales_representative(sales_representative_code),
    FOREIGN KEY (course_code)               REFERENCES course(course_code)
);

-- Tevredenheid per medewerker per jaar.
CREATE TABLE IF NOT EXISTS satisfaction (
    year                       INTEGER NOT NULL,
    sales_representative_code  INTEGER NOT NULL,
    satisfaction_type_code     INTEGER NOT NULL,
    PRIMARY KEY (year, sales_representative_code),
    FOREIGN KEY (sales_representative_code) REFERENCES sales_representative(sales_representative_code),
    FOREIGN KEY (satisfaction_type_code)    REFERENCES satisfaction_type(satisfaction_type_code)
);

-- =====================================================================================
--  DATABASE-OVERSCHRIJDENDE ASSOCIATIES (documentatie t.b.v. het SDM-diagram)
-- =====================================================================================
--  Deze associaties lopen OVER de grenzen van de bron-databases heen. De namen en
--  PK-invulling verschillen per database; daarom worden ze hieronder expliciet benoemd.
--
--  1) returned_item.order_detail_code  -->  order_details.order_detail_code
--     (binnen GO_SALES) Multipliciteit: 0..* retouren bij 1 orderregel.
--
--  2) training.sales_representative_code  -->  sales_staff.sales_staff_code
--     STAFF-database 'sales_representative'  ==  SALES-database 'sales_staff'
--     Andere tabelnaam, ANDERE kolomnaam, ZELFDE persoon/code.
--     Multipliciteit: 1 medewerker volgt 0..* trainingen.
--
--  3) satisfaction.sales_representative_code  -->  sales_representative.sales_representative_code
--     en via (2) dus ook gelijk aan sales_staff.sales_staff_code.
--     Multipliciteit: 1 medewerker heeft per jaar 0..1 tevredenheidsmeting.
--
--  4) sales_office.country_code  -->  country.country_code (SALES-database)
--     Multipliciteit: 1 land heeft 0..* verkoopkantoren.
--
--  In het Power BI / DWH worden associatie (2) en (3) gebruikt om training en
--  tevredenheid te koppelen aan dezelfde medewerker-dimensie (dim_sales_staff).
-- =====================================================================================

-- -------------------------------------------------------------------------------------
--  Reset-/laadstrategie (consequent toegepast, zoals in de SDM-pijplijn):
--    DELETE FROM <tabel>;  -- leegmaken
--    -- daarna opnieuw vullen vanuit de bron
--  Verwijder in omgekeerde FK-volgorde om sleutels niet te schenden:
-- -------------------------------------------------------------------------------------
-- DELETE FROM training;
-- DELETE FROM satisfaction;
-- DELETE FROM returned_item;
-- DELETE FROM sales_representative;
-- DELETE FROM sales_office;
-- DELETE FROM course;
-- DELETE FROM satisfaction_type;
-- DELETE FROM return_reason;
