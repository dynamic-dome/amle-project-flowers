# Flower app — 2-minute app video script

Narration in English, one audio file per slide. Screenshots come from the two extra app designs (`emotion_editions/app.py` and
`care_card/app.py`). Every number below is one the apps show or the notebook measured.

---

## Slide 1 · One model, two faces
**On screen:** "One model, two faces" · screenshots side by side: care card (rose) and Emotion editions (Smitten, rose) · same model, same rules

**Narration:**
After the analysis, the part a customer actually sees: the app. We built two designs on the same model and the same rules. One is calm, the way a garden centre would ship it. The other one is ours, with feelings.

## Slide 2 · The garden-centre version
**On screen:** screenshots rose care card · garden photo with an empty card "A member of staff will check" · above 0.90 we answer alone

**Narration:**
First, the calm one. You upload a photo or take one with the camera. When the model is at least ninety percent sure, you get a care card, like the label in a flower pot: water, cut back, pests, and a hint for the season. Below ninety percent the card stays empty, and a member of staff checks the photo.

## Slide 3 · An app with moods
**On screen:** carousel of the eight moods with the same rose: Smitten, Cheerful, Airy, Cool, Grounded, Jungle, Earth, Storm · colours, type, shapes and voice change together

**Narration:**
Then we asked: what if the app had a mood? Eight moods from our design system. Each one changes everything at once: the colours, the type, the shapes, and the voice of the text. Same rose, eight personalities.

## Slide 4 · The page follows the flower
**On screen:** Auto: sure rose → Smitten · sure sunflower → Cheerful · sure tulip → Airy · unsure → Cool, staff check, no celebration

**Narration:**
In auto mode, the page follows the result. A sure rose falls in love, a sunflower cheers, a tulip turns airy. When the model is not sure, the page calms down: lower case, no celebration, no care guide, and a member of staff checks the photo.

## Slide 5 · Honest when it is wrong
**On screen:** yellow tulips in a park → "sunflower, 96 %" · the caveat line: "Wide garden shot? Pop in close on one blossom for a surer answer!" · the close-up tip is always on screen

**Narration:**
And it stays honest. Yellow tulips in a park are still called a sunflower, ninety-six percent sure. No threshold can catch that. So every sure answer carries one more line, in the voice of the mood: wide garden shot? Photograph one blossom close up.

## Slide 6 · Try it
**On screen:** `uv run streamlit run app.py` · `cd care_card` then `uv run streamlit run app.py` · built with an AI assistant; the design choices are ours

**Narration:**
Same model, same rules, two faces. Both apps are in our repository, so you can try them with your own flower photos. Thank you.
