# Speaker script — Flower Classification, 5 minutes

Slides: `flowers-slides.pdf` (10 pages, one per slide). Video: `flowers-talk.mp4` (5:00, narrated). Times per slide at a calm live pace of about 140 words a minute; the whole script is about 4:50, so speak calmly but do not add much.
**Bold** = the number or phrase to stress. `[next]` = go to the next page.
Every number comes from an output of `01_flower_classification_project_dominic.ipynb` (step numbers in brackets).

---

### 1 · Rose, sunflower or tulip? — 0:31
A garden centre wants to send its customers **the right care guide** for a flower photo they upload. Today, a member of staff looks at every photo. We built a model that chooses between **roses, sunflowers and tulips**. The catch: we only had **one hundred training photos per flower**. And at the end, we wanted to know **which photos the model gets wrong**, so the garden centre knows when to trust it. `[next]`

### 2 · Rules fixed before the first model — 0:36
Before training anything, **we fixed the rules**. The metric is **accuracy**, the share of photos that get the right guide. Our goal: **at least ninety percent** on the sixty validation photos, so **at most six mistakes**. Every photo is squeezed to **one hundred sixty by one hundred sixty** pixels, exactly like the app does it later. The thirty test photos **stayed locked** until the very end. And we added two extras: **a threshold** below which a person checks the photo, and **a nicer app**. `[next]`

### 3 · Colour or shape? — 0:31
Our first guess was: colour tells the flowers apart. **Half right.** Colour separates the sunflowers: in a typical sunflower photo, **twenty-seven percent** of the pixels are bright yellow. But roses and tulips **share their colours**, red and pink, so between those two **the shape** has to decide. We also checked that the validation photos are independent: only **six of sixty** come from a photographer in the training set, and **none is a copy**. `[next]`

### 4 · A pretrained network, frozen — 0:27
Then the main idea: **transfer learning**. MobileNetV2 has already seen **more than a million photos**. We froze it and only trained a small head on top: **three thousand eight hundred forty-three** parameters, one output per flower. We guessed **eighty-five** percent. We got **eighty-four**. And the learning curves show **overfitting after about five epochs**: training reaches one hundred percent, while validation stays flat. `[next]`

### 5 · Where it fails — 0:24
Where does it fail? **Not where we expected.** Half of the mistakes are **tulips taken for sunflowers**. Look at the photos: **parks and gardens**, where the tulips are small and yellow. At one hundred sixty pixels there is **no tulip shape left**, only yellow outside. And the model is sure of itself, **up to ninety-nine percent**. `[next]`

### 6 · Augmentation and fine-tuning — 0:32
Step five: improve it. Augmentation flips, turns and zooms the photos. Our guess: plus three points. Reality: **zero more hits**, but better probabilities and later overfitting. Then, as an extra, we **fine-tuned** the top of the network with a tiny learning rate. That was **the only step that added hits**: almost **fifty-two of sixty** on average over three runs, **eighty-six percent**. Our goal was fifty-four. **We missed it, and we did not lower it afterwards.** `[next]`

### 7 · When should a person check? — 0:27
So when should a person look at the photo? We chose a threshold of **zero point nine** on the validation photos. Above it, the model answered **forty-four of sixty** photos alone, and **forty** of those were right. **Sixteen go to staff.** But **four confident mistakes** still slip through, the yellow tulips. A threshold **cannot catch a model that is sure and wrong**. `[next]`

### 8 · One test — 0:27
Then the test, **opened exactly once**. **Twenty-nine of thirty** right. That sounds better than validation, but with thirty photos the uncertainty is large: anything between **eighty-three and one hundred percent** fits. So our validation estimate **was fair**. The one error? Sunflowers, small, in a **vegetable garden**. The model said rose, but only with **sixty-six percent**, so this photo **would have gone to staff**. `[next]`

### 9 · The app — 0:28
Finally, **the app**. You upload a photo or take one with the camera. A clear rose: **one hundred percent**, and here is your care guide. The vegetable garden: only a **best guess**, so a member of staff checks it. And our known weakness, yellow tulips in a park: **sunflower, ninety-seven percent**. That is why the app always asks customers to **photograph the blossom close up**. `[next]`

*Live option instead of the screenshots (about one minute more):* `uv run streamlit run app.py --server.address 127.0.0.1` in the repository folder, open `http://127.0.0.1:8501`, upload one clear photo and one garden photo.

### 10 · What we tell the garden centre — 0:29
So what do we tell the garden centre? **Trust** the model with close-up photos. **Let staff check** gardens and parks, and ask customers for a close-up. **Next**, we would add more garden photos and an answer for "this is not one of our three flowers". We used an AI assistant for code, slides and this video. **The guesses, the decisions and the rules were ours.** **Thank you.**

---

## If they ask (short answers)

- **Why accuracy?** All three flowers have the same number of photos in every folder, so accuracy is not distorted by one large class; a model that always says the same flower gets 33 %.
- **Why 160 × 160?** The task suggests it, MobileNetV2 has ImageNet weights for that size, and it needs about half the computation of 224 × 224.
- **Why freeze the base?** With 100 photos per flower we cannot train millions of parameters; the frozen base brings what it learned from ImageNet, only 3,843 parameters are trained (step 4).
- **Why does augmentation not help?** It makes the probabilities more honest (lower validation loss) and delays overfitting, but the errors are photos where the flower is too small to see; flipping or zooming does not change that (step 5).
- **The test (96.7 %) is better than validation (86 %). Did you overfit to validation?** No: we chose on validation and opened the test only once afterwards. With 30 photos one photo is 3.3 points, and the 95 % interval for 29 of 30 is 82.8 % to 99.9 %, so both results fit (step 6.2).
- **Why did you not lower the goal to 85 %?** A goal set after seeing the results says nothing. We report it as missed and explain why.
- **Does the app give the same answers as the notebook?** Yes, for all 30 test photos; the probabilities differ by at most 0.0000017 (step 7.1).
- **What about other flowers, like a daisy?** The model can only answer rose, sunflower or tulip, so the website has to say which flowers the service covers. An "other flower" answer is our next step.
- **Did you use AI?** Yes, as a pair programmer and for this video. We wrote down our guesses before each result and made every decision ourselves. An independent AI reference solution (`reference/`) was opened only after our model choice and our single test.
