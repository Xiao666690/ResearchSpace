"""Set a local DeepSeek key interactively without putting it on the command line."""
import getpass
from dotenv import set_key
from core.common.runtime import BACKEND_ROOT

if __name__ == '__main__':
    key = getpass.getpass('DeepSeek API Key (hidden): ').strip()
    if not key:
        raise SystemExit('No key supplied; configuration unchanged.')
    set_key(str(BACKEND_ROOT / '.env'), 'DEEPSEEK_API_KEY', key)
    print('Saved local configuration. Restart with start_all.ps1.')
