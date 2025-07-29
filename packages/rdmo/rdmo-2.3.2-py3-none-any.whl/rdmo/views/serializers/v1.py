from django.template import Context, Template, TemplateSyntaxError

from rest_framework import exceptions, serializers

from rdmo.core.serializers import (
    ElementModelSerializerMixin,
    ElementWarningSerializerMixin,
    MarkdownSerializerMixin,
    ReadOnlyObjectPermissionSerializerMixin,
    TranslationSerializerMixin,
)

from ..models import View
from ..validators import ViewLockedValidator, ViewUniqueURIValidator


class ViewSerializer(TranslationSerializerMixin, ElementModelSerializerMixin,
                     ElementWarningSerializerMixin, ReadOnlyObjectPermissionSerializerMixin,
                     MarkdownSerializerMixin, serializers.ModelSerializer):

    markdown_fields = ('title', 'help')

    model = serializers.SerializerMethodField()

    warning = serializers.SerializerMethodField()
    read_only = serializers.SerializerMethodField()

    projects_count = serializers.IntegerField(read_only=True)

    def validate(self, data):
        # try to render the template to see that the syntax is ok
        try:
            Template(data['template']).render(Context({}))
        except (KeyError, IndexError):
            pass
        except (TemplateSyntaxError, TypeError) as e:
            raise exceptions.ValidationError({'template': '\n'.join(e.args)}) from e

        return super().validate(data)

    class Meta:
        model = View
        fields = (
            'id',
            'model',
            'uri',
            'uri_prefix',
            'uri_path',
            'comment',
            'locked',
            'order',
            'available',
            'catalogs',
            'sites',
            'editors',
            'groups',
            'template',
            'title',
            'help',
            'warning',
            'read_only',
            'projects_count'
        )
        trans_fields = (
            'title',
            'help'
        )
        extra_kwargs = {
            'uri_path': {'required': True}
        }
        validators = (
            ViewUniqueURIValidator(),
            ViewLockedValidator()
        )
        warning_fields = (
            'title',
        )


class ViewIndexSerializer(serializers.ModelSerializer):

    class Meta:
        model = View
        fields = (
            'id',
            'uri'
        )
