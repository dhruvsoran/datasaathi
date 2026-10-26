"""Generate the SYNTHETIC campus utilities dataset (not official records)."""
import numpy as np, pandas as pd
rng = np.random.default_rng(42)
months = pd.period_range("2025-04", "2026-03", freq="M").astype(str)
# building: (base kWh/month, base kL water/month, kind)
B = {
    "Boys Hostel": (48000, 2600, "hostel"), "Girls Hostel": (41000, 2300, "hostel"),
    "Engineering Block": (36000, 900, "academic"), "CS Lab Block": (29000, 520, "academic"),
    "Library": (18000, 350, "academic"), "Admin Block": (12000, 300, "academic"),
    "Cafeteria": (15000, 1400, "service"), "Sports Complex": (9000, 700, "service"),
}
season = dict(zip(months, [1.10, 1.30, 1.35, 1.20, 1.15, 1.15, 1.00, 0.85, 0.80, 0.80, 0.85, 0.95]))
vac = {"2025-05": {"hostel": .7, "academic": .85, "service": .8}, "2025-06": {"hostel": .4, "academic": .6, "service": .55}}
rows = []
for b, (e, w, kind) in B.items():
    for m in months:
        f = vac.get(m, {}).get(kind, 1.0)
        if b == "Girls Hostel" and m in vac:   # planted anomaly: full load during vacation
            f = .97
        rows.append((b, m, int(e * season[m] * f * rng.normal(1, .04)),
                     int(w * (0.8 + 0.2 * season[m]) * f * rng.normal(1, .04))))
df = pd.DataFrame(rows, columns=["building", "month", "electricity_kwh", "water_kl"])
df = df[~((df.building == "Library") & (df.month == "2026-03"))]          # missing observation
df.loc[(df.building == "Cafeteria") & (df.month == "2025-08"), "water_kl"] = np.nan  # missing value
df.to_csv("data/campus_utilities.csv", index=False)
print(df.shape)

# ---- messy demo copy (for the Data Trust check demo) ----
m = df.copy()
m.loc[(m.building == "Engineering Block") & (m.month == "2025-07"), "electricity_kwh"] *= 10       # typo / unit error
m.loc[(m.building == "Sports Complex") & (m.month == "2025-11"), "water_kl"] = -120                  # impossible value
m = m[~((m.building == "CS Lab Block") & (m.month == "2025-10"))]                                    # missing row
m = pd.concat([m, m[(m.building == "Admin Block") & (m.month == "2025-09")]])                        # duplicate row
m.to_csv("data/messy_demo.csv", index=False)
print("messy", m.shape)
