import os

API_ADDRESS = os.environ.get('LIMINAL_SHELLSYNC_API_ADDRESS', 'https://shellsync.liminalbios.com/api/v2')
SYNC_ADDRESS = os.environ.get('LIMINAL_SHELLSYNC_ATUIN_ADDRESS', 'https://shellsync.liminalbios.com/atuin/api/v2')

LIMINAL_INSTALLER_SKIP_CLEANUP = os.environ.get('LIMINAL_INSTALLER_SKIP_CLEANUP', 'no')
LIMINAL_INSTALLER_SKIP_ATUIN_IMPORT_HISTORY = os.environ.get('LIMINAL_INSTALLER_SKIP_ATUIN_IMPORT', None)
