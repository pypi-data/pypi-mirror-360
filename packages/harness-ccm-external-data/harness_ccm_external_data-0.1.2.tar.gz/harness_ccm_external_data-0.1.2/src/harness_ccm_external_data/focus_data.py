from typing import Dict, Sequence, Optional
import hashlib
from datetime import datetime
from dateutil.relativedelta import relativedelta

import pandas as pd
from requests import post, get, put, delete

HARNESS_FIELDS = [
    "BillingAccountId",
    "BillingAccountName",
    "BillingPeriodEnd",
    "BillingPeriodStart",
    "ChargeCategory",
    "ChargePeriodStart",
    "ChargePeriodEnd",
    "ConsumedQuantity",
    "EffectiveCost",
    "ProviderName",
    "ResourceId",
    "RegionName",
    "ServiceName",
    "SubAccountId",
    "SkuId",
    "SubAccountName",
    "Tags",
]

file_limit = 20000000


class Focus:
    """
    Load in a cloud provider focus billing export
    Apply modifications to the data as needed for processing
    Render a CSV that fits Harness' standards for external data ingestion

    Attributes:
        provider (str): Name of the provider name (eg AWS, GCP, etc)
        data_source (str): Name of the data source (eg AWS Master Payer)
        filename (str): Path to the focus billing export
        provider_type (str): Type of provider (default CUSTOM)
        invoice_period (str): Invoice period (default MONTHLY)
        mapping (Dict[str, str]): Mapping of focus fields to harness fields
        separator (str): CSV separator
        skip_rows (int | Sequence[int]): Rows to skip in the CSV
        cost_multiplier (float): Multiplier for cost
        converters (Dict[str, callable]): Custom converters for columns
        validate (bool): Validate columns
        harness_platform_api_key (str): API key for Harness platform
        harness_account_id (str): Account ID for Harness
    """

    def __init__(
        self,
        provider: str,
        data_source: str,
        filename: str,
        provider_type: str = "CUSTOM",
        invoice_period: str = "MONTHLY",
        provider_uuid: str = None,
        mapping: Dict[str, str] = {},
        separator: str = ",",
        skip_rows: int | Sequence[int] = None,
        cost_multiplier: float = 1.0,
        converters: Dict[str, callable] = {},
        validate: bool = True,
        harness_platform_api_key: str = None,
        harness_account_id: str = None,
    ):
        self.provider = provider
        self.data_source = data_source
        self.provider_type = provider_type
        self.invoice_period = invoice_period
        self.provider_uuid = provider_uuid
        self.filename = filename
        self.cost_multiplier = cost_multiplier
        self.converters = converters
        self.harness_platform_api_key = harness_platform_api_key
        self.harness_account_id = harness_account_id

        # Stub for generated content
        self.harness_focus_content: pd.DataFrame = None

        # sanitize mappings
        mapping = mapping if mapping else {}
        self.mapping = {**{x: x for x in HARNESS_FIELDS}, **mapping}

        # if provider dosnt exist, create it
        if self.provider_uuid is None:
            for provider in self._list_providers():
                if (
                    provider["name"] == self.data_source
                    and provider["providerName"] == self.provider
                ):
                    self.provider_uuid = provider["uuid"]
                    break
            else:
                self._create_provider()

        # restrict fields to ones supported by ccm
        # allow disabling verification for instances when ccm moves faster than the code
        if validate:
            for field in mapping:
                if field not in HARNESS_FIELDS:
                    print(
                        f"WARNING: Field {field} is not a recognized harness focus field. Will be ignored"
                    )
                    del self.mapping[field]

        baseline_converters = {
            # make sure provider is set
            self.mapping["ProviderName"]: lambda x: self.provider
            if not x
            else x,
        }
        if cost_multiplier:
            # apply given cost multiplier
            baseline_converters[self.mapping["EffectiveCost"]] = (
                lambda x: pd.to_numeric(x) * cost_multiplier
            )

        self.billing_content = pd.read_csv(
            filename,
            sep=separator,
            engine="python",
            skiprows=skip_rows,
            # any converters specified by the user will override built-in ones
            converters={**baseline_converters, **converters},
        )

    def render(self) -> pd.DataFrame:
        """
        Create the Harness-aligned FOCUS CSV
        """

        self.harness_focus_content = pd.DataFrame()
        for focus_field, source_field in self.mapping.items():
            if source_field in self.billing_content.columns:
                self.harness_focus_content[focus_field] = self.billing_content[
                    source_field
                ]
            else:
                # Default value for missing columns
                self.harness_focus_content[focus_field] = source_field

        return self.harness_focus_content

    def render_file(self, filename: str):
        """
        Save the Harness-CSV to a file
        """

        if self.harness_focus_content is None:
            self.render().to_csv(filename, index=False)
        else:
            self.harness_focus_content.to_csv(filename, index=False)

    def _list_providers(self):
        """
        List all providers in the account
        """
        resp = post(
            "https://app.harness.io/gateway/ccm/api/externaldata/provider/list",
            params={
                "accountIdentifier": self.harness_account_id,
            },
            headers={
                "x-api-key": self.harness_platform_api_key,
                "content-type": "application/json",
            },
        )

        if resp.status_code == 200:
            return resp.json().get("data", [])
        else:
            print(f"Failed to list providers: {resp.status_code} - {resp.text}")
            return []

    def _create_provider(self):
        """
        Given a provider name and type, create a provider in harness
        """

        resp = post(
            "https://app.harness.io/gateway/ccm/api/externaldata/provider",
            params={
                "accountIdentifier": self.harness_account_id,
            },
            headers={
                "x-api-key": self.harness_platform_api_key,
                "content-type": "application/json",
            },
            json={
                "externalDataProvider": {
                    "name": self.data_source,
                    "providerType": self.provider_type,
                    "providerName": self.provider,
                    "invoicePeriod": self.invoice_period,
                }
            },
        )

        if resp.status_code == 200:
            self.provider_uuid = resp.json().get("data", {}).get("uuid")
            return self.provider_uuid
        else:
            print(f"Failed to get provider UUID: {resp.status_code} - {resp.text}")
            return None

    def _delete_provider(self):
        """
        Delete an external data provider

        THIS WILL DELETE DATA IN HARNESS
        """

        resp = delete(
            f"https://app.harness.io/gateway/ccm/api/externaldata/provider/{self.provider_uuid}",
            params={
                "accountIdentifier": self.harness_account_id,
            },
            headers={
                "x-api-key": self.harness_platform_api_key,
                "content-type": "application/json",
            },
        )

        if resp.status_code != 200:
            print(f"Failed to delete provider: {resp.status_code} - {resp.text}")
            return False
        else:
            self.provider_uuid = None
            return True

    def __repr__(self):
        if self.harness_focus_content is None:
            return self.billing_content.__repr__()
        else:
            return self.harness_focus_content.__repr__()

    def list_files(self):
        """
        List all files in the provider
        """

        resp = post(
            "https://app.harness.io/gateway/ccm/api/externaldata/provider/filesinfo",
            params={
                "accountIdentifier": self.harness_account_id,
            },
            headers={
                "x-api-key": self.harness_platform_api_key,
                "content-type": "application/json",
            },
            json={"providerList": [self.provider_uuid]},
        )

        if resp.status_code == 200:
            return resp.json().get("data", {}).get(self.provider_uuid, [])
        else:
            print(f"Failed to list files: {resp.status_code} - {resp.text}")
            return []

    def _get_md5_hash(self, csv_content: str) -> str:
        """
        Generate MD5 hash of the CSV content.
        """

        return hashlib.md5(csv_content.encode("utf-8")).hexdigest()

    def _get_signed_url(
        self, provider_id: str, invoice_period: str, object_name: str
    ) -> Optional[str]:
        """
        Get signed URL for uploading the file.
        """

        resp = get(
            "https://app.harness.io/gateway/ccm/api/externaldata/signedurl",
            params={
                "providerId": provider_id,
                "accountIdentifier": self.harness_account_id,
                "invoicePeriod": invoice_period,
                "objectName": object_name,
            },
            headers={
                "x-api-key": self.harness_platform_api_key,
                "content-type": "application/json",
            },
        )

        if resp.status_code == 200:
            return resp.json().get("data")
        else:
            print(f"Failed to get signed URL: {resp.status_code} - {resp.text}")
            return None

    def _upload_to_gcs(self, signed_url: str, csv_content: str) -> bool:
        """
        Upload CSV content to GCS using the signed URL.
        """

        resp = put(signed_url, data=csv_content, headers={"Content-Type": "text/csv"})

        if resp.status_code == 200:
            return True
        else:
            print(f"Failed to upload to GCS: {resp.status_code} - {resp.text}")
            return False

    def _mark_upload_complete(
        self,
        provider_id: str,
        provider_name: str,
        invoice_period: str,
        object_name: str,
        md5_hash: str,
        cloud_storage_path: str,
    ) -> bool:
        """
        Mark the file upload as complete in Harness.
        """

        resp = post(
            "https://app.harness.io/gateway/ccm/api/externaldata/filesinfo",
            params={"accountIdentifier": self.harness_account_id},
            headers={
                "x-api-key": self.harness_platform_api_key,
                "content-type": "application/json",
            },
            json={
                "externalDataFiles": {
                    "accountId": self.harness_account_id,
                    "name": object_name,
                    "fileExtension": "CSV",
                    "signedUrlUsed": True,
                    "md5": md5_hash,
                    "providerId": provider_id,
                    "providerName": provider_name,
                    "cloudStoragePath": cloud_storage_path,
                    "uploadStatus": "COMPLETE",
                    "invoiceMonth": invoice_period,
                }
            },
        )

        if resp.status_code == 200:
            return True
        else:
            print(f"Failed to mark upload complete: {resp.status_code} - {resp.text}")
            return False

    def _get_invoice_period(self) -> str:
        """
        Calculate the invoice period from BillingPeriodStart and BillingPeriodEnd.
        Returns a string in the format YYYYMMDD-YYYYMMDD where it's the first day of the month
        the data is for and the first day of the next month.
        """
        try:
            # Get the first row's BillingPeriodStart and BillingPeriodEnd
            start_date_str = self.harness_focus_content["BillingPeriodStart"].iloc[0]

            # Parse the dates
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")

            # Calculate the first day of the month for the start date
            period_start = start_date.replace(day=1)

            # Calculate the first day of the next month
            period_end = (period_start + relativedelta(months=1)).replace(day=1)

            # Format as YYYYMMDD-YYYYMMDD
            return f"{period_start.strftime('%Y%m%d')}-{period_end.strftime('%Y%m%d')}"

        except Exception as e:
            print(f"Error calculating invoice period: {str(e)}")
            return None

    def _trigger_ingestion(self, provider_id: str, invoice_periods: list) -> bool:
        """
        Trigger the actual data ingestion in Harness.
        """

        resp = post(
            "https://app.harness.io/gateway/ccm/api/externaldata/dataingestion",
            params={"accountIdentifier": self.harness_account_id},
            headers={
                "x-api-key": self.harness_platform_api_key,
                "content-type": "application/json",
            },
            json={
                "accountId": self.harness_account_id,
                "invoicePeriod": invoice_periods,
                "providerId": provider_id,
            },
        )

        if resp.status_code == 200:
            return True
        else:
            print(f"Failed to trigger ingestion: {resp.status_code} - {resp.text}")
            return False

    def upload(self, force: bool = False):
        """
        Upload the Harness-CSV data to Harness

        Args:
            force (bool): Whether to force upload even if data already exists

        Returns:
            bool: True if all steps completed successfully, False otherwise
        """

        # Ensure we have the rendered content
        if self.harness_focus_content is None:
            self.render()

        csv_content = self.harness_focus_content.to_csv(index=False)
        md5_hash = self._get_md5_hash(csv_content)

        # Ensure we have a provider
        if self.provider_uuid is None:
            if not self._create_provider():
                return False

        # If no invoice_period is provided, calculate it from the data
        this_invoice_period = self._get_invoice_period()
        if not this_invoice_period:
            print("Failed to determine invoice period from data")
            return False

        # Check if file has already been uploaded
        for file in self.list_files():
            if file["md5"] == md5_hash:
                print(f"File already uploaded: {md5_hash}")
                return False

        # Generate a unique object name
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        object_name = (
            f"focusv1_{self.provider.lower()}-{self.harness_account_id}-{timestamp}.csv"
        )

        # Step 1: Get signed URL
        signed_url = self._get_signed_url(
            self.provider_uuid, this_invoice_period, object_name
        )
        if not signed_url:
            print("Failed to get signed URL")
            return False

        # Step 2: Upload to GCS
        if not self._upload_to_gcs(signed_url, csv_content):
            print("Failed to upload to GCS")
            return False

        # Extract the GCS URL from the signed URL (remove query parameters)
        cloud_storage_path = signed_url.split("?")[0]

        # Step 3: Mark upload as complete
        if not self._mark_upload_complete(
            self.provider_uuid,
            self.provider,
            this_invoice_period,
            object_name,
            md5_hash,
            cloud_storage_path,
        ):
            print("Failed to mark upload as complete")
            return False

        # Step 4: Trigger ingestion
        if not self._trigger_ingestion(self.provider_uuid, [this_invoice_period]):
            print("Failed to trigger ingestion")
            return False

        return True
