#!/usr/bin/env python


import io
import logging
import pathlib
from argparse import Namespace

# Typing
from typing import Optional, Union

# Own modules
from rtfparse import entities, utils

# Setup logging
logger = logging.getLogger(__name__)


class Rtf_Parser:
    def __init__(self, rtf_path: Optional[pathlib.Path] = None, rtf_file: Optional[Union[io.BufferedReader, io.BytesIO]] = None) -> None:
        self.rtf_path = rtf_path
        self.rtf_file = rtf_file
        if not (self.rtf_path or self.rtf_file):
            raise ValueError("Need `rtf_path` or `rtf_file` argument")
        self.ENCODING_PROBE = 48  # look for encoding information in the first 48 bytes of the file

    def read_encoding(self, file: Union[io.BufferedReader, io.BytesIO]) -> str:
        probed = file.read(self.ENCODING_PROBE)
        group = entities.Group("cp1252", io.BytesIO(probed))
        recognized_encodings = ("ansi", "ansicpg", "mac", "pc", "pca")
        # Gather all control words, which could define an encoding:
        names = tuple(filter(lambda item: isinstance(item, entities.Control_Word) and item.control_name in recognized_encodings, group.structure))
        # Check if the ANSI code page is set as a parameter of any of the control words:
        encoding = None
        for item in names:
            # if any item is a Control_Word which has a parameter, we assume that this is the parameter of \ansicpg, and that corresponds to the codepage we are looking for
            if item.parameter:
                param = item.parameter
            else:
                param = None
        if param:
            if param == 65001:
                logger.warning("Found encoding '65001', but often this is actually 'cp1252', so I'm taking that")
                encoding = "cp1252"
            else:
                encoding = f"cp{param}"
        else:
            if names[0].control_name == "ansi":
                logger.warning("Found encoding 'ansi', but often this is actually 'cp1252', so I'm taking that")
                encoding = "cp1252"
            elif names[0].control_name == "mac":
                encoding = "mac_roman"
            elif names[0].control_name == "pc":
                encoding = "cp437"
            elif names[0].control_name == "pca":
                encoding = "cp850"
        file.seek(0)
        logger.info(f"recognized encoding {encoding}")
        return encoding

    def parse_file(self) -> entities.Group:
        if self.rtf_path is not None:
            file = open(self.rtf_path, mode="rb")
        elif self.rtf_file is not None:
            file = self.rtf_file
        else:
            file = io.BytesIO(b"")
        parsed_object = utils.what_is_being_parsed(file)
        logger.info(f"Parsing the structure of {parsed_object}")
        try:
            encoding = self.read_encoding(file)
            self.parsed = entities.Group(encoding, file)
        except Exception as err:
            logger.exception(err)
            self.parsed = Namespace()
            self.parsed.structure = list()
        finally:
            if self.rtf_path is not None:
                logger.debug(f"Closing {parsed_object}")
                file.close()
            logger.info(f"Structure of {parsed_object} parsed")
            return self.parsed


if __name__ == "__main__":
    pass
