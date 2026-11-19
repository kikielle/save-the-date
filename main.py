"""Save The Date - a landing page for smashed dates with a flavor quiz.

Visitors can browse flavors, take a mini personality quiz to find out
which date flavor they are, add dates to a cart, and check out.

Advanced techniques used (not covered in class):
  * f-strings with format specs, e.g. f"${amount:.2f}" -- the ":.2f" part
    means "show this number with exactly 2 digits after the decimal point".
  * max(dictionary, key=dictionary.get) -- max() normally compares the dict's
    keys; key=dictionary.get tells it to compare the VALUES instead, so it
    returns the key with the largest value. Ties return the first key found.
  * dataclasses.field(default_factory=...) -- gives each State its own fresh
    list/dict instead of one shared list.
"""
from dataclasses import dataclass, field

from drafter import *

@dataclass
class Flavor:
    """Everything about the flavor"""
    name: str
    price: float
    tagline: str
    personality: str


@dataclass
class CartItem:
    """What's in the cart"""
    flavor: str
    quantity: int
    price: float


CATALOG = [
    Flavor("Salted PB Chocolate", 8.0, "Pure, gooey, classic.",
           "You're dependable and warm. People come to you for comfort, "
           "and you never need to try too hard to be loved."),
    Flavor("Dark Chocolate Cashew", 9.0, "Simple perfection.",
           "You have impeccable taste in fashion and "
           "never leave the house without your signature scent."),
    Flavor("Chocolate Covered Strawberry", 10.0, "Dessert, but make it a snack.",
           "You're a romantic at heart with a talent for "
           "planning the perfect party."),
    Flavor("Toasted Coconut", 9.0, "Elevated Almond Joy.",
           "You're the definition of summertime and "
           "the one with the best stories at the party."),
    Flavor("Dubai Chocolate", 12.0, "Pistachio cream paired with crispy kataifi.",
           "You're the spontaneous one. You say yes to the road trip "
           "and stay up to date on trends."),
]

# Each question: (question text, {answer text: flavor it votes for})
QUIZ = [
    ("It's Saturday morning. What's your vibe?", {
        "Slow coffee and a good book": "Dark Chocolate Cashew",
        "Candles, blankets, and baking": "Salted PB Chocolate",
        "Brunch somewhere fancy": "Chocolate Covered Strawberry",
        "Spontaneous road trip": "Dubai Chocolate",
        "Whatever my friends are doing": "Toasted Coconut",
    }),
    ("Pick a movie night snack:", {
        "Plain popcorn": "Dark Chocolate Cashew",
        "Warm cookies": "Salted PB Chocolate",
        "Dark chocolate anything": "Chocolate Covered Strawberry",
        "Kettle corn": "Toasted Coconut",
        "Spicy chips": "Dubai Chocolate",
    }),
    ("Your friends would describe you as:", {
        "Reliable": "Salted PB Chocolate",
        "Nurturing": "Chocolate Covered Strawberry",
        "Sophisticated": "Dark Chocolate Cashew",
        "Hilarious": "Toasted Coconut",
        "Adventurous": "Dubai Chocolate",
    }),
    ("Pick a season:", {
        "Spring": "Salted PB Chocolate",
        "Autumn": "Dark Chocolate Cashew",
        "Winter": "Chocolate Covered Strawberry",
        "Whichever my birthday is in": "Dubai Chocolate",
        "Summer": "Toasted Coconut",
    }),
]

SHIPPING_OPTIONS = {
    "Standard (5-7 days) - $4.99": 4.99,
    "Express (2 days) - $12.99": 12.99,
    "Local pickup in Newark, DE - Free": 0.0,
}

QUANTITY_OPTIONS = ["1", "2", "3", "4", "5", "6"]


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------


@dataclass
class State:
    """Everything the website remembers between pages"""
    customer_name: str = ""
    cart: list[CartItem] = field(default_factory=list)
    quiz_scores: dict[str, int] = field(default_factory=dict)
    quiz_step: int = 0
    result_flavor: str = ""
    gift_note: str = ""
    order_total: float = 0.0


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def format_money(amount: float) -> str:
    """Turn a number like 8 into a price string like $8.00"""
    return f"${amount:.2f}"


def find_flavor(flavor_name: str) -> Flavor:
    """Look up a Flavor in the catalog by name (falls back to the first)."""
    for flavor in CATALOG:
        if flavor.name == flavor_name:
            return flavor
    return CATALOG[0]


def item_subtotal(item: CartItem) -> float:
    """Return price * quantity for a single cart item"""
    return item.price * item.quantity


def cart_subtotal(items: list[CartItem]) -> float:
    """Add up the subtotals of every item in the cart"""
    total = 0.0
    for item in items:
        total += item_subtotal(item)
    return total


def date_count(items: list[CartItem]) -> int:
    """Count how many dates are in the cart in total"""
    count = 0
    for item in items:
        count += item.quantity
    return count


def add_to_cart_items(items: list[CartItem], flavor_name: str,
                      quantity: int) -> None:
    """Add dates to the cart list , merging with an existing entry if found"""
    for item in items:
        if item.flavor == flavor_name:
            item.quantity += quantity
            return
    items.append(CartItem(flavor_name, quantity,
                          find_flavor(flavor_name).price))


def remove_from_cart_items(items: list[CartItem], flavor_name: str) -> None:
    """Remove every entry for the given flavor from the cart list"""
    for item in list(items):  # copy so we can safely remove while looping
        if item.flavor == flavor_name:
            items.remove(item)


def cart_flavor_names(items: list[CartItem]) -> list[str]:
    """Return the flavor name of each item in the cart"""
    names = []
    for item in items:
        names.append(item.flavor)
    return names


def new_quiz_scores() -> dict[str, int]:
    """Create a score table with every flavor starting at zero"""
    scores = {}
    for flavor in CATALOG:
        scores[flavor.name] = 0
    return scores


def pick_winner(scores: dict[str, int]) -> str:
    """Return the flavor with the highest score (first one wins ties)"""
    return max(scores, key=scores.get)


def shipping_cost(choice: str) -> float:
    """Look up the cost of a shipping option (0 if unknown)"""
    return SHIPPING_OPTIONS.get(choice, 0.0)


def validate_checkout(name: str, email: str) -> str:
    """Return an error message, or an empty string if the info is fine"""
    if name.strip() == "":
        return "Please tell us your name so we can label your package."
    if "@" not in email or "." not in email:
        return "That email doesn't look right. Please double-check it."
    return ""


# ---------------------------------------------------------------------------
# Shared page pieces
# ---------------------------------------------------------------------------


def nav_bar(state: State) -> list:
    """Build the navigation links shown at the top of every page"""
    cart_label = f"Cart ({date_count(state.cart)})"
    return [
        Link("Home", index), " | ",
        Link("Shop", shop), " | ",
        Link("Find Your Dream Date", quiz_start), " | ",
        Link(cart_label, cart),
        HorizontalRule(),
    ]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@route
def index(state: State) -> Page:
    """Landing page: pitch the product and invite people to the quiz."""
    teaser = []
    for flavor in CATALOG:
        teaser.append(f"{flavor.name} - {flavor.tagline}")
    greeting = "Welcome back" if state.customer_name else "Welcome"
    if state.customer_name:
        greeting += f", {state.customer_name}"
    content = nav_bar(state) + [
        Header("Save The Date", 1),
        Header("Dates, smashed. Snacktime, upgraded.", 3),
        f"{greeting}! We hand-smash premium Medjool dates and "
        "garnish with your selection of delectable toppings! "
        "No added sugar. No nonsense.",
        LineBreak(),
        LineBreak(),
        Image("save the date homepage pic.jpg", width=400),   # photo
        LineBreak(),
        Header("Our flavors", 3),
        BulletedList(teaser),
        LineBreak(),
        Button("Shop now", shop),
        " ",
        Button("Date time: Take the quiz", quiz_start),
    ]
    if state.result_flavor:
        content.append(LineBreak())
        content.append(f"Your date: {state.result_flavor}")
    return Page(state, content)


@route
def shop(state: State) -> Page:
    """Shop page: list every flavor and let the customer add dates."""
    product_lines = []
    for flavor in CATALOG:
        product_lines.append(
            f"{flavor.name} ({format_money(flavor.price)}) - "
            f"{flavor.tagline}")
    names = [flavor.name for flavor in CATALOG]
    default_flavor = state.result_flavor if state.result_flavor else names[0]
    return Page(state, nav_bar(state) + [
        Header("Shop", 1),
        BulletedList(product_lines),
        LineBreak(),
        "Flavor: ",
        SelectBox("flavor", names, default_flavor),
        LineBreak(),
        "Quantity: ",
        SelectBox("quantity", QUANTITY_OPTIONS, "1"),
        LineBreak(),
        Button("Add to cart", add_to_cart),
    ])


@route
def add_to_cart(state: State, flavor: str, quantity: str) -> Page:
    """Add the chosen flavor and quantity to the cart, then show the cart."""
    add_to_cart_items(state.cart, flavor, int(quantity))
    return cart(state)


@route
def cart(state: State) -> Page:
    """Cart page: show items, the subtotal, and remove/checkout buttons."""
    if len(state.cart) == 0:
        return Page(state, nav_bar(state) + [
            Header("Your cart", 1),
            "Your cart is empty. Those dates won't smash themselves!",
            LineBreak(),
            Button("Go shopping", shop),
        ])
    lines = []
    for item in state.cart:
        lines.append(f"{item.quantity} x {item.flavor} @ "
                     f"{format_money(item.price)} = "
                     f"{format_money(item_subtotal(item))}")
    names = cart_flavor_names(state.cart)
    return Page(state, nav_bar(state) + [
        Header("Your cart", 1),
        BulletedList(lines),
        f"Subtotal: {format_money(cart_subtotal(state.cart))}",
        LineBreak(),
        LineBreak(),
        "Remove a flavor: ",
        SelectBox("flavor_to_remove", names, names[0]),
        " ",
        Button("Remove", remove_item),
        LineBreak(),
        LineBreak(),
        Button("Keep shopping", shop),
        " ",
        Button("Check out", checkout),
    ])


@route
def remove_item(state: State, flavor_to_remove: str) -> Page:
    """Remove a flavor from the cart and show the updated cart."""
    remove_from_cart_items(state.cart, flavor_to_remove)
    return cart(state)


def build_checkout_page(state: State, error: str) -> Page:
    """Build the checkout form, optionally showing an error message."""
    content = nav_bar(state) + [Header("Checkout", 1)]
    if error != "":
        content.append(f"⚠️ {error}")
        content.append(LineBreak())
    content += [
        f"Subtotal: {format_money(cart_subtotal(state.cart))}",
        LineBreak(),
        "Your name: ",
        TextBox("name", state.customer_name),
        LineBreak(),
        "Email: ",
        TextBox("email", ""),
        LineBreak(),
        "Shipping: ",
        SelectBox("shipping", list(SHIPPING_OPTIONS.keys()),
                  list(SHIPPING_OPTIONS.keys())[0]),
        LineBreak(),
        CheckBox("is_gift", False),
        " This is a gift",
        LineBreak(),
        "Gift note (only used if gift is checked):",
        LineBreak(),
        TextArea("gift_note", state.gift_note),
        LineBreak(),
        Button("Place order", place_order),
        " ",
        Button("Back to cart", cart),
    ]
    return Page(state, content)


@route
def checkout(state: State) -> Page:
    """Checkout page: only available when the cart has something in it."""
    if len(state.cart) == 0:
        return cart(state)
    return build_checkout_page(state, "")


@route
def place_order(state: State, name: str, email: str, shipping: str,
                is_gift: bool, gift_note: str) -> Page:
    """Validate the form, save the order total, and clear the cart."""
    state.customer_name = name.strip()
    state.gift_note = gift_note if is_gift else ""
    error = validate_checkout(name, email)
    if error != "":
        return build_checkout_page(state, error)
    state.order_total = (cart_subtotal(state.cart)
                         + shipping_cost(shipping))
    state.cart = []
    return confirmation(state)


@route
def confirmation(state: State) -> Page:
    """Thank-you page showing the final total."""
    content = nav_bar(state) + [
        Header("Order placed! 🎉", 1),
        f"Thanks, {state.customer_name}! Your total was "
        f"{format_money(state.order_total)}.",
        LineBreak(),
        "We're smashing your dates right now.",
    ]
    if state.gift_note != "":
        content.append(LineBreak())
        content.append(f"Your gift note: \"{state.gift_note}\"")
    content += [LineBreak(), LineBreak(), Button("Back home", index)]
    return Page(state, content)


@route
def quiz_start(state: State) -> Page:
    """Reset the quiz and show the intro screen."""
    state.quiz_scores = new_quiz_scores()
    state.quiz_step = 0
    state.result_flavor = ""
    return Page(state, nav_bar(state) + [
        Header("Which smashed date are you?", 1),
        f"{len(QUIZ)} quick questions. No wrong answers (okay, "
        "maybe one or two).",
        LineBreak(),
        Button("Let's go", quiz_question),
    ])


@route
def quiz_question(state: State) -> Page:
    """Show the current quiz question with its answer choices."""
    question, answers = QUIZ[state.quiz_step]
    options = list(answers.keys())
    return Page(state, nav_bar(state) + [
        Header(f"Question {state.quiz_step + 1} of {len(QUIZ)}", 2),
        question,
        LineBreak(),
        SelectBox("answer", options, options[0]),
        LineBreak(),
        Button("Next", answer_question),
    ])


@route
def answer_question(state: State, answer: str) -> Page:
    """Score the chosen answer, then go to the next question or result."""
    _, answers = QUIZ[state.quiz_step]
    voted_flavor = answers[answer]
    state.quiz_scores[voted_flavor] += 1
    state.quiz_step += 1
    if state.quiz_step >= len(QUIZ):
        state.result_flavor = pick_winner(state.quiz_scores)
        return quiz_result(state)
    return quiz_question(state)


@route
def quiz_result(state: State) -> Page:
    """Reveal which flavor the visitor is and offer to buy it."""
    flavor = find_flavor(state.result_flavor)
    return Page(state, nav_bar(state) + [
        Header(f"You're {flavor.name}!", 1),
        flavor.personality,
        LineBreak(),
        LineBreak(),
        f"dates price: {format_money(flavor.price)}",
        LineBreak(),
        Button("Add my flavor to cart", add_match_to_cart),
        " ",
        Button("Retake quiz", quiz_start),
    ])


@route
def add_match_to_cart(state: State) -> Page:
    """Add one unit of the visitor's quiz-result flavor to the cart."""
    add_to_cart_items(state.cart, state.result_flavor, 1)
    return cart(state)


# ---------------------------------------------------------------------------
# Unit tests (routes with no randomness are tested via the returned state)
# ---------------------------------------------------------------------------


def run_tests() -> None:
    """Run unit tests for helpers and routes."""
    # format_money
    assert_equal(format_money(8), "$8.00")
    assert_equal(format_money(9.5), "$9.50")
    # find_flavor
    assert_equal(find_flavor("Dubai Chocolate").price, 9.5)
    assert_equal(find_flavor("Nonexistent").name, "Salted PB Chocolate")
    # subtotals and counts
    items = [CartItem("Dubai Chocolate", 2, 9.5), CartItem("Salted PB Chocolate", 1, 8.0)]
    assert_equal(item_subtotal(items[0]), 19.0)
    assert_equal(cart_subtotal(items), 27.0)
    assert_equal(cart_subtotal([]), 0.0)
    assert_equal(date_count(items), 3)
    assert_equal(cart_flavor_names(items), ["Dubai Chocolate", "Salted PB Chocolate"])
    # add / remove
    cart_list = []
    add_to_cart_items(cart_list, "Dark Chocolate Cashew", 2)
    add_to_cart_items(cart_list, "Dark Chocolate Cashew", 1)
    assert_equal(len(cart_list), 1)
    assert_equal(cart_list[0].quantity, 3)
    remove_from_cart_items(cart_list, "Dark Chocolate Cashew")
    assert_equal(cart_list, [])
    # quiz scoring
    scores = new_quiz_scores()
    assert_equal(len(scores), 5)
    scores["Dubai Chocolate"] = 2
    scores["Toasted Coconut"] = 1
    assert_equal(pick_winner(scores), "Dubai Chocolate")
    assert_equal(pick_winner(new_quiz_scores()), "Salted PB Chocolate")
    # shipping and validation
    assert_equal(shipping_cost("Local pickup in Newark, DE - Free"), 0.0)
    assert_equal(shipping_cost("Teleportation"), 0.0)
    assert_equal(validate_checkout("", "a@b.com") != "", True)
    assert_equal(validate_checkout("Sam", "nope") != "", True)
    assert_equal(validate_checkout("Sam", "sam@udel.edu"), "")
    # route: add_to_cart / remove_item
    state = State()
    result = add_to_cart(state, "Toasted Coconut", "2")
    assert_equal(result.state.cart[0].quantity, 2)
    result = remove_item(result.state, "Toasted Coconut")
    assert_equal(result.state.cart, [])
    # route: quiz_start / answer_question
    state = quiz_start(State()).state
    assert_equal(state.quiz_step, 0)
    first_answer = list(QUIZ[0][1].keys())[0]
    result = answer_question(state, first_answer)
    assert_equal(result.state.quiz_step, 1)
    assert_equal(result.state.quiz_scores["Salted PB Chocolate"], 1)
    # route: finishing the quiz sets the result
    state = quiz_start(State()).state
    for question, answers in QUIZ:
        state = answer_question(state, list(answers.keys())[4]).state
    assert_equal(state.result_flavor != "", True)
    # route: add_match_to_cart
    state.result_flavor = "Dubai Chocolate"
    result = add_match_to_cart(state)
    assert_equal(result.state.cart[0].flavor, "Dubai Chocolate")
    # route: place_order (bad input keeps the cart, good input clears it)
    state = State()
    add_to_cart_items(state.cart, "Salted PB Chocolate", 2)
    result = place_order(state, "", "x@y.com", "Standard (5-7 days) - $4.99",
                         False, "")
    assert_equal(len(result.state.cart), 1)
    result = place_order(result.state, "Sam", "sam@udel.edu",
                         "Standard (5-7 days) - $4.99", True, "Enjoy!")
    assert_equal(result.state.cart, [])
    assert_equal(result.state.order_total, 20.99)
    assert_equal(result.state.gift_note, "Enjoy!")
    # Note: index, shop, cart, checkout, confirmation, quiz_question and
    # quiz_result only build page layouts from state, so their logic is
    # covered by the helper tests above.


# ---------------------------------------------------------------------------
# Start the site
# ---------------------------------------------------------------------------

set_website_title("Save The Date")
set_site_information(
    author="Keira L",
    description="Take a personality quiz to be paired with your dream date!",
    sources="Pinterest for photos",
    planning=["Claude Conversation.docx", "Planning 0.docx", "Planning 1.docx"],
    links=["https://github.com/kikielle/save-the-date"]
)
hide_debug_information()
set_website_framed(False)
add_website_css("body", "font-family: 'Times New Roman', Times, serif; "
                        "background: #fdf6e9; "
                        "color: #4a2c17; max-width: 700px; margin: auto;")
add_website_css("h1, h2, h3", "font-family: 'Times New Roman', Times, serif;")
add_website_css("button, input[type=submit]",
                "background-color: #8b5a2b; color: white; "
                "border: none; border-radius: 8px; padding: 8px 16px; "
                "cursor: pointer;")
hide_debug_information()
run_tests()
start_server(State())
