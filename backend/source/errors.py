from pydantic import BaseModel


class Error(BaseModel):
    detail: str


class UserAlreadyExists(Error):
    def __init__(self, username: str):
        super().__init__(detail=f"User with username {username} already exists")


class UserDoesNotExist(Error):
    def __init__(self, username: str):
        super().__init__(detail=f"User with username {username} does not exist")


class IncorrectPassword(Error):
    def __init__(self, username: str):
        super().__init__(detail=f"Incorrect password for user {username}")


class UserNotLoggedIn(Error):
    def __init__(self):
        super().__init__(detail="User is not logged in")