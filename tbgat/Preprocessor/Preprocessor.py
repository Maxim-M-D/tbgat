import re
import logging
import unicodedata

logger = logging.getLogger(__name__)


class PreProcessor:
    """Preprocesses tweets by normalizing, removing URLs, mentions, hashtags, emojis, and extra whitespace."""

    @staticmethod
    def clean_tweet(tweet: str) -> str:
        """Cleans a tweet by normalizing, removing URLs, mentions, hashtags, emojis, and extra whitespace.

        Args:
            tweet (str): The tweet to clean.

        Returns:
            str: The cleaned tweet.
        """
        logger.debug("Original tweet: %s", tweet)
        tweet = PreProcessor.normalize_tweet(tweet)
        tweet = PreProcessor.remove_urls(tweet)
        tweet = PreProcessor.remove_mentions_and_ats(tweet)
        tweet = PreProcessor.remove_hashtags(tweet)
        tweet = PreProcessor.remove_emojis(tweet)
        tweet = PreProcessor.remove_extra_whitespace(tweet)
        logger.debug("Cleaned tweet: %s", tweet)
        return tweet

    @staticmethod
    def normalize_tweet(tweet: str) -> str:
        """Normalizes a tweet. It removes accents and other diacritics. It uses the NFKD normalization form.

        Args:
            tweet (str): The tweet to normalize.

        Returns:
            str: The normalized tweet.
        """
        return unicodedata.normalize("NFKD", tweet)

    @staticmethod
    def remove_urls(tweet: str) -> str:
        """Removes URLs from a tweet.

        Args:
            tweet (str): The tweet to remove URLs from.

        Returns:
            str: The tweet without URLs.
        """
        return re.sub(r"http\S+|www\S+|https\S+", "", tweet, flags=re.MULTILINE)

    @staticmethod
    def remove_mentions_and_ats(tweet: str) -> str:
        """Removes mentions and @s from a tweet.

        Args:
            tweet (str): The tweet to remove mentions and @s from.

        Returns:
            str: The tweet without mentions and @s.
        """
        tweet = re.sub(r"@\w+", "", tweet, flags=re.MULTILINE)
        return tweet.replace("@", "")

    @staticmethod
    def remove_hashtags(tweet: str) -> str:
        """Removes hashtags from a tweet.

        Args:
            tweet (str): The tweet to remove hashtags from.

        Returns:
            str: The tweet without hashtags.
        """
        return tweet.replace("#", "")

    @staticmethod
    def remove_emojis(tweet: str) -> str:
        """Removes emojis from a tweet. It uses a regex pattern to remove emojis. These patterns are not exhaustive and may not remove all emojis.

        Args:
            tweet (str): The tweet to remove emojis from.

        Returns:
            str: The tweet without emojis.
        """
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "]+",
            flags=re.UNICODE,
        )
        return emoji_pattern.sub(r"", tweet)

    @staticmethod
    def remove_extra_whitespace(tweet: str) -> str:
        """Removes extra whitespace from a tweet.

        Args:
            tweet (str): The tweet to remove extra whitespace from.

        Returns:
            str: The tweet without extra whitespace.
        """
        return " ".join(tweet.split())
