"""Flower care guide, "Emotion editions": a mood is a whole personality for the page.

Run it from the repo root: uv run streamlit run emotion_editions/app.py   (it needs models/step5_finetuned.keras)
The model takes raw photos (pixel values 0 to 255), does its own preprocessing and returns one probability per flower.
All mood data (colours, fonts, shapes, motion, words) lives in moods.py. This file is the flow:
photo in, probabilities out, then "which mood is on?" and "what does the page say?".
The look of the first load lives in .streamlit/config.toml (next to this file); moods.py takes over from there.
"""

import math
from pathlib import Path

import altair as alt
import keras
import numpy as np
import pandas as pd
import streamlit as st
import tensorflow as tf

from moods import AUTO, LABEL_TO_ID, MOODS, build_css

HERE = Path(__file__).parent
MODEL_PATH = HERE.parent / "models" / "step5_finetuned.keras"  # one shared model at the repo root
CLASSES = ["rose", "sunflower", "tulip"]  # the folder names, in alphabetical order, as in the training data
THRESHOLD = 0.90  # at or above this probability we answer alone; below it a person looks at the photo first (notebook 5.6 and 6.4)
CELEBRATE_AT = 0.99  # only a very sure answer lets the mood play its motion (twice, then it rests)

# Auto mood: a SURE answer wears the mood of its flower, but an UNSURE answer never does.
# If the page wore the guessed flower's mood it would look certain while the text says it is not.
FLOWER_MOOD = {"rose": "smitten", "sunflower": "cheerful", "tulip": "airy"}
UNSURE_MOOD = "cool"  # calm hand-over to staff
DEFAULT_MOOD = "grounded"  # nothing to judge yet, or something went wrong

# Short and general on purpose: the model only names the flower, the advice must be safe for any garden.
CARE_GUIDES = {
    "rose": [
        "Water deeply at the base once or twice a week, and keep the leaves dry to avoid mildew.",
        "Cut back in early spring, just above an outward-facing bud, and remove dead or crossing stems.",
        "Look for aphids and black spot; a strong jet of water or a mild soap spray helps against aphids.",
    ],
    "sunflower": [
        "Water at the base every few days while it grows; tall plants need a deep drink, not a light sprinkle.",
        "Cut off the spent flower head so the stem can be pulled out at the end of the season, or leave the seeds for birds.",
        "Slugs eat young plants and aphids like the stems; protect seedlings and check them often.",
    ],
    "tulip": [
        "Water when the soil is dry in spring; after flowering stop watering, because the bulbs like to rest dry.",
        "Cut off the flower once it fades, but leave the green leaves until they turn yellow so the bulb can recharge.",
        "Watch for aphids and for mice or voles eating the bulbs; plant the bulbs deep and in a well-drained spot.",
    ],
}


@st.cache_resource  # load the model only once, not again every time the page changes
def load_model(path):
    return keras.models.load_model(path)


def prepare_photo(photo_bytes, model):
    """Decode and resize a photo with TensorFlow, as image_dataset_from_directory did for the training photos."""
    image = tf.io.decode_image(photo_bytes, channels=3, expand_animations=False)
    height, width = model.input_shape[1:3]
    return tf.image.resize(image, (height, width))  # bilinear, the default of image_dataset_from_directory


def predict(photo_bytes, model):
    pixels = prepare_photo(photo_bytes, model)
    return model.predict(pixels[np.newaxis], verbose=0)[0]  # a batch of one photo


def pct(probability):
    """A whole percent, rounded down and never 100: 0.8969 shows as 89%, because a model is never completely sure."""
    return f"{min(math.floor(probability * 100), 99)}%"


# ---- Which mood is on? -------------------------------------------------------------------------------------

def auto_mood(probabilities, failed=False):
    """The mood the photo asks for, and why (the second value is used for the sentence under the mood row)."""
    if failed:
        return DEFAULT_MOOD, "error"
    if probabilities is None:
        return DEFAULT_MOOD, "waiting"
    if probabilities.max() < THRESHOLD:
        return UNSURE_MOOD, "unsure"
    return FLOWER_MOOD[CLASSES[int(probabilities.argmax())]], "flower"


def resolve_mood(choice, probabilities=None, failed=False):
    """Order of power: a mood picked by hand, then Auto. Returns (mood id, source)."""
    if choice in LABEL_TO_ID:
        return LABEL_TO_ID[choice], "hand"
    return auto_mood(probabilities, failed)


def motion_for(probabilities, failed=False):
    """Calm by default. Only a very sure answer plays the mood's motion, and an unsure one never does."""
    if failed:
        return "off"
    if probabilities is None:
        return "loop"
    return "twice" if probabilities.max() >= CELEBRATE_AT else "off"


def mood_note(mood_id, source, probabilities):
    """One plain sentence that says why the page looks the way it does."""
    label = MOODS[mood_id]["label"]
    if source == "hand":
        return f"You picked {label}. Choose Auto to hand the page back to the flower."
    if source == "error":
        return f"Auto: this file did not work as a photo, so the page rests in {label}."
    if source == "waiting":
        return f"Auto: until there is a photo, the page rests in {label}."
    if source == "unsure":
        return (f"Auto: the model is not sure, so the page turns {label} and a person takes a look. "
                "It never wears the guessed flower's mood.")
    return f"Auto: a sure {CLASSES[int(probabilities.argmax())]} turns the page {label}."


# ---- What the page says ------------------------------------------------------------------------------------

def header_html(mood_id, motion):
    mood = MOODS[mood_id]
    return (
        build_css(mood_id, motion)
        + '<div class="mood-head"><p class="app-name">Flower care guide'
        + f'<span class="mood-tag">{mood["label"]}</span></p>'
        + f'<div class="mark" aria-hidden="true">{mood.get("mark", "")}</div>'
        + f'<div role="heading" aria-level="1" class="headline">{mood["voice"]["headline"]}</div></div>'
    )


def tip_html(mood_id):
    """The close-up tip, in the mood's voice. It is always on the page, with or without a photo."""
    return f'<div class="note"><span class="accent">Tip</span> {MOODS[mood_id]["voice"]["tip"]}</div>'


def result_lines(mood_id, probabilities):
    """(line in the mood's voice, second line) for the result card."""
    voice = MOODS[mood_id]["voice"]
    best = CLASSES[int(probabilities.argmax())]
    if probabilities.max() < THRESHOLD:
        # An unsure answer is not celebrated and not final: "Best guess", no care guide, a person looks.
        return (voice["unsure"], f"Best guess: {best}, {pct(probabilities.max())}. "
                                  "A member of staff will check this photo before we send a care guide.")
    # A sure answer always carries the honest line: the model can be sure and wrong, e.g. yellow tulips in a
    # park that it calls "sunflower" with 0.97. The probability cannot catch that, so we say it every time.
    return voice["sure"].format(flower=best, pct=pct(probabilities.max())), voice["caveat"]


def result_card_html(mood_id, probabilities):
    unsure = probabilities.max() < THRESHOLD
    line, second = result_lines(mood_id, probabilities)
    second_html = f'<p class="sub">{second}</p>' if unsure else f'<p class="caveat">{second}</p>'
    return (f'<div class="card {"unsure" if unsure else "sure"}" role="status">'
            f'<p class="verdict">{line}</p>{second_html}</div>')


def care_html(best):
    lines = "".join(f"<li>{line}</li>" for line in CARE_GUIDES[best])
    return (f'<div class="card care"><p class="accent">Care guide for your {best}</p><ul>{lines}</ul>'
            '<p class="sub">Not your flower? Take the photo again, close up on the blossom.</p></div>')


def probability_chart(probabilities, mood_id):
    """Horizontal bars in the mood colours, with a dashed line at the threshold."""
    mood = MOODS[mood_id]
    best = CLASSES[int(probabilities.argmax())]
    table = pd.DataFrame({"flower": CLASSES, "probability": probabilities})
    bars = alt.Chart(table).mark_bar(size=18).encode(
        x=alt.X("probability:Q", scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(format="%", values=[0, 0.5, 1], title=None)),
        y=alt.Y("flower:N", sort=CLASSES, title=None),
        color=alt.condition(alt.datum.flower == best, alt.value(mood.get("bar", mood["btn_fill"])), alt.value(mood["muted"])),
    )
    line = alt.Chart(pd.DataFrame({"t": [THRESHOLD]})).mark_rule(color=mood["text"], strokeDash=[4, 3]).encode(x="t:Q")
    return ((bars + line).properties(height=110, background="transparent")
            .configure_axis(labelColor=mood["muted"], labelFontSize=13, domainColor=mood["muted"], tickColor=mood["muted"], grid=False)
            .configure_view(strokeWidth=0))


def main():
    st.set_page_config(page_title="Flower care guide", layout="centered")
    head = st.empty()  # filled at the end, because the mood can depend on the photo

    # The mood row. 'Auto' lets the photo choose.
    st.session_state.setdefault("mood", AUTO)
    choice = st.pills("Choose a mood", [AUTO] + list(LABEL_TO_ID), key="mood") or AUTO
    note = st.empty()

    # Two ways to get a photo; both give an object with getvalue(), so the rest of the app does not care which.
    # Only one input is drawn at a time, so the browser asks for the camera only if someone picks it.
    source = st.segmented_control("Send your photo by", ["Upload", "Camera"], default="Upload",
                                  required=True, label_visibility="collapsed", key="source")
    if source == "Camera":
        photo = st.camera_input("Take a photo of the blossom", label_visibility="collapsed")
    else:
        photo = st.file_uploader("A photo of a rose, a sunflower or a tulip", type=["jpg", "jpeg", "png"])
    tip = st.empty()  # the tip is in the mood's voice, so it is filled once the mood is known

    probabilities, problem = None, None
    if photo is not None:
        if not MODEL_PATH.exists():
            problem = "The model file models/step5_finetuned.keras (at the repo root) is missing. Save it in step 5 of the notebook first."
        else:
            try:
                probabilities = predict(photo.getvalue(), load_model(str(MODEL_PATH)))
            except (tf.errors.InvalidArgumentError, ValueError):
                problem = "This file could not be read as a photo. Please try a jpg or a png."

    mood_id, mood_source = resolve_mood(choice, probabilities, failed=problem is not None)

    if problem:
        st.error(problem)
    if probabilities is not None:
        best = CLASSES[int(probabilities.argmax())]
        photo_col, result_col = st.columns(2)
        photo_col.image(photo, width="stretch")
        with result_col:
            st.markdown(result_card_html(mood_id, probabilities), unsafe_allow_html=True)
            st.altair_chart(probability_chart(probabilities, mood_id), theme=None, width="stretch")
            # Not st.caption: Streamlit fades captions with an opacity that fails contrast on the light moods.
            st.markdown(f'<p class="chart-note">The dashed line is the {THRESHOLD:.0%} threshold.</p>', unsafe_allow_html=True)
        if probabilities.max() >= THRESHOLD:  # an unsure answer gets no care guide at all
            st.markdown(care_html(best), unsafe_allow_html=True)

    head.markdown(header_html(mood_id, motion_for(probabilities, problem is not None)), unsafe_allow_html=True)
    tip.markdown(tip_html(mood_id), unsafe_allow_html=True)
    note.markdown(f'<p class="hint">{mood_note(mood_id, mood_source, probabilities)}</p>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
