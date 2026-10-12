# STA PL 3MW dashboard

Live: https://chaleamchonppp-tech.github.io/PEA-GMD-N2_STA-PL-3MW/

The modern dashboard uses `dashboard.css` and `dashboard.js` alongside the generated `index.html`. Keep these files, `dashboard-future.css`, `pea-tou-2026.js`, and `assets/fonts` when publishing. Run `python redesign_dashboard.py` to regenerate the page; this preserves the modern presentation. The interface is Thai-only; previous saved English preferences are ignored. Brand names, source filenames and standard measurement units are retained.

The clean futuristic white/purple/green interface has four main sections: overview, energy, inverters, and data (including checks). The overview combines the earlier four energy cards and chart/balance layout with VOLTA-style horizontal navigation and a purple site summary. Graphs provide pointer, touch, and keyboard value inspection. The daily power-flow chart stacks solar supply/export above zero and solar/grid consumption below zero; the negative sign is a display convention, not a negative meter reading. Detailed tables are available in expandable sections. The overview and energy rings use the September 2026 meter-report totals; hourly charts remain estimates from four quarter-hour samples. PEA purple (#74045F), gold (#C7911B), and white follow the supplied identity book. Logos retain their original proportions on white backgrounds.

GitHub Pages: main branch, root. English default; Thai language switch. Fixed viewport and paginated tables. Latest data means the latest measurement, not deployment time.

Daily import accepts complete SolarEdge power CSV, 96 unique quarter-hour samples per day with kW/MW headers. Imports replace matching hourly dates in local browser storage only. Download the updated hourly CSV from Files & updates. Monthly energy totals remain from the source monthly report.

To update the public September dataset, replace matching files under raw/Solar (3MW-prefixed daily files), run `python analyze.py` then `python redesign_dashboard.py`, and commit raw files, data and index.html to main. Requires Python and pandas. analyze.py currently validates the September 2026 period; a different month needs the corresponding monthly reports and a period configuration change. Uploading raw CSV alone does not update the published dashboard.

The light future theme uses locally served IBM Plex Sans Thai Regular and SemiBold, with its SIL Open Font License included in assets/fonts. No font CDN is required.

Daily energy totals use segmented capsule bars with exact-value tooltips. Daily power-flow plots remain stacked areas. The inverter section uses two-unit monthly comparison cards, a daily comparison table and a selectable fleet list, without inverter charts. Percentage differences use unit B as the baseline; a zero baseline displays no percentage.

Navigation uses short nonblocking transitions, an animated active indicator, browser history and section deep links (#overview, #daily, #inverters, #insights, #data, #compare). Scroll positions are retained per section during the session. Reduced-motion preferences disable the animations.

Dimensional gradients, layered shadows and raised edges add depth to surfaces. Energy rings show only the percentage at their centers, with titles, energy totals and secondary metrics laid out separately. Typography uses darker colors and larger sizes.

The energy page supports one day or an inclusive date range with an hourly time window repeated every day (start inclusive, end exclusive). Defaults: 06:00–18:00. Selected energy totals are estimates from hourly power; monthly meter totals on the overview remain unchanged. Multi-day power plots show the mean for each selected clock hour, not the summed power. Daily bars sum only the selected hours.

TOU classification uses local site times: weekdays 09:00–22:00 On-Peak, all other hours Off-Peak; Saturdays, Sundays and the 17 weekday holiday dates listed in the user-supplied PEA 2569 calendar are Off-Peak all day. The calendar was issued on 24 December 2025 and transcribed into pea-tou-2026.js. Compensatory holidays and additional cabinet special holidays are not inferred. Dates outside 2026 remain unclassified. This compares energy, not tariff cost.

## Separate transformer datasets

`build_feeder_data.py` reads all 30 original CSVs in `raw/500kVA` and creates `data/500kva.json` and `feeder-data.js`. Read each column's MW/kW unit, normalize to kW, and integrate 15-minute samples as kW × 0.25 h. Coverage is 2,880 distinct timestamps for September 2026. This source has no meter-energy totals, site ID, feeder number, DC rating, or inverter records. Its energy totals are estimates, never combined with the existing 3,000 kVA report. Minor power-balance differences are retained as supplied (rounded MW readings); do not force balance. The user confirmed 3,000 kVA = Feeder 9 and 500 kVA = Feeder 10. Browser imports and time-filter state are isolated by transformer dataset.
