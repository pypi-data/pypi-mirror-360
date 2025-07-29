import logging

from pywander.config import load_all_config

logger = logging.getLogger(__name__)

from .ref_scripts import REF_SCRIPTS_DICT


def process_text(infile):
    config = load_all_config()

    process_text_config = config.get('PROCESS_TEXT')

    if process_text_config:
        for item in process_text_config:
            op = item.get('OPERATION')

            if op in REF_SCRIPTS_DICT:
                op_func = REF_SCRIPTS_DICT[op]
                op_func_kwargs = item

                op_func(infile, **op_func_kwargs)
            else:
                logger.error(f"Unknown operation: {op}")
