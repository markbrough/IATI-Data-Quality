
#  IATI Data Quality, tools for Data QA on IATI-formatted  publications
#  by Mark Brough, Martin Keegan, Ben Webb and Jennifer Smith
#
#  Copyright (C) 2014  Publish What You Fund
#
#  This programme is free software; you may redistribute and/or modify
#  it under the terms of the GNU Affero General Public License v3.0

which_packages = [
    ('dfid-ml', True),
    ('dfid-589', True),
    ('dfid-ph', True),
    ('worldbank-ao', True),
    ]

default_minimal_organisations = [
            {
            'organisation_name': 'World Bank',
            'organisation_code': '44002',
            'packagegroup_name': 'worldbank',
            'condition': None,
            'package_name': 'worldbank-ao',
             "organisation_total_spend": "11703.48",
             "organisation_total_spend_source": None,
             "organisation_currency": None,
             "organisation_currency_conversion": None,
             "organisation_currency_conversion_source": None,
             "organisation_largest_recipient": None,
             "organisation_largest_recipient_source": None
            },
            {
            'organisation_name': 'UK, DFID',
            'organisation_code': 'GB-GOV-1',
            'packagegroup_name': 'dfid',
            'condition': None,
            'package_name': 'dfid-ml',
             "organisation_total_spend": "3750.21",
             "organisation_total_spend_source": None,
             "organisation_currency": None,
             "organisation_currency_conversion": None,
             "organisation_currency_conversion_source": None,
             "organisation_largest_recipient": None,
             "organisation_largest_recipient_source": None
            },
            {
            'organisation_name': 'UK, DFID',
            'organisation_code': 'GB-GOV-1',
            'packagegroup_name': 'dfid',
            'condition': None,
            'package_name': 'dfid-589',
             "organisation_total_spend": "3750.21",
             "organisation_total_spend_source": None,
             "organisation_currency": None,
             "organisation_currency_conversion": None,
             "organisation_currency_conversion_source": None,
             "organisation_largest_recipient": None,
             "organisation_largest_recipient_source": None
            },
            {
            'organisation_name': 'UK, DFID',
            'organisation_code': 'GB-GOV-1',
            'packagegroup_name': 'dfid',
            'condition': None,
            'package_name': 'dfid-ph',
             "organisation_total_spend": "3750.21",
             "organisation_total_spend_source": None,
             "organisation_currency": None,
             "organisation_currency_conversion": None,
             "organisation_currency_conversion_source": None,
             "organisation_largest_recipient": None,
             "organisation_largest_recipient_source": None
            }
        ]
