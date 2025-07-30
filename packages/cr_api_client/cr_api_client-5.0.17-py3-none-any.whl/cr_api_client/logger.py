# -*- coding: utf-8 -*-
import sys

import mantis_logger

logger = mantis_logger.logger.bind(name="cr_api_client")


def configure_logger() -> None:
    # Never send logs from cr_api_client cli to loki
    mantis_logger.config.mantis_logger_config.loki_url = None
    mantis_logger.configure(
        loguru_outputs_handlers=[
            {
                "sink": sys.stdout,
                "format": "|<level>{level: ^7}</level>| {message}",
            },
        ],
        loki_labels={"app": "cr_api_client"},
    )
