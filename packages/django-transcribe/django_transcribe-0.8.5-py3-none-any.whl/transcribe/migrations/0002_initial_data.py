# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

INITIAL_TAG_DATA = [
    {
        'id': 1,
        'name': 'Heading',
        'description': 'a heading or chapter title',
        'open_tag': '<head>',
        'close_tag': '</head>',
    },  # noqa
    {
        'id': 2,
        'name': 'Quote',
        'description': 'quoted text',
        'open_tag': '<q>',
        'close_tag': '</q>',
    },  # noqa
    {
        'id': 3,
        'name': 'Person',
        'description': 'the name of a person (e.g. John Doe)',
        'open_tag': '<name type="person">',
        'close_tag': '</name>',
    },  # noqa
    {
        'id': 4,
        'name': 'Place',
        'description': 'the name of a place (e.g. New York City)',
        'open_tag': '<name type="place">',
        'close_tag': '</name>',
    },  # noqa
    {
        'id': 5,
        'name': 'Date',
        'description': 'Mark a text string as a date. (Include a normalize...',
        'open_tag': '<date when="YYYY-MM-DD">',
        'close_tag': '</date>',
    },  # noqa
    {
        'id': 6,
        'name': 'Add',
        'description': 'an addition or insertion',
        'open_tag': '<add>',
        'close_tag': '</add>',
    },  # noqa
    {
        'id': 7,
        'name': 'Del',
        'description': 'as strikeout or deletion',
        'open_tag': '<del rend="overstrike">',
        'close_tag': '</del>',
    },  # noqa
    {
        'id': 8,
        'name': 'Note',
        'description': 'a note in the margin, or elsewhere',
        'open_tag': '<note place="margin">',
        'close_tag': '</note>',
    },  # noqa
    {
        'id': 9,
        'name': 'Unclear',
        'description': 'mark something as unclear/illegible',
        'open_tag': '<unclear reason="illegible">',
        'close_tag': '</unclear>',
    },  # noqa
    {
        'id': 10,
        'name': 'Page #',
        'description': 'mark a new page break along with the printed page ...',
        'open_tag': '<pb n="',
        'close_tag': '"/>',
    },  # noqa
    {
        'id': 11,
        'name': 'Underline',
        'description': 'underlined text',
        'open_tag': '<hi rend="underline">',
        'close_tag': '</hi>',
    },  # noqa
    {
        'id': 12,
        'name': 'Bold',
        'description': 'bold text',
        'open_tag': '<hi rend="bold">',
        'close_tag': '</hi>',
    },  # noqa
    {
        'id': 13,
        'name': 'Italic',
        'description': 'italicized text',
        'open_tag': '<hi rend="italic">',
        'close_tag': '</hi>',
    },  # noqa
    {
        'id': 14,
        'name': 'Superscript',
        'description': 'superscript text',
        'open_tag': '<hi rend="sup">',
        'close_tag': '</hi>',
    },  # noqa
    {
        'id': 15,
        'name': 'Subscript',
        'description': 'subscript text',
        'open_tag': '<hi rend="sub">',
        'close_tag': '</hi>',
    },  # noqa
]


def initial_tag_data(apps, schema_editor):
    Tag = apps.get_model('transcribe', 'Tag')
    Tag.objects.all().delete()
    for data in INITIAL_TAG_DATA:
        Tag.objects.create(**data)


class Migration(migrations.Migration):

    dependencies = [('transcribe', '0001_initial')]

    operations = [
        migrations.RunPython(
            initial_tag_data, reverse_code=migrations.RunPython.noop
        ),
    ]
