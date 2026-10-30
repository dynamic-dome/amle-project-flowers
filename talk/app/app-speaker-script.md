# Speaker script — the app, about 2 minutes

Slides: `app-slides.pdf` (6 pages, one per slide). The narrated video `app-video.mp4` shows the same slides with the same words, so it is the
fallback if you prefer to play instead of speak. Times per slide at a calm live pace of about 140 words a minute; the whole script is
about 1:50 without the live demo, about 3 minutes with it.
**Bold** = the word or number to stress. `[next]` = go to the next page. `[demo]` = optional live moment, see the end.

---

### 1 · One model, two faces — 0:20
After the analysis, the part a customer actually sees: **the app**. We built **two designs** on the **same model** and the **same rules**. One is **calm**, the way a garden centre would ship it. The other one is ours, **with feelings**. `[next]`

### 2 · The garden-centre version — 0:28
First, the calm one. You upload a photo or take one with the camera. When the model is **at least ninety percent sure**, you get a **care card**, like the label in a flower pot: water, cut back, pests, and a hint for the season. **Below ninety percent** the card stays empty, and **a member of staff checks** the photo. `[next]`

### 3 · Same rose, eight moods — 0:20
Then we asked: what if the app had **a mood**? **Eight moods** from our design system. Each one changes **everything at once**: the colours, the type, the shapes, and **the voice of the text**. **Same rose, eight personalities.** `[next]`

### 4 · Auto: the page follows the flower — 0:24
In **auto mode**, the page follows the result. A sure rose **falls in love**, a sunflower **cheers**, a tulip turns **airy**. When the model is **not sure**, the page **calms down**: lower case, **no celebration**, no care guide, and a member of staff checks the photo. `[next]` *(or `[demo]` here)*

### 5 · Honest when it is wrong — 0:22
And it stays **honest**. Yellow tulips in a park are still called a sunflower, **ninety-six percent sure**. **No threshold can catch that.** So every sure answer carries **one more line**, in the voice of the mood: *wide garden shot? Photograph one blossom close up.* `[next]`

### 6 · Try it with your own flower photos — 0:12
**Same model, same rules, two faces.** Both apps are in our repository, so you can try them with **your own flower photos**. **Thank you.**

---

## Optional live demo (about 1 minute, after slide 4)

**Prepare 10 minutes before** (TensorFlow needs 45 to 90 seconds the first time, that must not happen live):
1. In a terminal in the repository folder: `uv run streamlit run emotion_editions/app.py --server.address 127.0.0.1`
2. Open `http://127.0.0.1:8501` in the browser (zoom 125 % for the projector), upload one photo once so the model is warm, then remove it.
3. Keep these photos at hand (all in the repository):
   - clear rose: `data/test/rose/2675221506_5286c0595f.jpg`
   - sure sunflower: `data/validation/sunflower/4933823922_911ac40b0d.jpg`
   - sunflowers in a vegetable garden (unsure): `data/test/sunflower/2807106374_f422b5f00c.jpg`
   - yellow tulips in a park (sure and wrong): `data/validation/tulip/7166640338_46b15d9ec8_n.jpg`

**What to do and say:**
1. Mood row on **Auto**, upload the **clear rose**: "A sure rose, and the page **falls in love**." *(Smitten, 99 %)*
2. Upload the **sure sunflower**: "A sunflower, and it **cheers**." *(Cheerful)*
3. Upload the **vegetable garden**: "Here the model is **not sure**, sixty-six percent. The page calms down, and **a member of staff checks**." *(Cool, no care guide)*
4. Click **Earth** or **Storm** in the mood row: "Any mood can also be **picked by hand**." Then back to slide 5.

If anything hangs: say "the video shows the same" and go on with the slides.

---

## If they ask (short answers)

- **Does the mood change the prediction?** No. Both designs use the same model file, the same photo preparation and the same 0.90 threshold. The mood only changes how the result looks and sounds.
- **Why two designs?** The care card is what a garden centre would ship: calm and practical. The mood version is our own idea, to show that the same honest result can be presented in very different ways.
- **Why 0.90?** We chose it on the validation photos: above it, 40 of 44 answers were right; on the test photos all 26 answers above it were right. Below it, a person looks.
- **The yellow tulips are still wrong. Why not fix that?** The model is sure and wrong, so no threshold catches it. The flower is a few pixels in a wide scene. The honest fix is a better photo, which is why the close-up tip is always on screen.
- **Is it accessible?** We checked the text contrast of every mood: at least 4.5 to 1. Motion is switched off for people who ask their system for reduced motion.
- **Does it run on a phone?** Yes, the layout works at phone width and the camera tab only opens when you choose it. It can be deployed on Streamlit Community Cloud.
- **Did you use AI?** Yes, an AI assistant built the code, the slides and the video with us. The moods come from our own design system, and the decisions, the rules and the threshold were ours.
