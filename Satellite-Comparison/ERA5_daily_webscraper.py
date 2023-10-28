import cdsapi

c = cdsapi.Client()
MONTHS = [
    "01", "02", "03", "04", "05", "06",
    "07", "08", "09", "10", "11", "12"]

for month in MONTHS:
    result = c.service(
        "tool.toolbox.orchestrator.workflow",
        params={
            "realm": "user-apps",
            "project": "app-c3s-daily-era5-statistics",
            "version": "master",
            "kwargs": {
                "dataset": "reanalysis-era5-single-levels",
                "product_type": "reanalysis",
                "variable": "2m_temperature",
                "statistic": "daily_mean",
                "year": "2020",
                "month": month,
                "time_zone": "UTC+00:00",
                "frequency": "1-hourly",
                "grid": "0.25/0.25",
                "area": {"lat": [-90, 90], "lon": [-180, 180]}
            },
            "workflow_name": "application"
        })
    c.download(result)
