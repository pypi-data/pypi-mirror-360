def check_error(error, expected_message, expected_errors=1):
    validation_errors = error.value.errors()
    assert len(validation_errors) == expected_errors
    assert validation_errors[0]['msg'].startswith(expected_message)
