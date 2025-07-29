from my_aws_helpers.logging import select_powertools_logger


logger = select_powertools_logger("aws-helpers-s3")


class Auth:

    @staticmethod
    def get_bearer_from_lambda_event(event: dict) -> str:
        try:
            bearer_token = event["headers"]["Authorization"]
            return str(bearer_token).split("Bearer")[-1]
        except Exception as e:
            logger.exception(f"Failed to get bearer from lambda event due to {e}")
        return None
