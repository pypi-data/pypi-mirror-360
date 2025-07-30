# blackbox_logger/masking.py

SENSITIVE_FIELDS = {
    "password", "pass", "passwd", "secret", "token", "api_key", "authorization", "csrfmiddlewaretoken"
}

def mask_sensitive_data(data, custom_fields=None):
    sensitive_keys = SENSITIVE_FIELDS.union(set(custom_fields or []))

    if isinstance(data, dict):
        return {
            key: "***" if key.lower() in sensitive_keys else mask_sensitive_data(value, custom_fields)
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [mask_sensitive_data(item, custom_fields) for item in data]
    return data