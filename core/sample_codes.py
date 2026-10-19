"""Pre-curated Python snippets exhibiting common real-world bugs for instant testing."""

SAMPLE_SNIPPETS = {
    "Classic Math & Collection Bugs": {
        "description": "Division by zero on empty collections and incorrect negative number handling.",
        "code": '''def divide_numbers(a, b):
    # Bug 1: No ZeroDivision check
    return a / b


def calculate_average(numbers):
    # Bug 2: ZeroDivisionError if numbers is empty
    total = sum(numbers)
    return total / len(numbers)


def find_largest(numbers):
    # Bug 3: Fails for all-negative lists (e.g. [-5, -20, -10] returns 0 instead of -5)
    # Bug 4: Unhandled empty list returns 0
    largest = 0
    for number in numbers:
        if number > largest:
            largest = number
    return largest
''',
    },
    "Shopping Cart & Discounts (Mutable Default & Float)": {
        "description": "Dangerous mutable default argument and percentage logic bug.",
        "code": '''def apply_discount(price, discount_percent):
    # Bug: treating integer percentage e.g. 20 as 20x price reduction instead of 20%
    return price - (price * discount_percent)


def add_item_to_cart(item, price, cart=[]):
    # Bug: Mutable default argument persists between function invocations
    cart.append({"item": item, "price": price})
    return cart


def calculate_subtotal(cart):
    # Bug: KeyError if dictionary lacks "price" key or unexpected type
    return sum(item["price"] for item in cart)
''',
    },
    "Binary Search (Off-by-One & Infinite Loop)": {
        "description": "Boundary condition bug and integer overflow / infinite loop hazard.",
        "code": '''def binary_search(arr, target):
    # Bug: off-by-one right bound and integer midpoint issue
    left = 0
    right = len(arr)  # Should be len(arr) - 1

    while left < right:  # Should be left <= right
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid  # Should be mid + 1, causes infinite loop
        else:
            right = mid - 1

    return -1
''',
    },
    "User Authentication & State": {
        "description": "Case-sensitivity oversight and missing None checks.",
        "code": '''def validate_credentials(users_db, username, password):
    # Bug: crashes with AttributeError if username is None
    # Bug: case-sensitive username lookup fails normalized queries
    if username.strip() in users_db:
        stored_hash = users_db[username.strip()]
        return stored_hash == password
    return False


def get_user_role(users_meta, user_id):
    # Bug: KeyError when user_id is not present
    return users_meta[user_id]["role"]
''',
    },
}
