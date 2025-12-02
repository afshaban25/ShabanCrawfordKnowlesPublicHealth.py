# Public Health: Patient & Hospital Data Dashboard

This project provides a `HealthAnalyzer` class and a Streamlit dashboard for exploring hospital/patient data.

Quick start

1. Create a Python 3.11 virtual environment (recommended). Example using system `python3.11`:

```bash
python3.11 -m venv .venv311
source .venv311/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

2. Run the Streamlit app

```bash
streamlit run main.py
```

3. Upload your CSV or use the sample dataset built into the app.

Notes
- If you run into build issues installing packages, consider using Conda and `conda install -c conda-forge streamlit pandas altair` to avoid compilation.
- The app provides example charts: outcome distribution by age, admissions over time, and average satisfaction by department.

Submission naming and deployment

- Rename or copy `app.py` to meet assignment naming convention, e.g. `Afshaban2_PublicHealth.py` or `AllGroupMembersLastNames_ProjectTopic.py`.
- Verify the dashboard works locally before deploying to Streamlit Cloud.
- To deploy to Streamlit Cloud (share.streamlit.io), push your repo to GitHub and follow Streamlit Cloud's "New app" flow; set the run command to `streamlit run app.py`.

Screenshots and slides

- Capture screenshots of the charts (browser or OS screenshot) and include them in your submission zip.
- Convert `slides.md` to PowerPoint with Pandoc (optional) or manually create an 8–12 slide PowerPoint from `slides.md`.
