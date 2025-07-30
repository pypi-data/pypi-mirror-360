from functools import cached_property

from haplohub import (
    ApiClient,
    BiomarkerApi,
    CohortApi,
    Configuration,
    FileApi,
    MemberApi,
    MemberReportApi,
    MetadataApi,
    ModelApi,
    SampleApi,
    UploadApi,
    VariantApi,
)

from haplohub_cli import settings
from haplohub_cli.auth.token_storage import TokenStorage
from haplohub_cli.config.config_manager import config_manager


class Client:
    token_storage = TokenStorage(settings.CREDENTIALS_FILE)

    @cached_property
    def client(self):
        config = Configuration(
            host=config_manager.config.api_url,
            access_token=self.token_storage.get_access_token(),
        )
        return ApiClient(config)

    @cached_property
    def cohort(self):
        return CohortApi(self.client)

    @cached_property
    def file(self):
        return FileApi(self.client)

    @cached_property
    def upload(self):
        return UploadApi(self.client)

    @cached_property
    def model(self):
        return ModelApi(self.client)

    @cached_property
    def variant(self):
        return VariantApi(self.client)

    @cached_property
    def sample(self):
        return SampleApi(self.client)

    @cached_property
    def member(self):
        return MemberApi(self.client)

    @cached_property
    def biomarker(self):
        return BiomarkerApi(self.client)

    @cached_property
    def member_report(self):
        return MemberReportApi(self.client)

    @cached_property
    def metadata(self):
        return MetadataApi(self.client)


client = Client()
