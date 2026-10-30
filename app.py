"""Tell a garden centre which care guide to send, rose, sunflower or tulip, from a customer's photo.

Run it from the repository folder: uv run streamlit run app.py

The model must take the raw photos (pixel values 0 to 255) and do its own preprocessing, for example with
mobilenet_v2.preprocess_input inside the model, and it must output one probability per flower.
"""

from pathlib import Path

import keras
import numpy as np
import pandas as pd
import streamlit as st
import tensorflow as tf

CLASSES = ["rose", "sunflower", "tulip"]  # the folder names, in alphabetical order, as in the training data
CHOSEN_MODEL = "step5_finetuned.keras"  # our choice in step 5 of the notebook, selected by default

# Below this probability a person looks at the photo first. Chosen on the validation photos (notebook 5.6):
# above 0.90, 40 of 44 answers were right; on the test photos 26 of 26 (notebook 6.4).
THRESHOLD = 0.90

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


@st.cache_resource  # load each model only once, not again every time the page changes
def load_model(path):
    return keras.models.load_model(path)


def prepare_photo(photo_bytes, model):
    """Decode and resize a photo with TensorFlow, as image_dataset_from_directory did for the training photos."""
    image = tf.io.decode_image(photo_bytes, channels=3, expand_animations=False)
    height, width = model.input_shape[1:3]
    return tf.image.resize(image, (height, width))  # bilinear, the default of image_dataset_from_directory


st.set_page_config(page_title="Flower Classifier", page_icon="🌸")
st.title("🌸 Flower Classifier")
st.write(
    "We recognise **roses, sunflowers and tulips**. "
    "A photo of any other flower still gets one of these three answers, so please check the result."
)

model_files = sorted(Path("models").glob("*.keras"))
if not model_files:
    st.error("No model found in `models/`. Save a model there in step 5 of the notebook first.")
    st.stop()

names = [path.name for path in model_files]
model_path = st.selectbox("Model", model_files, format_func=lambda path: path.name,
                          index=names.index(CHOSEN_MODEL) if CHOSEN_MODEL in names else 0)
model = load_model(str(model_path))

# Two ways to get a photo; both give an object with getvalue(), so the rest of the app does not care which.
upload_tab, camera_tab = st.tabs(["Upload a photo", "Take a photo"])
with upload_tab:
    uploaded = st.file_uploader("A photo of a rose, a sunflower or a tulip", type=["jpg", "jpeg", "png"])
with camera_tab:
    taken = st.camera_input("Take a photo of the blossom")
photo = uploaded or taken  # if both are filled, the upload wins

# The model is weakest on whole gardens, so we always tell customers how to take a good photo.
st.info("Tip: photograph the blossom close up. Whole gardens and parks confuse the model.", icon="💡")

if photo is not None:
    pixels = prepare_photo(photo.getvalue(), model)
    probabilities = model.predict(pixels[np.newaxis], verbose=0)[0]  # a batch of one photo
    best = CLASSES[probabilities.argmax()]
    unsure = probabilities.max() < THRESHOLD

    photo_col, result_col = st.columns(2)
    photo_col.image(photo, width="stretch")
    with result_col:
        # "Best guess" instead of "Prediction" when unsure, so it does not look like a final answer
        st.subheader(f"{'Best guess' if unsure else 'Prediction'}: {best} ({probabilities.max():.0%})")
        st.bar_chart(pd.Series(probabilities, index=CLASSES, name="probability"), horizontal=True)

    # A probability alone cannot catch every mistake (small yellow tulips in a park look like sunflowers with
    # 0.9 or more), so the threshold only catches the unsure cases. The tip above helps with the rest.
    if unsure:
        st.warning("A member of staff will check this photo before we send a care guide.", icon="👀")
    else:
        st.success(f"Care guide for your {best}", icon="🌱")
        with st.container(border=True):
            st.markdown("\n".join(f"- {line}" for line in CARE_GUIDES[best]))
