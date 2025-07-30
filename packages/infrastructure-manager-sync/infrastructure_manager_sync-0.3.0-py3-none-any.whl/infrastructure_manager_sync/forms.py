from django import forms

from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import CommentField, TagFilterField
from .models import (
    CriticalityChoise,
    EnvironmentChoise,
    FinancialInfoChoise,
    InfrastructureManagerSync,
    InfrastructureManagerSyncVMInfo,
    LicensingChoise,
    SyncType,
    UpdatePrioChoise,
    InfrastructureManagerSyncHostInfo,
)
from utilities.forms.widgets import DatePicker, DateTimePicker
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES, add_blank_choice
from django.utils.translation import gettext as _


class InfrastructureManagerSyncForm(NetBoxModelForm):
    comments = CommentField()

    assign_by_default_to_cluster_tenant = forms.BooleanField(
        label=("Assign untagged vms to cluster tenant"),
        required=False,
        initial=False,
        help_text=_("Assign VMs without tenant tag automatically to the Cluster tenant"),
    )

    class Meta:
        model = InfrastructureManagerSync
        fields = (
            "name",
            "fqdn",
            "username",
            "password",
            "cluster_tenant",
            "entry_type",
            "primary_site",
            "enabled",
            "update_prio",
            "assign_by_default_to_cluster_tenant",
            "comments",
            "tags",
        )


class InfrastructureManagerSyncFilterForm(NetBoxModelFilterSetForm):
    model = InfrastructureManagerSync

    entry_type = forms.MultipleChoiceField(choices=SyncType, required=False)
    update_prio = forms.MultipleChoiceField(choices=UpdatePrioChoise, required=False)

    assign_by_default_to_cluster_tenant = forms.NullBooleanField(
        required=False, label=_("Assign default tenant"), widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES)
    )

    tag = TagFilterField(model)


class InfrastructureManagerSyncVMInfoSyncForm(NetBoxModelForm):
    class Meta:
        model = InfrastructureManagerSyncVMInfo
        fields = (
            "vm",
            "backup_plan",
            "backup_type",
            "criticality",
            "environment",
            "financial_info",
            "licensing",
            "owner",
            "service_info",
            "backup_status",
            "last_backup",
            "deployed_on",
            "deployed_by",
            "billing_reference",
            "ims"
        )
        widgets = {
            "deployed_on": DatePicker(),
            "last_backup": DateTimePicker(),
        }


class InfrastructureManagerSyncVMInfoFilterForm(NetBoxModelFilterSetForm):
    model = InfrastructureManagerSyncVMInfo

    environment = forms.MultipleChoiceField(choices=EnvironmentChoise, required=False)
    criticality = forms.MultipleChoiceField(choices=CriticalityChoise, required=False)
    financial_info = forms.MultipleChoiceField(choices=FinancialInfoChoise, required=False)
    licensing = forms.MultipleChoiceField(choices=LicensingChoise, required=False)

    ims = forms.ModelChoiceField(
        queryset=InfrastructureManagerSync.objects.all(),
        required=False,
        label=_('ims'),
    )

    owner = forms.CharField(max_length=100, required=False)


class InfrastructureManagerSyncHostInfoSyncForm(NetBoxModelForm):
    class Meta:
        model = InfrastructureManagerSyncHostInfo
        fields = ("host", "build_number")


class InfrastructureManagerSyncHostInfoFilterForm(NetBoxModelFilterSetForm):
    model = InfrastructureManagerSyncHostInfo
