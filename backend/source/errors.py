from fastapi import HTTPException, status

class UserAlreadyExists(HTTPException):
    def __init__(self, username: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with username {username} already exists"
        )


class UserDoesNotExist(HTTPException):
    def __init__(self, username: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username {username} does not exist"
        )


class IncorrectPassword(HTTPException):
    def __init__(self, username: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Incorrect password for user {username}"
        )


class UserNotLoggedIn(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not logged in"
        )


class CategoryAlreadyExists(HTTPException):
    def __init__(self, name: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category with name {name} already exists"
        )


class CategoryDoesNotExist(HTTPException):
    def __init__(self, name: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with name {name} does not exist"
        )