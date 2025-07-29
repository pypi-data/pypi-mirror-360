from django import forms
from netbox.forms import NetBoxModelForm
from utilities.forms.widgets import DatePicker
from utilities.forms.fields import DynamicModelChoiceField, CommentField, SlugField
from utilities.forms.rendering import FieldSet, TabbedGroups
from django.utils.html import format_html
from django.db.models import Q
from dcim.models import Manufacturer, Device
from virtualization.models import VirtualMachine
from netbox_license.models.license import License
from netbox_license.models.licenseassignment import LicenseAssignment
from netbox_license.models.licensetype import LicenseType
from ..choices import (
    VolumeTypeChoices,
    PurchaseModelChoices,
    LicenseModelChoices,
    VolumeRelationChoices,
    LicenseStatusChoices,
    LicenseAssignmentStatusChoices,
    AssignmentKindChoices

)

__all__ = (
    'LicenseForm',
    'LicenseAssignmentForm',
    'LicenseTypeForm',
)

# ---------- LicenseType ----------

class LicenseTypeForm(NetBoxModelForm):
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=True,
        label="Manufacturer",
        selector=True,
        quick_add=True
    )

    volume_type = forms.ChoiceField(
        choices= VolumeTypeChoices,
        required=True,
        label="Volume Type"
    )
    volume_relation = forms.ChoiceField(
        choices=[('', '---------')] + list(VolumeRelationChoices),
        required=False,
        label="Volume Relation"
    )

    license_model = forms.ChoiceField(
        choices= LicenseModelChoices,
        required=True,
        label="License Model"
    )

    base_license = DynamicModelChoiceField(
        queryset=LicenseType.objects.filter(license_model="base"),
        required=False,
        label="Base License",
        help_text="Select a base license if this is an expansion pack.",
        selector=True,
        query_params={
            "license_model": "base",
            "manufacturer_id": "$manufacturer"
        }
    )

    purchase_model = forms.ChoiceField(
        choices=PurchaseModelChoices,
        required=True,
        label="Purchase Model"
    )

    slug = SlugField(
        required=True,
        label="Slug",
        help_text="URL-friendly identifier",
        slug_source="name",
    )

    comments = CommentField()

    class Meta:
        model = LicenseType
        fields = [
            "name", "slug", "manufacturer", "product_code", "ean_code",
            "volume_type", "volume_relation", "license_model", "base_license",
            "purchase_model", "description", "comments"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['base_license'].queryset = LicenseType.objects.filter(
            license_model=LicenseModelChoices.BASE
        )

        license_model_value = (
            self.data.get("license_model")
            or self.initial.get("license_model")
            or getattr(self.instance, "license_model", None)
        )

        if license_model_value == LicenseModelChoices.EXPANSION:
            self.fields["base_license"].required = True
        else:
            self.fields["base_license"].required = False


    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data:
            return cleaned_data

        license_model = cleaned_data.get("license_model")
        base_license = cleaned_data.get("base_license")

        if license_model == "expansion" and not base_license:
            self.add_error("base_license", "You must select a base license when the license model is set to 'Expansion Pack'.")
        elif license_model == "base" and base_license:
            self.add_error("base_license", "Base licenses cannot reference another base license.")

        return cleaned_data

# ---------- License ----------

class LicenseForm(NetBoxModelForm):

    license_type = DynamicModelChoiceField(
        queryset=LicenseType.objects.all(),
        required=True,
        label="License Type",
        help_text="Select the type of license.",
        selector=True,
        quick_add=True,
    )

    parent_license = DynamicModelChoiceField(
        queryset=License.objects.none(),
        required=False,
        label="Parent License",
        help_text="Select a parent license if applicable.",
        selector=True,
        query_params={'base_license_type_id': '$license_type'},
    )

    license_key = forms.CharField(required=True, label="License Key")

    volume_limit = forms.IntegerField(
        required=False,
        min_value=1,
        label="Volume Limit",
        help_text="Set to 1 for single, >1 for volume. Required for volume licenses."
    )

    purchase_date = forms.DateField(
        required=False,
        widget=DatePicker(attrs={'is_clearable': True}),
        label="Purchase Date"
    )

    expiry_date = forms.DateField(
        required=False,
        widget=DatePicker(attrs={'is_clearable': True}),
        label="Expiry Date"
    )

    comment = CommentField()

    class Meta:
        model = License
        fields = [
            "license_type", "license_key", "serial_number",
            "description", "volume_limit", "parent_license",
            "purchase_date", "expiry_date", "comment"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        license_type_id = (
            self.initial.get("license_type")
            or self.data.get("license_type")
            or getattr(self.instance, "license_type_id", None)
        )

        parent_license_id = (
            self.initial.get("parent_license")
            or self.data.get("parent_license")
            or getattr(self.instance, "parent_license_id", None)
        )

        license_type = None
        if license_type_id:
            try:
                license_type = LicenseType.objects.get(pk=license_type_id)
            except LicenseType.DoesNotExist:
                pass

        if license_type and license_type.license_model == LicenseModelChoices.EXPANSION:
            base_type = license_type.base_license
            if base_type:
                self.fields["parent_license"].queryset = License.objects.filter(
                    Q(license_type=base_type) | Q(pk=parent_license_id)
                ).distinct()
            else:
                self.fields["parent_license"].queryset = License.objects.filter(pk=parent_license_id)
            self.fields["parent_license"].required = True
        else:
            self.fields["parent_license"].queryset = (
                License.objects.filter(pk=parent_license_id)
                if parent_license_id else License.objects.none()
            )
            self.fields["parent_license"].required = False

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data:
            return cleaned_data

        license_type = cleaned_data.get("license_type")
        parent_license = cleaned_data.get("parent_license")
        volume_limit = cleaned_data.get("volume_limit")

        if license_type:
            if license_type.license_model == LicenseModelChoices.EXPANSION:
                if not parent_license:
                    self.add_error("parent_license", "An expansion license must be linked to a parent base license.")
                elif parent_license.license_type.license_model != LicenseModelChoices.BASE:
                    self.add_error("parent_license", "The selected parent license must be of a base license type.")
            elif license_type.license_model == LicenseModelChoices.BASE:
                if parent_license:
                    self.add_error("parent_license", "Base licenses cannot have a parent license.")

            if license_type.volume_type == "single" and not volume_limit:
                cleaned_data["volume_limit"] = 1 
            elif license_type.volume_type == "volume" and not volume_limit:
                self.add_error("volume_limit", "Volume limit is verplicht bij volume-licenties.")

        return cleaned_data

# ---------- Assignments ----------

class LicenseAssignmentForm(NetBoxModelForm):

    license = DynamicModelChoiceField(
        queryset=License.objects.all(),
        required=True,
        label="License",
        selector=True,
    )

    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label="Device",
        selector=True,
    )

    virtual_machine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label="Virtual Machine",
        selector=True,
    )

    comments = CommentField()

    fieldsets = (
        FieldSet("license", "volume", "description", name="General Information"),
        FieldSet(
            TabbedGroups(
                FieldSet("device", name="Device Assignment"),
                FieldSet("virtual_machine", name="Virtual Machine Assignment"),
            ),
            name="Assignment Target",
        ),
    )

    class Meta:
        model = LicenseAssignment
        fields = [
            "license",
            "device",   
            "virtual_machine",
            "volume",
            "description",
            "comments",
        ]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        instance = self.instance
        data = self.data or self.initial

        license_id = data.get("license") or getattr(instance, "license_id", None)
        device_id = data.get("device") or getattr(instance, "device_id", None)
        vm_id = data.get("virtual_machine") or getattr(instance, "virtual_machine_id", None)

        # self.fields["license"].label_from_instance = lambda obj: format_html(
        #     '{}<br><small class="text-muted">{}</small>',
        #     obj.license_key,
        #     obj.serial_number or "",
        # )

        if instance.pk:
            for field in ["license", "device", "virtual_machine"]:
                self.fields[field].disabled = True
        else:
            if license_id:
                self.fields["license"].initial = license_id
            if device_id:
                self.fields["device"].initial = device_id
            if vm_id:
                self.fields["virtual_machine"].initial = vm_id

        kind_value = (
            (data.get("device") and "device")
            or (data.get("virtual_machine") and "virtual_machine")
            or (instance.device_id and "device")
            or (instance.virtual_machine_id and "virtual_machine")
        )

        if kind_value == "device":
            self.fields["virtual_machine"].widget = forms.HiddenInput()
        elif kind_value == "virtual_machine":
            self.fields["device"].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data:
            return cleaned_data

        device = cleaned_data.get("device")
        virtual_machine = cleaned_data.get("virtual_machine")

        if not device and not virtual_machine:
            raise forms.ValidationError("You must assign the license to either a Device or a Virtual Machine.")
        if device and virtual_machine:
            raise forms.ValidationError("You can only assign a license to either a Device or a Virtual Machine, not both.")

        return cleaned_data

    def save(self, commit=True):
        assignment = super().save(commit=False)

        if assignment.device:
            assignment.virtual_machine = None
        elif assignment.virtual_machine:
            assignment.device = None

        if commit:
            assignment.save()

        return assignment