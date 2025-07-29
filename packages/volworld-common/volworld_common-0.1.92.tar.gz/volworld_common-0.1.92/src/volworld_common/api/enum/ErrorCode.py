from enum import IntEnum
from volworld_common.api.enum.common_error_code import CommonErrorCode


class ErrorCode(IntEnum):
    NoError = CommonErrorCode.NoError.value

    NoNeedToUpdate = 311

    Unauthorized = 40
    Forbidden = 403
    TargetObjectNotFound = 404

    NotEnoughResource = 512

    RequestTooManyImages = 603

    CanNotUndo = 701

    # ====== 1000 auth ======
    UserNameExisting = 1001
    WrongUserNameFormat = 1002
    TooShortPassword = 1003
    NotLogin = 1004
    WrongPassword = 1011
    CanNotUpdateSystemUsers = 1021
    NoPermission = 1022
    NotTestUser = 1023
    NotRootUser = 1024

    # ===== 1101-1399 Adventurer Common =====
    # ===== 1401-1599 Designer Common =====
    NotDesignAuthor = 1403
    # ===== 1601-1799 Learner Common =====

    # ====== 4000 (extend HTML 4xx) ======
    VersionMismatch = 4010
    EventMismatch = 4011

    # ====== 4100 user ======
    UserNotFound = 4100
    UserIdExisting = 4101

    # ====== 4200 SA ======
    SaNotFound = 4200

    # ====== 4500 Puzzle ======
    PuzzleNotFound = 4500
    PuzzleChallengeNotFound = 4501
    PuzzleChallengeAlreadyFinished = 4502
    PuzzleDesignNotFound = 4503
    PuzzleContextNotFound = 4530
    PuzzleIsPublished = 4580
    PuzzleIsArchived = 4581
    PuzzleIsNotPublished = 4582

    # ====== 4600 Site ======
    SiteNotFound = 4600
    SiteChallengeNotFound = 4601
    SiteChallengeAlreadyConquered = 4602
    NotInSiteChallenge = 4603
    AlreadyInSiteChallenge = 4605
    SiteContextNotFound = 4630
    SiteIsPublished = 4680
    SiteIsArchived = 4681
    SiteIsNotPublished = 4682

    # ====== 4700 Lane ======
    LaneNotFound = 4700
    LaneChallengeNotFound = 4701
    LaneChallengeAlreadyConquered = 4702
    NotInLaneChallenge = 4703
    AlreadyInLaneChallenge = 4705
    LaneContextNotFound = 4730
    ChallengeLaneNotFound = 4760
    LaneIsPublished = 4780
    LaneIsArchived = 4781
    LaneIsNotPublished = 4782

    # ====== 5000 Server Error ======
