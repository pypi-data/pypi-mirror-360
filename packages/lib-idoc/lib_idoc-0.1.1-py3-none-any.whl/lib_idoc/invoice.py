import re
import logging
from ftplib import FTP
from lib_utilys import clean_special_characters, read_json
from lib_invoice import Invoice

logger = logging.getLogger(__name__)

class IDOC:
    def __init__(self):
        self.static_segment_start = None
        self.static_segment_end = None
        self.dynamic_segment = None
        self.xml_filename = None
        self.xml = None
        self._initialize_segments()

    def _initialize_segments(self, startseg_path: str, dynseg_path: str, endseg_path: str):
        """Initializes IDOC segments."""
        try:
            with open(startseg_path, 'r') as file:
                self.static_segment_start = file.read()
            with open(dynseg_path, 'r') as file:
                self.dynamic_segment = file.read()
            with open(endseg_path, 'r') as file:
                self.static_segment_end = file.read()
        except Exception:
            logger.exception("Failed to initialize IDOC segments")

    def _replace_static_start(self, kvpairs: dict):
        """Replaces the static start segment of the IDOC."""
        try:
            for key, value in kvpairs.items():
                if value is not None:
                    self.static_segment_start = self.static_segment_start.replace(f"[{key}]", str(value))
            self.static_segment_start = re.sub(r'\[.*?\]', '', self.static_segment_start)
        except Exception:
            logger.exception("Error replacing static start segment")

    def _replace_dynamic(self, kvpairs: dict):
        """Replaces the dynamic segment of the IDOC."""
        try:
            dynamic, position_counter = '', 10
            for material in kvpairs['Material_list']:
                template = self.dynamic_segment
                for key, value in material.items():
                    if value is not None:
                        template = template.replace(f"[{key}]", str(value))
                template = template.replace('[Position_number]', str(position_counter))
                template = re.sub(r'\[.*?\]', '', template)
                position_counter += 10
                dynamic += template
            self.dynamic_segment = dynamic
        except Exception:
            logger.exception("Error replacing dynamic segment")

    def _replace_static_end(self, kvpairs: dict):
        """Replaces the static end segment of the IDOC."""
        try:
            for key, value in kvpairs.items():
                if value is not None:
                    self.static_segment_end = self.static_segment_end.replace(f"[{key}]", str(value))
            self.static_segment_end = re.sub(r'\[.*?\]', '', self.static_segment_end)
        except Exception:
            logger.exception("Error replacing static end segment")

    def _configure_filename(self, invoice: Invoice):
        """Configures the filename of the IDOC."""
        try:
            self.xml_filename = f"{invoice.kvpairs['Creditor_number']}-{invoice.kvpairs['Debtor_international_location_number']}.{invoice.kvpairs['Invoice_number']}.xml"
            self.xml_filename = clean_special_characters(self.xml_filename)
        except Exception:
            logger.exception("Error configuring filename")

    def configure_idoc(self, invoice: Invoice):
        """Creates the IDOC."""
        try:
            self._configure_filename(invoice)
            self._replace_static_start(invoice.kvpairs)
            self._replace_dynamic(invoice.kvpairs)
            self._replace_static_end(invoice.kvpairs)

            self.xml = self.static_segment_start + self.dynamic_segment + self.static_segment_end
        except Exception:
            logger.exception("Error creating IDOC")