from analyzer.base import Analyzer
from typing import List, Dict, Any
import re

def find_warnings(tree) -> List[Dict[str, Any]]:
    """
    Находит потенциально опасные или неочевидные директивы.
    Возвращает список: [{type, directive, context, value}]
    """
    analyzer = Analyzer(tree)
    warnings = []
    for d, parent in analyzer.walk():
        if d.get('directive') == 'proxy_pass':
            val = d.get('args', '')
            if not re.match(r'^(http|https)://', val):
                warnings.append({'type': 'proxy_pass_no_scheme', 'directive': 'proxy_pass', 'context': parent, 'value': val})
        if d.get('directive') == 'autoindex' and d.get('args', '').strip() == 'on':
            warnings.append({'type': 'autoindex_on', 'directive': 'autoindex', 'context': parent, 'value': 'on'})
        if d.get('block') == 'if':
            warnings.append({'type': 'if_block', 'directive': 'if', 'context': parent, 'value': ''})
        if d.get('directive') == 'server_tokens' and d.get('args', '').strip() == 'on':
            warnings.append({'type': 'server_tokens_on', 'directive': 'server_tokens', 'context': parent, 'value': 'on'})
    return warnings 