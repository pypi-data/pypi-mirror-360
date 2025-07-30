import os
from click.testing import CliRunner
from unittest.mock import patch, Mock
from tushell.tushellcli import scan_keys


def _invoke_scan_keys(mock_response):
    runner = CliRunner()
    with patch('tushell.tushellcli.requests.get', return_value=mock_response):
        with patch.dict(os.environ, {'EH_API_URL': 'http://test-api', 'EH_TOKEN': 't'}):
            return runner.invoke(scan_keys, ['--pattern', 'test'])


def test_scan_keys_new_api_format():
    resp = Mock()
    resp.status_code = 200
    resp.json.return_value = {'keys': ['0', ['alpha:1', 'beta:2']]}
    result = _invoke_scan_keys(resp)
    assert result.exit_code == 0
    assert 'alpha' in result.output
    assert 'beta' in result.output


def test_scan_keys_legacy_format():
    resp = Mock()
    resp.status_code = 200
    resp.json.return_value = {'keys': ['alpha:1', 'alpha:2']}
    result = _invoke_scan_keys(resp)
    assert result.exit_code == 0
    assert 'alpha' in result.output

