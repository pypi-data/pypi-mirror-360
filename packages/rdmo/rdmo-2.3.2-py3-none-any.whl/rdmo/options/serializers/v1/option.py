from rest_framework import serializers

from rdmo.core.serializers import (
    ElementModelSerializerMixin,
    ElementWarningSerializerMixin,
    MarkdownSerializerMixin,
    ReadOnlyObjectPermissionSerializerMixin,
    ThroughModelSerializerMixin,
    TranslationSerializerMixin,
)

from ...models import Option, OptionSet
from ...validators import OptionLockedValidator, OptionUniqueURIValidator


class OptionSerializer(ThroughModelSerializerMixin, TranslationSerializerMixin,
                       ElementModelSerializerMixin, ElementWarningSerializerMixin,
                       ReadOnlyObjectPermissionSerializerMixin, MarkdownSerializerMixin,
                       serializers.ModelSerializer):

    markdown_fields = ('text', 'help')

    model = serializers.SerializerMethodField()

    optionsets = serializers.PrimaryKeyRelatedField(queryset=OptionSet.objects.all(), required=False, many=True)
    conditions = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    warning = serializers.SerializerMethodField()
    read_only = serializers.SerializerMethodField()

    values_count = serializers.IntegerField(read_only=True)
    projects_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Option
        fields = (
            'id',
            'model',
            'uri',
            'uri_prefix',
            'uri_path',
            'comment',
            'locked',
            'text',
            'help',
            'default_text',
            'view_text',
            'label',
            'additional_input',
            'optionsets',
            'conditions',
            'values_count',
            'projects_count',
            'editors',
            'warning',
            'read_only',
        )
        trans_fields = (
            'text',
            'help',
            'default_text',
            'view_text'
        )
        parent_fields = (
            ('optionsets', 'optionset', 'option', 'optionset_options'),
        )
        extra_kwargs = {
            'uri_path': {'required': True}
        }
        validators = (
            OptionUniqueURIValidator(),
            OptionLockedValidator()
        )
        warning_fields = (
            'text',
        )


class OptionIndexSerializer(serializers.ModelSerializer):

    class Meta:
        model = Option
        fields = (
            'id',
            'uri'
        )
