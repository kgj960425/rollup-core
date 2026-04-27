"""커스텀 예외."""


class RollupException(Exception):
    """모든 Rollup 예외의 베이스."""

    code: str = "UNKNOWN"
    status: int = 400


class InvalidActionError(RollupException):
    code = "INVALID_ACTION"
    status = 400


class NotYourTurnError(RollupException):
    code = "NOT_YOUR_TURN"
    status = 403


class NotRoomMemberError(RollupException):
    code = "NOT_ROOM_MEMBER"
    status = 403


class GameNotFoundError(RollupException):
    code = "GAME_NOT_FOUND"
    status = 404


class GameAlreadyStartedError(RollupException):
    code = "GAME_ALREADY_STARTED"
    status = 409


class UnknownGameTypeError(RollupException):
    code = "UNKNOWN_GAME_TYPE"
    status = 400
