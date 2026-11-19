class CampaignValidationError(ValueError):
    pass


class CampaignNotFoundError(LookupError):
    pass


class OfferAlreadyExistsError(ValueError):
    pass


class OfferNotFoundError(LookupError):
    pass