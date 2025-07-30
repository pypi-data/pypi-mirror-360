import json

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def jqgrid_css():
    """
    Includes the required CSS files for jqGrid.
    """
    css = [
        # jQuery UI CSS
        '<link rel="stylesheet" href="/static/django_jqgrid/plugins/jquery-ui/jquery-ui.min.css">',

        # jqGrid core CSS
        '<link rel="stylesheet" href="/static/django_jqgrid/plugins/jqGrid/css/ui.jqgrid-bootstrap4.css">',

        # jqGrid addons CSS
        '<link rel="stylesheet" href="/static/django_jqgrid/plugins/jqGrid/css/addons/ui.multiselect.css">',

        # Custom jqGrid styles
        '<link rel="stylesheet" href="/static/django_jqgrid/css/jqgrid-bootstrap.css">'
    ]
    return mark_safe('\n'.join(css))


@register.simple_tag
def jqgrid_dependencies():
    """
    Includes the required dependency JavaScript files for jqGrid.
    Call this before jqgrid_js() if jQuery and jQuery UI are not already loaded.
    """
    js = [
        # jQuery Core
        '<script src="/static/django_jqgrid/plugins/jquery/jquery.min.js"></script>',

        # jQuery UI and dependencies
        '<script src="/static/django_jqgrid/plugins/jquery-ui/jquery-ui.min.js"></script>',

        # XLSX support for import/export
        '<script src="/static/django_jqgrid/plugins/xlsx/xlsx.full.min.js"></script>',
    ]
    return mark_safe('\n'.join(js))


@register.simple_tag
def jqgrid_js():
    """
    Includes the required JavaScript files for jqGrid.
    """
    js = [
        # jqGrid core files
        '<script src="/static/django_jqgrid/plugins/jqGrid/js/i18n/grid.locale-en.js"></script>',
        '<script src="/static/django_jqgrid/plugins/jqGrid/js/jquery.jqGrid.min.js"></script>',

        # Additional plugins
        '<script src="/static/django_jqgrid/plugins/jqGrid/plugins/jquery.contextmenu.js"></script>',
        '<script src="/static/django_jqgrid/plugins/jqGrid/plugins/grid.postext.js"></script>',
        '<script src="/static/django_jqgrid/plugins/jqGrid/plugins/jquery.tablednd.js"></script>',

        # Our custom jqGrid modules
        '<script src="/static/django_jqgrid/js/jqgrid-config.js"></script>',
        '<script src="/static/mainapp/js/multi-db-jqgrid.js"></script>',
        '<script src="/static/mainapp/js/multi-db-import-export.js"></script>',
        # '<script src="/static/django_jqgrid/js/jqgrid-integration.js"></script>'
    ]
    return mark_safe('\n'.join(js))


@register.inclusion_tag('django_jqgrid/grid_tag.html')
def jqgrid(grid_id, app_name, model_name, grid_title=None,
           custom_formatters=None, custom_buttons=None, custom_bulk_actions=None,
           on_grid_complete=None, on_select_row=None, on_select_all=None,
           on_init_complete=None, extra_options=None, include_import_export=True):
    """
    Renders a jqGrid with the specified options.
    
    Args:
        grid_id (str): ID for the grid element in HTML
        app_name (str): Django app name containing the model
        model_name (str): Django model name (lowercase)
        grid_title (str, optional): Title to display above the grid
        custom_formatters (dict, optional): Dictionary of custom formatter functions
        custom_buttons (dict, optional): Dictionary of custom button configurations
        custom_bulk_actions (dict, optional): Dictionary of custom bulk action configurations
        on_grid_complete (str, optional): JavaScript function to call when grid completes loading
        on_select_row (str, optional): JavaScript function to call when a row is selected
        on_select_all (str, optional): JavaScript function to call when all rows are selected
        on_init_complete (str, optional): JavaScript function to call when grid initialization completes
        extra_options (str, optional): Additional options to pass to initializeTableInstance
        include_import_export (bool, optional): Whether to include import/export buttons (default: True)
        
    Returns:
        dict: Context for the template rendering
        
    Examples:
        {% jqgrid "users_grid" "mainapp" "user" "Users" %}
        
        {% jqgrid "users_grid" "mainapp" "user" "Users" include_import_export=False %}
    """
    # Convert dictionary objects to JSON strings if provided
    if custom_formatters:
        if isinstance(custom_formatters, dict):
            custom_formatters = json.dumps(custom_formatters)

    if custom_buttons:
        if isinstance(custom_buttons, dict):
            custom_buttons = json.dumps(custom_buttons)

    if custom_bulk_actions:
        if isinstance(custom_bulk_actions, dict):
            custom_bulk_actions = json.dumps(custom_bulk_actions)

    return {
        'grid_id': grid_id,
        'app_name': app_name,
        'model_name': model_name,
        'grid_title': grid_title,
        'custom_formatters': custom_formatters,
        'custom_buttons': custom_buttons,
        'custom_bulk_actions': custom_bulk_actions,
        'on_grid_complete': on_grid_complete,
        'on_select_row': on_select_row,
        'on_select_all': on_select_all,
        'on_init_complete': on_init_complete,
        'extra_options': extra_options,
        'include_import_export': include_import_export
    }


@register.filter(is_safe=True)
def js_function(value):
    """
    Filter to safely render a JavaScript function string in a template.
    This helps avoid issues with escaping quotes and newlines.
    
    Usage:
        {{ my_js_function|js_function }}
    """
    if not value:
        return ''

    # Make sure the value is properly JSON serialized
    # but only if it's not already a string that looks like a function
    if not isinstance(value, str) or not value.strip().startswith('function'):
        value = json.dumps(value)

    return mark_safe(value)
