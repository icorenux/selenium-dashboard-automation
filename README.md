# Datadog Dashboard Team Tag Updater

This project helps you extract and update team tags on your Datadog dashboards using Selenium and the Datadog API.

## 🛠️ Requirements

- **Python**: `3.11.6`
- **Selenium**: `selenium==4.33.0`
- A working installation of `Google Chrome` and the appropriate `ChromeDriver` for your version.

## 📦 Setup

1. Clone this repository.

2. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   Make sure your `requirements.txt` contains:

   ```
   selenium==4.33.0
   ```

3. Download Selenium IDE on: https://chromewebstore.google.com/detail/selenium-ide/mooikfkahbdckldjjndioackbalphokd

## 🚀 How to Use

### 1. Log in to Datadog

Before running the script, **make sure you are already logged in** to the [Datadog UI](https://app.datadoghq.com/) using your default browser (Google Chrome is required).\
The Selenium script will use your existing browser session to extract dashboard data.

### 2. Run the dashboard extraction script

Run the following Python script to extract dashboard URLs and associated team information:

```bash
python get-dashboard-teams.py
```

This script will:

- Launch Chrome via Selenium.
- Access your Datadog dashboard list.
- Extract dashboard URLs and associated team names (based on tags or page structure).
- Generate a `dashboard-list.txt` file in the following format:

```
https://app.datadoghq.com/dashboard/abc-123,devops
https://app.datadoghq.com/dashboard/xyz-456,infra
```

> ⚠️ Make sure to keep the browser session open until the script finishes.

### 3. Update Dashboards with Team Tags

After generating `dashboard-list.txt`, run the following shell script to patch team tags on each dashboard via the Datadog API:

```bash
./patch-dashboard.sh
```

This script will:

- Loop through each line in `dashboard-list.txt`
- Download each dashboard definition using the API
- Add or update the `"team:<team_name>"` tag if it is missing
- Upload the modified dashboard JSON back to Datadog

Make sure you have the following environment variables configured in the script:

```bash
DD_API_KEY=""
DD_APP_KEY=""
```

Replace the empty strings with your actual Datadog API and Application Keys.

## ✅ Notes

- Make sure your Datadog account has the necessary permissions to read and update dashboards.
- This script assumes each dashboard should have **one** `team:<team_name>` tag based on the input file.
- Use responsibly in production environments.

## 📟 Output

- `dashboard_<ID>.json`: the original downloaded dashboard definition
- `dashboard_<ID>_modified.json`: the patched version with the updated tags

