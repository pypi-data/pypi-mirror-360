from therix.core.constants import DataSourceMaster
from .pipeline_component import DataSource


class PDFDataSource(DataSource):
    def __init__(self, config):
        super().__init__(DataSourceMaster.PDF, config)


class PDFDIDataSource(DataSource):
    def __init__(self, config):
        super().__init__(DataSourceMaster.PDF_DI, config)


class TextDataSource(DataSource):
    def __init__(self, config):
        super().__init__(DataSourceMaster.TEXT, config)        


class JsonDataSource(DataSource):
    def __init__(self, config):
        super().__init__(DataSourceMaster.JSON, config)               


class WebsiteDataSource(DataSource):
    def __init__(self, config):
        super().__init__(DataSourceMaster.WEBSITE, config)


class CSVDataSource(DataSource):
    def __init__(self, config):
        super().__init__(DataSourceMaster.CSV, config)


class DatabaseDataSource(DataSource):
    def __init__(self, config):
        super().__init__(DataSourceMaster.DATABASE, config)


class DOCXDataSource(DataSource):
    def __init__(self, config):
        super().__init__(DataSourceMaster.DOCX, config)


class YoutubeDataSource(DataSource):
    def __init__(self, config):
        super().__init__(DataSourceMaster.YOUTUBE, config)
