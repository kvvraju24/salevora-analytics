# Findings: 10 business questions

Each answer comes from a query in [`sql/queries/`](../sql/queries/). Run any of them with:

```bash
python -m salevora.run_query sql/queries/01_yearly_sales.sql
```

**Per open day** means sales divided by the days a store was open. This leaves out closed days (sales = 0) and isn't distorted by the 2014 data gap (Q7).

## Q1. How did sales change from year to year?
[`01_yearly_sales.sql`](../sql/queries/01_yearly_sales.sql)

| Year | Total sales | Per open day | Per open day, Jan–Jun |
|---|---:|---:|---:|
| 2013 | 2,302,876,084 | 6,814 | 6,662 |
| 2014 | 2,180,804,896 | 7,025 | 6,875 |
| 2015 (to 31 Jul) | 1,389,499,643 | 7,088 | 7,098 |

**Answer:** comparing the same months (January–June), sales per open day grew **3.2% a year**, in both 2014 and 2015. The 2014 *total* is lower than 2013 only because 180 stores have no data for July–December 2014 (Q7). That's a data gap, not a real drop.

**Lesson:** never compare totals across periods with different store counts or lengths.

## Q2. Which 10 stores sell the most on an average open day?
[`02_top_stores.sql`](../sql/queries/02_top_stores.sql)

**Answer:** store **817** (type a) leads with 21,757 per open day, followed by **262** (type b, 20,719) and **1114** (type a, 20,667). The top 10 each sell 2.4–3.1 times the chain average of 6,956. Seven of the ten carry the extended assortment (c). Stores 262 and 562 were open on all 942 days, Sundays included.

**Why it matters:** a forecast error at one of these stores costs far more than at a small store. That's why WAPE, which weights errors by sales, is a headline metric in Phase 4.

## Q3. How do store type and assortment relate to sales and customers?
[`03_store_type_assortment.sql`](../sql/queries/03_store_type_assortment.sql)

**Answer:**
- **Type b** (only 17 stores) sells the most per day (8,639–17,970) and draws far more customers: 1,805–3,105 a day, against 584–856 for the other types. But each customer spends the least: 4.18–6.17 per visit.
- **Type d** is the opposite: the fewest customers (584–619 a day) but the highest spend per customer (11.02–11.38).
- The **extended assortment (c)** sells more than basic (a) within store types a (+16%), c (+3%) and d (+9%).

The data doesn't explain what the store types mean. Type b's pattern (many customers, small baskets, and in Q2 two type-b stores open every single day) looks like busy locations such as stations, but that is a guess.

## Q4. How much higher are sales on promotion days, for each weekday?
[`04_promo_by_weekday.sql`](../sql/queries/04_promo_by_weekday.sql)

| Day | Promo | No promo | Uplift |
|---|---:|---:|---:|
| Monday | 9,773 | 6,223 | +57.1% |
| Tuesday | 8,277 | 5,716 | +44.8% |
| Wednesday | 7,685 | 5,617 | +36.8% |
| Thursday | 7,598 | 5,750 | +32.1% |
| Friday | 7,744 | 6,344 | +22.1% |
| Saturday | — | 5,875 | no promos |
| Sunday | — | 8,225 | no promos |

**Answer:** promotions run **Monday to Friday only**. Promo days average 22–57% more sales, and the gap is biggest on Monday. Sunday's high average comes from the few stores that open on Sundays.

**Careful:** this is an association, not proof that promotions *cause* the increase. Promotions could, for example, be scheduled for weeks that would be busy anyway.

## Q5. What happens to sales on public holidays?
[`05_holidays.sql`](../sql/queries/05_holidays.sql)

| | Store-days | Open | Sales per open day |
|---|---:|---:|---:|
| No public holiday | 986,159 | 85.5% | 6,954 |
| Public holiday | 20,260 | 3.4% | 8,487 |
| Easter | 6,690 | 2.2% | 9,888 |
| Christmas | 4,100 | 1.7% | 9,744 |

**Answer:** almost every store **closes** on public holidays; only 1.7–3.4% of store-days are open. The few stores that do open sell 22–42% more than on a normal open day.

**For the model:** a holiday mostly means "closed", and a closed store's forecast is 0.

## Q6. Do stores with a competitor nearby sell less?
[`06_competition_distance.sql`](../sql/queries/06_competition_distance.sql)

| Nearest competitor | Stores | Sales per open day |
|---|---:|---:|
| Under 500 m | 218 | 7,614 |
| 500 m to 2 km | 283 | 6,920 |
| 2 km to 10 km | 424 | 6,705 |
| 10 km or more | 187 | 6,825 |
| Unknown | 3 | 5,482 |

**Answer:** no. Stores with a competitor **within 500 m sell the most**, 14% more than the 2–10 km group. The likely reason is that close competitors cluster in busy city centres, so location drives both. This is a classic case of correlation without causation: a nearby competitor doesn't raise your sales.

**Limitation:** each store has one distance value, so competitors that opened during 2013–2015 aren't separated out.

## Q7. Which stores are missing days in their history, and when?
[`07_missing_days.sql`](../sql/queries/07_missing_days.sql)

**Answer:** 934 of 1,115 stores have all 942 days. The other 181:
- **180 stores** (store 13, for example) have 758 days and **no rows at all from 1 July to 31 December 2014**. That's exactly the 184 missing days.
- **Store 988** is missing only 1 January 2013.

**Why it matters:** any chart of *total* sales dips in the second half of 2014 even though real sales didn't fall. Phase 4 has to handle this gap when it builds features from history.

## Q8. How did average sales change from month to month?
[`08_monthly_trend.sql`](../sql/queries/08_monthly_trend.sql)

**Answer:** **December is the peak every year**: 8,613 (2013) and 8,604 (2014) per open day, 25% and 14% above November. January then falls by 24% and 20%. Outside December, months range between about 6,200 and 7,500.

July 2014 shows only a normal −5.0% change even though 180 stores stop reporting. That shows the per-open-day measure does its job.

**For the model:** our forecast window, August–September, is one of the quieter periods (6,360–6,760 in 2013 and 2014).

## Q9. Which are the top 3 stores within each store type?
[`09_top3_per_store_type.sql`](../sql/queries/09_top3_per_store_type.sql)

| Type | 1st | 2nd | 3rd |
|---|---|---|---|
| a | 817 (21,757) | 1114 (20,667) | 251 (19,123) |
| b | 262 (20,719) | 562 (17,970) | 733 (14,933) |
| c | 523 (15,531) | 595 (15,019) | 560 (13,613) |
| d | 842 (18,575) | 261 (12,616) | 903 (11,738) |

**Answer:** type d's leader, **store 842, sells 47% more than the next type-d store**. It's an outlier worth a closer look before modelling. Type c's best stores sell well below the leaders of the other types.

*SQL note:* `RANK()` gives tied stores the same rank; `ROW_NUMBER()` would number them 1, 2, 3 anyway.

## Q10. Was chain-wide demand rising or falling at the end of the history?
[`10_moving_average.sql`](../sql/queries/10_moving_average.sql)

**Answer:** **roughly flat.** Through June–July 2015 the 14-day moving average stayed between 6.32 and 6.95 million a day, ending at 6.67 million.

The 7-day average still swings between about 5.5 and 8.0 million because promotions usually run **every other week**: `promo_share` is 1.00 for a week of weekdays, then 0.00 for the next. Only a 14-day window covers a full promo cycle. A one-off check of the whole history found that promotions are always chain-wide (all stores or none), and the weekly alternation breaks only 13 times in 135 weeks. The dip on Thursday 4 June 2015 (3.5 million) is Corpus Christi, a public holiday in several German states.

## What this means for the forecast (Phase 4)

- **Strong inputs:** day of week, promo (and its two-week cycle), holidays and closures, store type and assortment, month (December).
- **Not an input:** customers. They're unknown for future days.
- **Handle with care:** the July–December 2014 gap, outlier stores such as 842, and the fact that promo effects are associations.
- **Baseline to beat:** these patterns explain why a simple store × weekday × promo average is already a strong forecast.
