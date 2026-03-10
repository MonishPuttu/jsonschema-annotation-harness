class ValidatorProtocol:
    """
    Interface for validator implementations used by the harness.
    """

    def validate(self, schema, instance):
        """
        Validate instance against schema.

        Returns
        -------
        (valid: bool, annotations: dict)
        """
        raise NotImplementedError