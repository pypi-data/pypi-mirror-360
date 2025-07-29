from typing import Optional, Union

from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from rdmo.conditions.models import Condition
from rdmo.core.serializers import ElementModelSerializerMixin, MarkdownSerializerMixin
from rdmo.core.utils import markdown2html
from rdmo.domain.models import Attribute
from rdmo.options.models import Option, OptionSet
from rdmo.questions.models import Page, Question, QuestionSet


class AttributeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attribute
        fields = (
            'id',
            'uri'
        )


class OptionSerializer(MarkdownSerializerMixin, serializers.ModelSerializer):

    markdown_fields = ('text', 'help')

    class Meta:
        model = Option
        fields = (
            'id',
            'text',
            'help',
            'text_and_help',
            'additional_input',
            'default_text'
        )


class OptionSetSerializer(ElementModelSerializerMixin, serializers.ModelSerializer):

    model = serializers.SerializerMethodField()
    options = OptionSerializer(source='elements', many=True)

    class Meta:
        model = OptionSet
        fields = (
            'id',
            'uri',
            'model',
            'options',
            'has_provider',
            'has_search',
            'has_refresh',
            'has_conditions'
        )


class ConditionSerializer(serializers.ModelSerializer):

    class Meta:
        ref_name = 'ProjectConditionSerializer'

        model = Condition
        fields = (
            'id',
            'uri',
            'source',
            'relation',
            'target_text',
            'target_option'
        )


class QuestionSerializer(ElementModelSerializerMixin, MarkdownSerializerMixin, serializers.ModelSerializer):

    markdown_fields = ('help', 'text')

    model = serializers.SerializerMethodField()
    conditions = ConditionSerializer(default=None, many=True)
    optionsets = serializers.SerializerMethodField()

    verbose_name = serializers.SerializerMethodField()

    attribute_uri = serializers.CharField(source='attribute.uri', read_only=True)

    class Meta:
        model = Question
        fields = (
            'id',
            'uri',
            'model',
            'help',
            'text',
            'default_text',
            'default_option',
            'default_external_id',
            'verbose_name',
            'widget_type',
            'value_type',
            'unit',
            'width',
            'minimum',
            'maximum',
            'step',
            'attribute',
            'attribute_uri',
            'conditions',
            'optionsets',
            'is_collection',
            'is_optional',
            'has_conditions'
        )

    def get_optionsets(self, obj) -> dict:
        ordered_optionsets = sorted(obj.optionsets.all(), key=lambda optionset: optionset.order)
        return OptionSetSerializer(ordered_optionsets, many=True).data

    def get_verbose_name(self, obj) -> str:
        return obj.verbose_name or _('entry')


class QuestionSetSerializer(ElementModelSerializerMixin, MarkdownSerializerMixin, serializers.ModelSerializer):

    markdown_fields = ('title', 'help')

    model = serializers.SerializerMethodField()
    conditions = ConditionSerializer(default=None, many=True)
    elements = serializers.SerializerMethodField()
    verbose_name = serializers.SerializerMethodField()

    attribute_uri = serializers.CharField(source='attribute.uri', read_only=True)

    class Meta:
        model = QuestionSet
        fields = (
            'id',
            'uri',
            'model',
            'title',
            'help',
            'verbose_name',
            'attribute',
            'attribute_uri',
            'is_collection',
            'conditions',
            'elements',
            'has_conditions'
        )

    def get_elements(self, obj) -> list[dict]:
        for element in obj.elements:
            if isinstance(element, QuestionSet):
                yield QuestionSetSerializer(element, context=self.context).data
            else:
                yield QuestionSerializer(element, context=self.context).data

    def get_verbose_name(self, obj) -> str:
        return obj.verbose_name or _('block')


class PageSerializer(ElementModelSerializerMixin, MarkdownSerializerMixin, serializers.ModelSerializer):

    markdown_fields = ('title', 'help')

    model = serializers.SerializerMethodField()
    conditions = ConditionSerializer(default=None, many=True)
    elements = serializers.SerializerMethodField()
    section = serializers.SerializerMethodField()
    prev_page = serializers.SerializerMethodField()
    next_page = serializers.SerializerMethodField()
    verbose_name = serializers.SerializerMethodField()

    attribute_uri = serializers.CharField(source='attribute.uri', read_only=True)

    class Meta:
        ref_name = 'ProjectPageSerializer'

        model = Page
        fields = (
            'id',
            'uri',
            'model',
            'title',
            'help',
            'verbose_name',
            'attribute',
            'attribute_uri',
            'is_collection',
            'conditions',
            'elements',
            'section',
            'prev_page',
            'next_page',
            'has_conditions'
        )

    def get_elements(self, obj) -> list[dict]:
        for element in obj.elements:
            if isinstance(element, QuestionSet):
                yield QuestionSetSerializer(element, context=self.context).data
            else:
                yield QuestionSerializer(element, context=self.context).data

    def get_section(self, obj) -> dict[str, Union[int, str, None]]:
        section = self.context['catalog'].get_section_for_page(obj)
        return {
           'id': section.id,
           'title': markdown2html(section.title),
           'first': section.elements[0].id if section.elements else None
        } if section else {}

    def get_prev_page(self, obj) -> Optional[int]:
        page = self.context['catalog'].get_prev_page(obj)
        return page.id if page else None

    def get_next_page(self, obj) -> Optional[int]:
        page = self.context['catalog'].get_next_page(obj)
        return page.id if page else None

    def get_verbose_name(self, obj) -> str:
        return obj.verbose_name or _('set')
