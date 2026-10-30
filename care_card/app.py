"""Flower care desk: a customer sends a photo of a rose, a sunflower or a tulip and gets the right care card.

Run it from the repo root: uv run streamlit run care_card/app.py   (it needs models/step5_finetuned.keras)

The model takes raw photos (pixel values 0 to 255), does its own preprocessing inside, and returns one
probability per flower. The look lives in .streamlit/config.toml (theme) and style.css (the care card).
"""

import datetime
from pathlib import Path

import keras
import numpy as np
import streamlit as st
import tensorflow as tf

HERE = Path(__file__).parent
CLASSES = ["rose", "sunflower", "tulip"]  # alphabetical folder names, as in the training data
MODEL_PATH = HERE.parent / "models" / "step5_finetuned.keras"  # one shared model at the repo root

# At this probability or above we answer alone (0.90 counts as sure). Below it a person looks at the photo first
# (chosen on the validation photos, notebook 5.6).
THRESHOLD = 0.90

# Short and general on purpose: the model only names the flower, so the advice must be safe for any garden.
FLOWERS = {
    "rose": {
        "latin": "Rosa",
        "care": [
            "Water deeply at the base once or twice a week. Keep the leaves dry to avoid mildew.",
            "Cut back in early spring, just above an outward-facing bud. Remove dead or crossing stems.",
            "Look for aphids and black spot. A strong jet of water or a mild soap spray helps against aphids.",
        ],
        "season": {
            "spring": "Prune now and feed with a rose fertiliser as the first leaves open.",
            "summer": "Snip off faded blooms to keep new flowers coming.",
            "autumn": "Stop feeding. Rake up fallen leaves, because they can carry black spot.",
            "winter": "Bare-root roses can be planted on frost-free days.",
        },
    },
    "sunflower": {
        "latin": "Helianthus annuus",
        "care": [
            "Water at the base every few days while it grows. Tall plants need a deep drink, not a light sprinkle.",
            "When the head fades, leave it for the birds or cut it off and dry the seeds. Pull the stem out at season end.",
            "Slugs eat young plants and aphids like the stems. Protect seedlings and check them often.",
        ],
        "season": {
            "spring": "Sow seeds outdoors once the last frost has passed.",
            "summer": "Stake tall plants and water deeply in dry spells.",
            "autumn": "Leave the seed heads for birds, or cut and dry them.",
            "winter": "Nothing to do outside. A good time to order seeds.",
        },
    },
    "tulip": {
        "latin": "Tulipa",
        "care": [
            "Water when the soil is dry in spring. After flowering, stop: the bulbs like to rest dry.",
            "Cut off the flower once it fades, but leave the green leaves until they turn yellow so the bulb can recharge.",
            "Watch for aphids, and for mice or voles eating the bulbs. Plant bulbs deep, in a well-drained spot.",
        ],
        "season": {
            "spring": "Enjoy the bloom. Afterwards remove the flower, not the leaves.",
            "summer": "The bulbs rest. In wet soil, lift them and keep them dry.",
            "autumn": "Planting time: set bulbs pointed end up, about three times as deep as the bulb is tall.",
            "winter": "Nothing to do. The bulbs sleep under the soil.",
        },
    },
}
CARE_LABELS = ["Water", "Cut back", "Pests"]  # one label per line of "care"
# Northern-hemisphere seasons (Dec-Feb winter, ...). A garden centre in the south would flip this table.
SEASON_OF_MONTH = ["winter", "winter", "spring", "spring", "spring", "summer",
                   "summer", "summer", "autumn", "autumn", "autumn", "winter"]

TIP = ("<b>Photograph the blossom close up.</b> Gardens and parks confuse the model: "
       "in our tests, yellow tulips in a park were taken for sunflowers.")


@st.cache_resource  # load the model once, not again every time the page changes
def load_model(path):
    return keras.models.load_model(path)


def prepare_photo(photo_bytes, model):
    """Decode and resize exactly as the training photos were (bilinear, no crop)."""
    image = tf.io.decode_image(photo_bytes, channels=3, expand_animations=False)
    return tf.image.resize(image, model.input_shape[1:3])


def predict(model, photo_bytes):
    pixels = prepare_photo(photo_bytes, model)
    return model.predict(pixels[np.newaxis], verbose=0)[0]  # a batch of one photo


def percent(p):
    # Round down and never show 100: a 0.899 that goes to staff must not show up as "90 %", and no model is 100 % sure.
    # A no-break space (written \u00a0) keeps the number and the sign together.
    nbsp = "\u00a0"
    return f"under 1{nbsp}%" if p < 0.01 else f"{min(int(p * 100), 99)}{nbsp}%"


def card_html(flower, probability, today):
    """The care card as one HTML block. It is also what the customer downloads, so it must stand alone."""
    info = FLOWERS[flower]
    season = SEASON_OF_MONTH[today.month - 1]
    rows = "".join(f'<div class="row"><div class="what">{label}</div><p>{text}</p></div>'
                   for label, text in zip(CARE_LABELS, info["care"]))
    return (f'<div class="card {flower}"><div class="band"><div class="name">{flower.capitalize()}</div>'
            f'<div class="latin">{info["latin"]}</div></div>{rows}'
            f'<div class="row season"><div class="what">In {season}</div><p>{info["season"][season]}</p></div>'
            f'<div class="foot">Matched from your photo, {percent(probability)} sure. Flower care desk, {today:%d %b %Y}.</div></div>')


def verdict_html(probabilities):
    """The answer as a big line in the flower's colour, with the rule stated plainly. It sits above the photo."""
    best = CLASSES[probabilities.argmax()]
    others = ", ".join(f"{CLASSES[i]} {percent(probabilities[i])}" for i in np.argsort(probabilities)[::-1][1:])
    rule = f'<div class="rule">At {THRESHOLD:.2f} or above we answer alone. Below, staff check.</div>'
    if probabilities.max() >= THRESHOLD:
        return (f'<div class="verdict {best}"><div class="big">{percent(probabilities.max())} sure: it is a {best}.</div>'
                f'<div class="also">Also possible: {others}.</div>{rule}</div>')
    return (f'<div class="verdict unsure"><div class="big">Not sure enough.</div>'
            f'<div class="also">First guess: {best}, {percent(probabilities.max())}. This is not final. Others: {others}.</div>{rule}</div>')


def ghost_html(title, text):
    return f'<div class="ghost"><div class="name">{title}</div><p>{text}</p></div>'


def card_page(card):
    """A self-contained HTML file the customer can keep or print."""
    css = (HERE / "style.css").read_text(encoding="utf-8")
    fonts = "https://fonts.googleapis.com/css2?family=Fraunces:wght@600&family=Inter:wght@400;600&display=swap"
    return (f'<!doctype html><html lang="en"><meta charset="utf-8"><title>Care card</title>'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<link rel="stylesheet" href="{fonts}"><style>body{{background:#F4F7F2;padding:24px}}{css}</style>'
            f'<body>{card}</body></html>')


def main():
    st.set_page_config(page_title="Flower care desk", page_icon="🌿", layout="wide")
    st.html(HERE / "style.css")  # a Path is read as a file; style-only HTML takes no space on the page

    if not MODEL_PATH.exists():
        st.error("The model file models/step5_finetuned.keras (at the repo root, next to care_card) is missing. Save it in step 5 of the notebook first.")
        st.stop()
    model = load_model(str(MODEL_PATH))

    probabilities = None
    photo = None
    with st.container(key="page"):
        st.html('<div class="wordmark"><i></i>Flower care desk</div>')
        left, right = st.columns([5, 4], gap="large")  # on a phone the right column simply goes underneath

        with left:
            st.title("Send a photo, get a care card")
            st.write("We know roses, sunflowers and tulips. Nothing else yet.")

            # Only one input is drawn at a time, so the camera permission is asked only if someone picks it.
            source = st.segmented_control("Send your photo by", ["Upload", "Camera"], default="Upload",
                                          required=True, label_visibility="collapsed")
            if source == "Camera":
                photo = st.camera_input("Take a photo of the blossom", label_visibility="collapsed")
            else:
                photo = st.file_uploader("A photo of a rose, a sunflower or a tulip", type=["jpg", "jpeg", "png"])
            st.html(f'<div class="tip">{TIP}</div>')  # always visible

            if photo is not None:
                try:
                    probabilities = predict(model, photo.getvalue())
                except (tf.errors.InvalidArgumentError, ValueError):
                    st.error("We could not read this photo. Try a JPG or PNG.")
                else:
                    best = CLASSES[probabilities.argmax()]
                    st.html(verdict_html(probabilities))  # above the photo, so it is the first thing to read
                    st.image(photo, width="stretch")

        with right:
            today = datetime.date.today()
            if probabilities is None:
                st.html(ghost_html("Your care card will appear here",
                                   "Add a photo and we check it against roses, sunflowers and tulips."))
            elif probabilities.max() < THRESHOLD:
                # No care guide here: a wrong guide is worse than a short wait.
                st.html(ghost_html("A member of staff will check your photo",
                                   "We are not sure enough to name the flower. You get your care card after the check. "
                                   "A close-up of the blossom often helps, and you can send a new photo any time."))
            else:
                card = card_html(CLASSES[probabilities.argmax()], probabilities.max(), today)
                st.html(card)
                st.download_button("Save the care card", card_page(card), file_name=f"care-card-{best}.html",
                                   mime="text/html", icon=":material/download:", on_click="ignore")

        with st.expander("How reliable is this?"):
            st.markdown(
                "- **Validation photos:** 51 of 60 right (85\u00a0%); mean of 3 training seeds 51.7 of 60 (86\u00a0%). "
                "Our goal of 90\u00a0% was **not reached**.\n"
                "- **Test photos:** 29 of 30 right (96.7\u00a0%), 95\u00a0% interval 82.8\u00a0% to 99.9\u00a0%.\n"
                "- **With the 0.90 rule on test:** 26 of 30 answered alone, all right; 4 went to staff.\n"
                "- **With the 0.90 rule on validation:** 44 of 60 answered alone, 40 right; "
                "16 went to staff and 4 confident answers were wrong.\n"
                "- The model only knows three flowers. Any other flower still gets one of the three names."
            )


if __name__ == "__main__":  # importing this file (for tests) does not draw the page
    main()
