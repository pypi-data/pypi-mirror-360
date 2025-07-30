import sys
import os

from intelliw.utils import iuap_request
from intelliw.utils.storage_service import StorageService


def download(url, path, dry: bool = True):
    try:
        if not dry:
            raise Exception()
        iuap_request.download(url=url, output_path=path)
    except Exception:
        StorageService(url, "download").download(path)
    return


if __name__ == '__main__':
    file_url = sys.argv[1]
    save_path = sys.argv[2]
    download(file_url, save_path)
