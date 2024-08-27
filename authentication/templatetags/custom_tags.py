from django import template

register = template.Library()


@register.filter
def set_attrs(field, args):
    """
    args should be a string in the format: "class:class-name,placeholder:placeholder-text"
    """
    attrs = {}
    for arg in args.split(","):
        key, value = arg.split(":")
        attrs[key] = value

    return field.as_widget(attrs=attrs)
