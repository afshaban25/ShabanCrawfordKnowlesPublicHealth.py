import pandas as pd
import altair as alt


class HealthAnalyzer:
    """Analyze hospital patient records.

    Expected columns (flexible):
    - patient_id
    - admission_date
    - discharge_date
    - outcome (e.g., 'discharge', 'DAMA', 'death')
    - age
    - gender
    - department
    - satisfaction (numeric rating 0-5)
    - diagnosis

    The class holds a cleaned pandas DataFrame in `self.df`.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def clean_data(self):
        df = self.df
        # normalize column names
        df.columns = [c.strip().lower() for c in df.columns]

        # parse dates if present
        for col in ("admission_date", "admit_date", "date_admitted"):
            if col in df.columns:
                df.rename(columns={col: "admission_date"}, inplace=True)
                break
        for col in ("discharge_date", "date_discharged"):
            if col in df.columns:
                df.rename(columns={col: "discharge_date"}, inplace=True)
                break

        if "admission_date" in df.columns:
            df["admission_date"] = pd.to_datetime(df["admission_date"], errors="coerce")
        if "discharge_date" in df.columns:
            df["discharge_date"] = pd.to_datetime(df["discharge_date"], errors="coerce")

        # standardize outcome labels
        if "outcome" in df.columns:
            df["outcome"] = df["outcome"].astype(str).str.lower().str.strip()

        # ensure numeric age
        if "age" in df.columns:
            df["age"] = pd.to_numeric(df["age"], errors="coerce")

        # ensure satisfaction numeric
        if "satisfaction" in df.columns:
            df["satisfaction"] = pd.to_numeric(df["satisfaction"], errors="coerce")

        # compute length of stay (days)
        if "admission_date" in df.columns and "discharge_date" in df.columns:
            df["length_of_stay"] = (df["discharge_date"] - df["admission_date"]).dt.days

        # fill missing simple fields
        if "department" in df.columns:
            df["department"] = df["department"].fillna("Unknown")
        if "gender" in df.columns:
            df["gender"] = df["gender"].fillna("Unknown")

        # drop obvious duplicates
        if "patient_id" in df.columns:
            df = df.drop_duplicates(subset=["patient_id", "admission_date"], keep="first")
        else:
            df = df.drop_duplicates()

        self.df = df
        return df

    def summarize_outcomes(self, by=None):
        """Return counts and percentages of outcomes. Optionally grouped by `by` column(s)."""
        df = self.df
        if by:
            grouped = df.groupby(by)["outcome"].value_counts().unstack(fill_value=0)
            grouped_pct = grouped.div(grouped.sum(axis=1), axis=0)
            return grouped, grouped_pct
        else:
            counts = df["outcome"].value_counts(dropna=False)
            pct = counts / counts.sum()
            return counts, pct

    def aggregate_by(self, column, agg="count", value_col=None):
        """Generic aggregator. If agg=='mean' and value_col provided, compute mean of value_col."""
        df = self.df
        if agg == "count":
            return df.groupby(column).size().sort_values(ascending=False)
        elif agg == "mean" and value_col:
            return df.groupby(column)[value_col].mean().sort_values(ascending=False)
        else:
            return df.groupby(column).agg(agg)

    def admissions_over_time(self, freq="M"):
        """Return a time series (pd.Series) of admission counts resampled at `freq`."""
        df = self.df
        if "admission_date" not in df.columns:
            raise ValueError("admission_date column required")
        s = df.set_index("admission_date").resample(freq).size()
        return s

    def average_satisfaction_by_department(self):
        if "satisfaction" not in self.df.columns or "department" not in self.df.columns:
            return pd.Series(dtype=float)
        return self.df.groupby("department")["satisfaction"].mean().sort_values(ascending=False)

    # Simple plotting helpers using Altair
    def plot_outcomes_by_age_hist(self, age_bin_width=10):
        df = self.df.dropna(subset=["age", "outcome"]) if "age" in self.df.columns else self.df
        if df.empty or "age" not in df.columns:
            return None
        df = df.copy()
        df["age_bin"] = (df["age"] // age_bin_width).astype(int) * age_bin_width
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("age_bin:O", title=f"Age bins ({age_bin_width})"),
            y=alt.Y("count():Q", title="Patients"),
            color="outcome:N",
            tooltip=["age", "outcome", "patient_id"] if "patient_id" in df.columns else ["age", "outcome"]
        ).properties(width=700)
        return chart

    def plot_admissions_over_time(self, freq="M"):
        s = self.admissions_over_time(freq=freq)
        df = s.reset_index()
        df.columns = ["date", "admissions"]
        chart = alt.Chart(df).mark_line(point=True).encode(
            x="date:T",
            y="admissions:Q",
            tooltip=["date", "admissions"]
        ).properties(width=700)
        return chart

    def plot_satisfaction_by_department(self):
        ser = self.average_satisfaction_by_department()
        if ser.empty:
            return None
        df = ser.reset_index()
        df.columns = ["department", "satisfaction"]
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("department:N", sort="-y"),
            y=alt.Y("satisfaction:Q", title="Avg satisfaction"),
            tooltip=["department", "satisfaction"]
        ).properties(width=700)
        return chart
