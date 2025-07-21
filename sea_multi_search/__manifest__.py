{
    'name': 'Sea Multi Search',
    'version': '12.0.1.0.0',
    'category': 'Tools',
    'summary': 'Multi Search Mixin for Odoo Models',
    'description': """
    This module provides a mixin that allows searching multiple records at once using special syntax:
    {term1 term2 term3}
    [term1, term2, term3]

    The mixin can be inherited by any model to enable multi-search functionality.
    """,
    'author': 'SeaTek',
    'license': 'LGPL-3',
    'website': 'https://seateklab.vn/',
    'depends': ['base','web'],
    'data': [],
    "images": ["static/description/banner.png"],
    'installable': True,
    'auto_install': False,
    'application': False,
}