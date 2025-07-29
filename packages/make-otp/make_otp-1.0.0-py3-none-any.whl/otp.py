import random
import string
def generate_otp(length=None,include_letters=True,include_digits=True):
    try:
        
        # Validate length
        if length is None or length <= 0:
            raise ValueError("specify a valid length for OTP")
        
        # Ensure at least one character set is enabled
        elif not include_letters and not include_digits:
            raise ValueError("Cannot generate OTP: At least one of 'include_letters' or 'include_digits' must be True/1.")
        
        # Validate input types
        valid_values = (True, False, 0, 1)
        if include_letters not in valid_values or include_digits not in valid_values:
            raise ValueError("'include_letters' and 'include_digits' must be boolean (True/False) or 0/1")
        
        # Select character pool 
        if include_letters and not include_digits:
            characters = string.ascii_letters

        elif include_digits and not include_letters:
            characters = string.digits

        elif include_letters and include_digits:
            half = length // 2
            extra = length % 2
            characters = random.choices(string.digits, k=half) + random.choices(string.ascii_letters, k=half + extra)
            random.shuffle(characters)
            return ''.join(characters)
        
        return ''.join(random.choices(characters, k=length))
        
    except ValueError as e:
        return f"Error: {e}"

