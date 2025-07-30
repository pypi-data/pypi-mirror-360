from cgc.commands.cgc_models import CGCEntityList


class SSHKeyTypes(CGCEntityList):
    """List of supported SSH key types

    :param Enum: name of SSH key type
    :type Enum: str
    """

    RSA = "ssh-rsa"
    DSS = "ssh-dss"
    ECDSA_P256 = "ecdsa-sha2-nistp256"
    ECDSA_P384 = "ecdsa-sha2-nistp384"
    ECDSA_P521 = "ecdsa-sha2-nistp521"
    ED25519 = "ssh-ed25519"

    def load_data() -> list:
        """Return list of supported SSH key types

        :return: list of supported SSH key types
        :rtype: list
        """
        return [
            SSHKeyTypes.RSA,
            SSHKeyTypes.DSS,
            SSHKeyTypes.ECDSA_P256,
            SSHKeyTypes.ECDSA_P384,
            SSHKeyTypes.ECDSA_P521,
            SSHKeyTypes.ED25519,
        ]
