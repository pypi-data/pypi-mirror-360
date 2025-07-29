from aos_signer.signer import commands
from aos_signer.signer.errors import SignerError

from pathlib import Path
p = Path('c:\\Users\\vmyky\\work\\test_s\\meta\\config.yaml')
commands.sign_service(p, 'c:\\Users\\vmyky\\work\\test_s\\src', '.')
