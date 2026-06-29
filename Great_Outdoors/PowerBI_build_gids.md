# Power BI build-gids — Retouren & Cursussen (Great Outdoors)

Deze gids legt stap voor stap uit hoe je in **Power BI Desktop** de twee dashboards bouwt voor
knelpunt 2 (retouren) en knelpunt 4 (cursussen). Je hebt geen code nodig — alles werkt met de
CSV-bestanden die de notebook heeft gemaakt.

> **Geen Power BI? (bv. macOS)** Gebruik Tableau of Qlik Sense met dezelfde CSV's en dezelfde KPI's.

---

## Stap 1 — Data inladen

De notebook `GO_DWH_Retouren_Cursussen_Notebook.ipynb` heeft CSV's gezet in de map
`Great_Outdoors/powerbi_exports/`. Importeer deze:

1. **Home → Get data → Text/CSV**.
2. Laad deze bestanden in:
   - `fact_returns.csv`, `dim_return_reason.csv`
   - `fact_training.csv`, `fact_staff_satisfaction.csv`, `dim_course.csv`, `dim_satisfaction_type.csv`
   - Gedeelde dimensies: `dim_date.csv`, `dim_product.csv`, `dim_region.csv`,
     `dim_customer.csv`, `dim_sales_staff.csv`
3. Klik **Load** (niet Transform — de data is al schoon).

> Alternatief: rechtstreeks op `GO_DWH.db` via een **SQLite ODBC-driver**. De CSV-route is het
> eenvoudigst en wordt hier aangehouden.

---

## Stap 2 — Relaties leggen (Model-weergave)

Open links de **Model**-weergave en sleep de volgende verbindingen (allemaal *één-op-veel*, richting
van dimensie → feit, kruisfilter enkel):

**Retouren (sterschema 1)**
| Van (dimensie) | Kolom | Naar (feit) | Kolom |
|---|---|---|---|
| dim_date | date_key | fact_returns | date_key |
| dim_product | product_key | fact_returns | product_key |
| dim_region | region_key | fact_returns | region_key |
| dim_customer | customer_key | fact_returns | customer_key |
| dim_sales_staff | sales_staff_key | fact_returns | sales_staff_key |
| dim_return_reason | return_reason_key | fact_returns | return_reason_key |

**Cursussen (sterschema 2)**
| Van (dimensie) | Kolom | Naar (feit) | Kolom |
|---|---|---|---|
| dim_course | course_key | fact_training | course_key |
| dim_sales_staff | sales_staff_key | fact_training | sales_staff_key |
| dim_satisfaction_type | satisfaction_type_key | fact_staff_satisfaction | satisfaction_type_key |
| dim_sales_staff | sales_staff_key | fact_staff_satisfaction | sales_staff_key |

> Tip: in `dim_return_reason` en `dim_course` (SCD2) staat mogelijk meer dan één versie per
> business key. Filter visuals desgewenst op `is_current = 1` zodat je de huidige omschrijving toont.

---

## Stap 3 — KPI's als DAX-measures

Maak een lenew tabel **Measures** (Home → Enter data → lege tabel "Measures") en voeg toe
(**Modeling → New measure**). Plak telkens één measure:

### Retouren (knelpunt 2)
```DAX
Aantal geretourneerd = SUM(fact_returns[return_quantity])

Retourwaarde = SUM(fact_returns[return_value])

Gederfde marge = SUM(fact_returns[gross_loss])

Aantal verkocht = SUM(fact_order_sales[quantity])   -- laad hiervoor ook fact_order_sales.csv (optioneel)

Retourpercentage =
DIVIDE ( [Aantal geretourneerd], [Aantal verkocht] )

Aantal retourorders = COUNTROWS(fact_returns)
```
> Heb je `fact_order_sales` niet geladen? Gebruik dan de meegeleverde view-export of bereken het
> retourpercentage per product met de kolom `original_quantity` als benadering:
> `Retour% (benadering) = DIVIDE(SUM(fact_returns[return_quantity]), SUM(fact_returns[original_quantity]))`.

### Cursussen (knelpunt 4)
```DAX
Aantal deelnames = SUM(fact_training[courses_followed])

Cursuskosten = SUM(fact_training[course_cost])

Aantal getrainde medewerkers = DISTINCTCOUNT(fact_training[sales_representative_bk])

Gemiddelde tevredenheid = AVERAGE(fact_staff_satisfaction[satisfaction_score])

Aantal tevredenheidsmetingen = COUNTROWS(fact_staff_satisfaction)
```

---

## Stap 4 — Dashboardpagina 1: "Retouren"

Visuals:
1. **KPI-kaarten** (boven): `Retourwaarde`, `Gederfde marge`, `Aantal geretourneerd`,
   `Retourpercentage`.
2. **Staafdiagram – retourreden**: As = `dim_return_reason[reason_description]`,
   Waarde = `Retourwaarde`. Legenda/kleur op `reason_category`.
3. **Kaart/Map – per regio**: Locatie = `dim_region[country]`, Grootte = `Retourwaarde`.
   (Of een staafdiagram land × retourwaarde.)
4. **Tabel – top producten**: `dim_product[product_name]`, `Aantal verkocht`,
   `Aantal geretourneerd`, `Retourpercentage` (sorteer aflopend op retourpercentage).
5. **Lijndiagram – trend**: As = `dim_date[full_date]` (of jaar/maand-hiërarchie),
   Waarde = `Aantal geretourneerd`.

**Interactiviteit (verplicht):**
- **Slicers**: `dim_date[year_num]`, `dim_region[country]`, `dim_return_reason[reason_category]`,
  `dim_product[product_line]`.
- **Drill-down** op de product-/regio-visual: `product_line → product_type → product_name`
  en `country → region → city`.

---

## Stap 5 — Dashboardpagina 2: "Cursussen & tevredenheid"

Visuals:
1. **KPI-kaarten**: `Aantal deelnames`, `Cursuskosten`, `Aantal getrainde medewerkers`,
   `Gemiddelde tevredenheid`.
2. **Staafdiagram – deelname per cursus**: As = `dim_course[course_description]`,
   Waarde = `Aantal deelnames`, kleur op `course_category`.
3. **Staafdiagram – kosten per categorie**: As = `dim_course[course_category]`,
   Waarde = `Cursuskosten`.
4. **Lijndiagram – tevredenheid per jaar**: As = `dim_satisfaction... year_num`
   (`fact_staff_satisfaction[year_num]`), Waarde = `Gemiddelde tevredenheid`.
5. **Kolomdiagram – effect van training**: maak een berekende groep "aantal cursussen per
   medewerker" (0 / 1-3 / 4+) en zet `Gemiddelde tevredenheid` per groep. Dit toont of meer
   training samengaat met hogere tevredenheid.

**Interactiviteit (verplicht):**
- **Slicers**: `fact_training[year_num]`, `dim_course[course_category]`,
  `dim_sales_staff[branch_country]`.
- **Drill-down** op cursus: `course_category → course_description`.

---

## Stap 6 (optioneel) — Pagina "Pijplijnkwaliteit"

Importeer `logs/go_dwh_extra_etl.log` (Text/CSV, scheidingsteken `|`; kolommen:
tijd, niveau, stap, tabel, actie, aantal, details). Toon:
- Kaart: aantal `ERROR`/`WARNING`-regels (idealiter 0 errors).
- Tabel: laatste run met rijaantallen per tabel (`ROWCOUNT`-regels).
- Lijn: geladen rijen per stap.

Zo maak je de **kwaliteit van de datapijplijn** zichtbaar, zoals de criteria vragen.

---

## Controlegetallen (moeten overeenkomen met je visuals)
- `fact_returns`: **690** retourregels, **13.964** stuks, **€1.179.859** retourwaarde,
  **€348.281** gederfde marge.
- Grootste retourcategorie op waarde: **Kwaliteit** (≈ €590k).
- Hoogste retourpercentage (verkocht ≥ 100): **EverGlow Lamp ≈ 2,46%**.
- `fact_training`: **402** deelnames, **€259.750** (aangenomen) cursuskosten.
- Gemiddelde tevredenheid: 0 cursussen → **2,93**; 1–3 → **3,48**; 4+ → **3,60**.
