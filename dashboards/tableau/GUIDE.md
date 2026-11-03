# Build the Tableau Public dashboard (Phase 3)

You'll build one dashboard with six views, check each against numbers we already know from SQL, and publish it.
Plan for about 2–3 hours the first time.

## 0. Before you start

1. Create a free account at [public.tableau.com](https://public.tableau.com).
2. Download and install **Tableau Public** (the desktop app) for Mac from the same site.
3. Create the data files:
   ```bash
   cd ~/Desktop/projects/salevora-analytics && source .venv/bin/activate
   python -m salevora.export_tableau
   ```
   This writes three CSVs to `dashboards/tableau/data/`:

   | File | One row per | Rows | Use it for |
   |---|---|---|---|
   | `store_months.csv` | store per month | 33,485 | trends, store types, top stores, competition |
   | `stores.csv` | store | 1,115 | store details: type, assortment, competitor distance |
   | `daily_chain.csv` | day (whole chain) | 942 | weekday and promotion view |

**Why sums, not averages?** The files hold totals (sales, open days, customers). To get "sales per open day"
for any group, divide the *sums*: `SUM(sales) / SUM(open days)`. Averaging averages gives wrong answers,
because a store open 5 days would count as much as a store open 30.

> Tableau tidies column names: `store_type` shows up as **Store Type**. It's the same field.

## 1. Connect the data

1. Open Tableau Public. Under **Connect → To a File**, choose **Text file** and pick `store_months.csv`.
2. Drag `stores.csv` from the left panel onto the canvas next to `store_months`. Tableau draws a line between them
   (a **relationship**). Click the line and check it matches **Store Id = Store Id**.
3. Add a second data source for the daily file: **Data → New Data Source → Text file → `daily_chain.csv`**.
   It's a separate source because it isn't per store.
4. In the data pane, **Store Id** is shown as a number (a *measure*). Right-click it in **both** tables →
   **Convert to Dimension**. A store number is a label, not something to add up.

## 2. Create the calculated fields

**Analysis → Create Calculated Field**, in the `store_months + stores` source:

| Name | Formula |
|---|---|
| Sales per open day | `SUM([Sales]) / SUM([Open Days])` |
| Spend per customer | `SUM([Sales]) / SUM([Customers])` |

In the `daily_chain` source:

| Name | Formula |
|---|---|
| Sales per open store | `SUM([Sales]) / SUM([Open Stores])` |
| Promo label | `IF [Promo] = 1 THEN "Promo" ELSE "No promo" END` |

Format the first three as numbers with no decimals (Spend per customer: 2 decimals):
right-click the field → **Default Properties → Number Format**.

## 3. Build the six sheets

Rename each sheet (double-click its tab) with the name in bold. After each one, check the number in **✅ Check**.
If it matches, your relationships and formulas are right.

### Sheet 1. **KPIs**
- Drag **Sales per open day** onto **Text** on the Marks card. Then add **SUM(Sales)** and **COUNTD(Store Id)**
  (drag Store Id to Text, right-click → Measure → Count (Distinct)).
- ✅ Check: sales per open day **6,956**, total sales **5,873,180,623**, stores **1,115**.

### Sheet 2. **Monthly trend**
- **Columns:** Month. Right-click it → choose the *second* "Month" (green = continuous).
- **Rows:** Sales per open day.
- ✅ Check: hover over December 2013. It should be about **8,613**, the highest point of 2013.
- Then drag **Store Type** onto **Color** to get one line per store type.

### Sheet 3. **Store types**
- **Columns:** Store Type. **Rows:** Sales per open day. Drag Sales per open day onto **Label** too.
- Drag **Spend per customer** onto **Tooltip**.
- ✅ Check: a **6,925**, b **10,231**, c **6,933**, d **6,822**. Tooltips: b spends **5.06** per customer, d **11.25**.

### Sheet 4. **Weekday and promo** (switch to the `daily_chain` source)
- **Columns:** Weekday, then Promo label. **Rows:** Sales per open store. **Color:** Promo label.
- Sort weekdays Monday→Sunday: right-click Weekday → **Sort → Field → Day Of Week, Minimum, Ascending**.
- ✅ Check: Monday promo **9,773** vs no promo **6,223**. Saturday and Sunday have no promo bar.

### Sheet 5. **Top 10 stores**
- **Rows:** Store Id, Store Type, Assortment. **Columns:** Sales per open day (a horizontal bar).
- Sort descending (the sort icon in the toolbar).
- Drag **Store Id** to **Filters → Top tab → By field: Top 10 by Sales per open day**.
- ✅ Check: first row is store **817** (type a, basic) with **21,757**, then 262 and 1114.

### Sheet 6. **Competitor distance**
- **Columns:** Competitor Distance. **Rows:** Sales per open day, also on **Label**.
- ✅ Check: under 500 m **7,614**; 2 km to 10 km **6,705** (the lowest of the four known bands).

## 4. Put the dashboard together

1. **Dashboard → New Dashboard**. On the left, set **Size → Automatic**.
2. Drag in a **Text** object at the top as a title: *Rossmann Store Sales: what drives revenue*.
3. Layout:
   - row 1: **KPIs**
   - row 2: **Monthly trend** (full width)
   - rows 3–4: **Store types**, **Weekday and promo**, **Top 10 stores**, **Competitor distance** in a 2 × 2 grid
4. **Filters:** on the Monthly trend sheet, click its menu (▼) → **Filters → Store Type**. Then on the filter card's
   menu → **Apply to Worksheets → All Using This Data Source**. Now one filter controls every store view.
5. **Interactivity:** on Store types, click the funnel icon (**Use as Filter**). Clicking a bar now filters
   the other views to that store type.
6. Add a small **Text** box at the bottom with 2–3 findings in your own words, plus:
   *Data: Rossmann Store Sales (Kaggle), monthly and daily summaries. Code: github.com/kvvraju24/salevora-analytics*

**Design tips:** one colour per meaning (keep Promo the same colour everywhere), remove gridlines you don't need
(**Format → Lines**), and give every axis a clear title.

## 5. Publish

1. **File → Save to Tableau Public As…** and sign in.
2. Name it **Rossmann Sales Analytics**. It opens in your browser when the upload finishes.
3. On the Tableau Public page, open **Settings** for the workbook and make sure it's visible on your profile.
4. Send Claude the link. It goes into the README, and Phase 3 is done.
5. Optional: save a screenshot as `docs/images/tableau-dashboard.png` so the README can show it.

## What to say about it in an interview

- **Why a summary export?** Tableau Public can't connect to MySQL, and summaries keep the public workbook small
  without republishing the raw dataset.
- **Why `SUM / SUM`?** Ratios must be computed from totals; averaging averages over-weights small groups.
- **Relationship vs join:** a relationship lets Tableau combine `store_months` and `stores` at the right level for
  each view, instead of fixing one join for everything.
- **What it shows:** promotions and the weekday drive daily sales most; type b stores are busy with small baskets;
  nearby competitors go with *higher* sales because both cluster in busy areas (correlation, not cause).
