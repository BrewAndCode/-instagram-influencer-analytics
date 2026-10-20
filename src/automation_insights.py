"""
================================================================================
SR NEXT INTERNSHIP - STEP 5: AUTOMATION INSIGHTS STANDALONE RUNNER
================================================================================
Module:       src/automation_insights.py
Description:  Standalone runner for Part B Automation Insights, ensuring that
              running python3 src/automation_insights.py executes the full
              heuristic risk scoring and validation pipeline.
================================================================================
"""

import sys
import os

# Import main execution logic from anomaly_detection module
from anomaly_detection import main

if __name__ == "__main__":
    main()
