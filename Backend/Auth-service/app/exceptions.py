from fastapi import HTTPException


class EmailAlreadyExistsException(HTTPException):
    def __init__(self, email: str):
        super().__init__(409, f"Email déjà utilisé : {email}")


class InvalidCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(
            401,
            "Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )


class AccountDisabledException(HTTPException):
    def __init__(self):
        super().__init__(403, "Compte désactivé")


class InvalidTokenException(HTTPException):
    def __init__(self):
        super().__init__(
            401,
            "Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )


class UserNotFoundException(HTTPException):
    def __init__(self, user_id: int):
        super().__init__(404, f"Utilisateur {user_id} introuvable")