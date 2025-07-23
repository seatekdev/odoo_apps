import re
import logging
from odoo import models, api, fields, _
from odoo.osv import expression

_logger = logging.getLogger(__name__)

# Extend Base Model to apply multi-search globally
class BaseModel(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def _get_multi_search_pattern(self, value):
        """Check is multi-search pattern or not."""
        if not isinstance(value, str):
            return False, []

        # {record1 record2 ...}
        if value.startswith('{') and value.endswith('}'):
            content = value[1:-1].strip()
            if not content:
                return False, []

            search_terms = [term.strip() for term in content.split() if term.strip()]
            return bool(search_terms), search_terms

        # [record1, record2, ...]
        elif value.startswith('[') and value.endswith(']'):
            content = value[1:-1].strip()
            if not content:
                return False, []

            search_terms = [term.strip() for term in content.split(',') if term.strip()]
            return bool(search_terms), search_terms

        return False, []

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        """Override _search for all models"""
        try:
            new_domain = self._process_multi_search_args(domain)
            return super()._search(
                new_domain, offset=offset, limit=limit, order=order,
                access_rights_uid=access_rights_uid
            )
        except Exception as e:
            _logger.warning("Multi-search processing failed, falling back to normal search: %s", str(e))
            # Fallback to normal search if multi-search fails
            return super()._search(
                domain, offset=offset, limit=limit, order=order,
                access_rights_uid=access_rights_uid
            )

    @api.model
    def _process_multi_search_args(self, domain):
        if not domain:
            return domain

        new_args = []
        i = 0

        while i < len(domain):
            arg = domain[i]

            if arg in ('&', '|', '!'):
                new_args.append(arg)
                i += 1
                continue

            if isinstance(arg, (list, tuple)) and len(arg) == 3:
                field_name, operator, value = arg

                # Check multi-search
                is_multi_search, search_terms = self._get_multi_search_pattern(value)

                if is_multi_search and search_terms:
                    term_domains = []
                    for term in search_terms:
                        term_domains.append([(field_name, operator, term)])

                    if len(term_domains) == 1:
                        new_args.extend(term_domains[0])
                    else:
                        try:
                            or_domain = expression.OR(term_domains)
                            new_args.extend(or_domain)
                        except Exception as e:
                            _logger.warning("Failed to create OR domain for multi-search: %s", str(e))
                            # Fallback
                            new_args.append(arg)
                    i += 1
                    continue
            new_args.append(arg)
            i += 1
        return new_args

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """Override name_search for all models"""
        if name:
            is_multi_search, search_terms = self._get_multi_search_pattern(name)
            if is_multi_search and search_terms:
                # Create domain for multi-search
                name_domains = []
                for term in search_terms:
                    name_domains.append([(self._rec_name, operator, term)])

                if len(name_domains) == 1:
                    search_domain = name_domains[0]
                else:
                    try:
                        search_domain = expression.OR(name_domains)
                    except Exception as e:
                        _logger.warning("Failed to create OR domain for name_search: %s", str(e))
                        # Fallback to normal search
                        return super(BaseModel, self).name_search(
                            name=name, args=args, operator=operator, limit=limit
                        )

                if args:
                    search_domain = expression.AND([args, search_domain])

                # Find with domain
                records = self.search(search_domain, limit=limit)
                return records.name_get()

        # Fallback to normal name_search
        return super().name_search(
            name=name, args=args, operator=operator, limit=limit
        )
