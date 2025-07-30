def get_clean_validation_messages(validation_error):
    """
    Extract and format clean validation error messages.

    Args:
        validation_error (ValidationError): The Marshmallow ValidationError instance.

    Returns:
        str: A formatted string with all validation error messages.
    """

    def format_errors(errors, parent_key=""):
        messages = []
        for key, value in errors.items():
            full_key = f"{parent_key}.{key}" if parent_key else key
            if isinstance(value, dict):
                # Recursively format nested errors
                messages.extend(format_errors(value, full_key))
            else:
                # Append error messages
                messages.append(f"{full_key}: {', '.join(value)}")
        return messages

    return "\n".join(format_errors(validation_error.messages))
