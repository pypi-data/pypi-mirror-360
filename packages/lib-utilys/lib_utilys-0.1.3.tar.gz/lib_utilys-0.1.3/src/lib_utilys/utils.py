
def clean_special_characters(string):
        """Replaces special characters in a string with a hyphen."""
        special_chars = ["/", "\\", ":", "*", "?", "\"", "<", ">", "|"]
        for char in special_chars:
            string = string.replace(char, "-")
        return string