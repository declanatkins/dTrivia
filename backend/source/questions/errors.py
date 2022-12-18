from fastapi import HTTPException, status


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


class QuestionNotFound(HTTPException):
    def __init__(self, question_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with id {question_id} does not exist"
        )

class NoQuestionsFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No questions found"
        )