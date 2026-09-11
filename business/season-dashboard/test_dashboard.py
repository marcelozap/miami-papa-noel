"""Run the dashboard's synthetic JavaScript contracts in the offline battery."""
from pathlib import Path
import subprocess


def test_dashboard_javascript_contracts():
    result = subprocess.run(['node', '--test', str(Path(__file__).with_name('test-dashboard.cjs'))],
                            capture_output=True, text=True, encoding='utf-8', timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
