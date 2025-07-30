from __future__ import annotations

import socket
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, Optional, Union


def get_local_host() -> Optional[Dict[str, Union[str, int]]]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0)
    try:
        sock.connect(("10.254.254.254", 1))
    except Exception:
        return None
    else:
        return {
            "_hostname": socket.gethostname(),
            "_ip": sock.getsockname()[0],
        }
    finally:
        sock.close()
