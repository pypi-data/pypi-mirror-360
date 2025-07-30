import django_filters
from netbox.filtersets import NetBoxModelFilterSet
from .models import (
    InfrastructureManagerSync,
    InfrastructureManagerSyncVMInfo,
    InfrastructureManagerSyncHostInfo,
)


class InfrastructureManagerSyncFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = InfrastructureManagerSync
        fields = ("name", "fqdn", "username", "primary_site", "build_number", "version", "enabled", "update_prio")

        assign_by_default_to_cluster_tenant = django_filters.BooleanFilter(
            label="Assigned tenant by default",
        )


class InfrastructureManagerSyncVMInfoFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = InfrastructureManagerSyncVMInfo
        fields = (
            "environment",
            "criticality",
            "financial_info",
            "licensing",
            "owner",
            "backup_status",
            "deployed_by",
            "billing_reference",
            "ims"
        )


class InfrastructureManagerSyncHostInfoFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = InfrastructureManagerSyncHostInfo
        fields = ("memory", "build_number")
