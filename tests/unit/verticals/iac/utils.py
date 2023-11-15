from typing import List, Optional

from pygitguardian.iac_models import (
    IaCDiffScanEntities,
    IaCDiffScanResult,
    IaCFileResult,
    IaCScanResult,
    IaCVulnerability,
)

from ggshield.verticals.iac.collection.iac_diff_scan_collection import (
    IaCDiffScanCollection,
)
from ggshield.verticals.iac.collection.iac_path_scan_collection import (
    IaCPathScanCollection,
)


def generate_vulnerability(
    policy_id: Optional[str] = "GG_IAC_0024",
    status: Optional[str] = None,
) -> IaCVulnerability:
    return IaCVulnerability(
        policy="Leaving public access open exposes your service to the internet",
        policy_id=policy_id,
        line_end=35,
        line_start=1,
        description="The API server of an AKS cluster [...]",
        documentation_url=f"https://docs.gitguardian.com/iac-security/policies/{policy_id}",
        component="azurerm_kubernetes_cluster.k8s_cluster",
        severity="HIGH",
        status=status,
    )


def generate_file_result_with_vulnerability(
    filename: str = "file.tf",
    policy_id: Optional[str] = "GG_IAC_0024",
    status: Optional[str] = None,
) -> IaCFileResult:
    return IaCFileResult(
        filename,
        [generate_vulnerability(policy_id, status)],
    )


def generate_path_scan_collection(file_results: List[IaCFileResult]):
    return IaCPathScanCollection(
        ".",
        IaCScanResult(
            id=".",
            type="path_scan",
            iac_engine_version="1.8.0",
            entities_with_incidents=file_results,
        ),
    )


def generate_diff_scan_collection(
    new: List[IaCFileResult],
    unchanged: List[IaCFileResult] = [],
    deleted: List[IaCFileResult] = [],
):
    return IaCDiffScanCollection(
        ".",
        IaCDiffScanResult(
            id=".",
            type="diff_scan",
            iac_engine_version="1.8.0",
            entities_with_incidents=IaCDiffScanEntities(
                unchanged=unchanged,
                deleted=deleted,
                new=new,
            ),
        ),
    )
