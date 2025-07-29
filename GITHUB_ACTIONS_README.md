# CRIMENET GitHub Actions Setup

## Automated Daily Crime Data Scraping

This repository includes a GitHub Actions workflow that automatically runs the CRIMENET crime data scraper daily at 11 PM GMT.

### Features

- **Scheduled Execution**: Runs automatically every day at 11 PM GMT
- **Manual Trigger**: Can be triggered manually from the GitHub Actions tab
- **Automatic Commits**: Results are automatically committed back to the repository
- **Archival**: Each run creates archived copies with timestamps
- **Artifacts**: Results are uploaded as downloadable artifacts (retained for 30 days)
- **Summary Reports**: Each run generates a summary with key metrics

### Workflow Details

The workflow (`crimenet-daily-scraper.yml`) performs the following steps:

1. **Setup Environment**: 
   - Checks out the repository
   - Sets up Python 3.13
   - Creates virtual environment
   - Installs dependencies from `requirements.txt`

2. **Execute Scraper**:
   - Runs `main.py`
   - Scrapes crime headlines from configured sources
   - Applies ML classification with confidence thresholds
   - Generates CSV output with crime data

3. **Process Results**:
   - Archives results with timestamps
   - Commits updated data to repository
   - Creates summary report
   - Uploads artifacts

### Manual Execution

To manually trigger the workflow:

1. Go to the **Actions** tab in your GitHub repository
2. Select **CRIMENET Daily Crime Data Scraper**
3. Click **Run workflow**
4. Choose log level (info/debug) if needed
5. Click **Run workflow**

### Output Files

- `data/crime_news.csv`: Latest crime headlines with confidence scores
- `log`: Application logs from the latest run
- `archives/crime_news_YYYY-MM-DD_HH-MM-SS.csv`: Archived results
- `archives/log_YYYY-MM-DD_HH-MM-SS.txt`: Archived logs

### Configuration

To modify the schedule or behavior:

1. Edit `.github/workflows/crimenet-daily-scraper.yml`
2. Update the cron expression in the `schedule` section:
   ```yaml
   schedule:
     - cron: '0 23 * * *'  # 11 PM GMT daily
   ```
3. Commit the changes

### Monitoring

- Check the **Actions** tab for execution history
- View run summaries for quick metrics
- Download artifacts for detailed analysis
- Monitor commit history for data updates

### Troubleshooting

If the workflow fails:

1. Check the Actions tab for error logs
2. Verify that all required secrets are configured
3. Ensure the model file `model/NBCrime.pkl` exists
4. Check that dependencies in `requirements.txt` are correct

The workflow includes automatic failure notifications and will create a summary even if the run fails.
