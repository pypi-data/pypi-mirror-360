import os
import subprocess

from pywander.utils.command_utils import get_command_path

import logging

logger = logging.getLogger(__name__)

def convert_tex_to_epub(infile, metadata, resource):
    pandoc_command = get_command_path('pandoc')
    infile_name = os.path.splitext(infile)[0]
    process_cmd = [pandoc_command, '-o', f'{infile_name}.epub', f'--metadata-file={metadata}', f'--resource-path={resource}', infile]
    logger.debug(f'start call cmd {process_cmd}')
    subprocess.check_call(process_cmd)
    return f'{infile_name}.epub'

