"""The eight moods of "Emotion editions" and the CSS that turns one of them into a whole page personality.

A mood is more than a palette: eight moods, each a whole personality. Each one switches seven things at once:
colours, fonts (heading + body), case rule, shape (radius or clip-path), ONE signature motion, the voice of the
copy, and the small flourishes (mark, list style). The layout never changes, so the app stays easy to use.

Every colour pair that carries text was checked for a contrast of at least 4.5 to 1. Where a first choice fell
short, the colour was darkened or lightened and is marked "contrast" below. Accent colours are only used as text
on the card surface, never on the page gradient, because accent text on the darkest gradient stop of Smitten,
Cheerful and Airy would be below 4.5.
"""

import re
from string import Template

AUTO = "Auto"


def google_fonts(*families):
    """One Google Fonts stylesheet URL for all the families a mood needs (so the page loads one @import)."""
    query = "&".join("family=" + family.replace(" ", "+") for family in families)
    return f"https://fonts.googleapis.com/css2?{query}&display=swap"


# Font stacks with system fallbacks: if Google Fonts is blocked or slow, the page still looks close.
SERIF = '"Fraunces","Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif'
GROTESK = '"Space Grotesk",system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif'
SANS = '"Inter",system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif'

# CSS selectors for "all Streamlit buttons on the page", "the solid ones" and the pills, used by the mood fragments below.
# Streamlit 1.66 gives pills no data-testid: a pill is button[data-variant="pills"] and the chosen one has aria-checked="true".
PILL = '[data-testid="stMain"] button[data-variant="pills"]'
PILL_ON = PILL + '[aria-checked="true"]'
BTN = ('[data-testid="stMain"] :is([data-testid="stBaseButton-primary"],[data-testid="stBaseButton-secondary"],'
       '[data-testid="stCameraInputButton"],button[data-variant="pills"],button[data-variant="segmented_control"])')
SOLID = '[data-testid="stMain"] :is([data-testid="stBaseButton-primary"],[data-testid="stCameraInputButton"])'

# What a mood needs unless it says otherwise.
DEFAULTS = dict(
    scheme="dark", case="none", head_weight="500", body_weight="400", stops=(),
    btn_end=None, edge="transparent", line="color-mix(in srgb,var(--accent) 28%,var(--bg))",
    r_btn="10px", r_card="12px", clip_btn="none", clip_card="none", ring="2px",
    btn_extra="", card_extra="", keyframes="", ambient="", hover="", extra="", mark="",
)

# label = the name on the button. voice = the words of the page: headline, line when sure, line when unsure,
# close-up tip. caveat = the always-visible honest line under a sure answer.
MOODS = {
    "smitten": dict(
        label="Smitten", scheme="light",
        bg="#FAEEF3", stops=("#FBF2F8", "#FAE5EC", "#FADBE1"), surface="#FDF5F9", text="#472834", muted="#684C56",
        accent="#B74278",  # contrast: accent as text, darkened a little
        btn_fill="#C44275", btn_end="#B2417F", btn_label="#FBF7F9",  # contrast: a lighter fill gave only 3.75 for the label
        fonts=google_fonts("Fraunces:opsz,wght@9..144,500;9..144,600", "Inter:wght@400;500;600"),
        font_head=SERIF, font_body=SANS, head_weight="500",
        r_btn="999px", r_card="24px",
        btn_extra="box-shadow:0 14px 34px -12px color-mix(in srgb,var(--btn) 70%,transparent);font-weight:600;",
        card_extra="border:1.5px solid var(--line);box-shadow:0 18px 44px -20px color-mix(in srgb,var(--btn) 35%,transparent);",
        mark='<span class="heart">&#9829;</span>',
        keyframes="@keyframes beat{0%,100%{transform:scale(1)}12%{transform:scale(1.14)}24%{transform:scale(1)}"
                  "36%{transform:scale(1.1)}48%{transform:scale(1)}}",
        ambient=".mark{animation:beat 2.4s ease-in-out $plays}",
        hover="$BTN{transition:transform .3s cubic-bezier(.34,1.56,.64,1)}"
              "$BTN:hover{transform:translateY(-3px);filter:brightness(1.06)}",
        extra=".mark{color:var(--btn);font-size:2rem;line-height:1}",
        voice=dict(
            headline="Falling for every flower.",
            sure="Oh, a {flower}! I am {pct} sure.",
            unsure="My heart says maybe. Staff will check your photo.",
            tip="Come closer. Give the petals your full attention.",
            caveat="Was that a wide garden shot? Come close to one blossom and my heart will be surer.",
        ),
    ),
    "cheerful": dict(
        label="Cheerful", scheme="light",
        bg="#FAF1DC", stops=("#FBF5DF", "#FBE9C6"), surface="#FEFCF4", text="#34251A", muted="#5A493D",
        accent="#BB4C00",  # contrast: accent as text, darkened (a lighter orange gave 3.75)
        btn_fill="#C2520B", btn_label="#FEFCF4",  # contrast: a lighter fill gave only 4.09 for the label
        fonts=google_fonts("Space Grotesk:wght@700", "Inter:wght@400;600;700"),
        font_head=GROTESK, font_body=SANS, head_weight="700",
        r_btn="999px", r_card="28px",
        btn_extra="box-shadow:0 10px 30px -8px color-mix(in srgb,var(--btn) 60%,transparent);font-weight:700;",
        card_extra="border:2px solid var(--line);",
        mark='<i></i><i></i><i></i><i></i><i></i>',
        keyframes="@keyframes bounce{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}",
        ambient=".mark i{animation:bounce 2.6s ease-in-out $plays}"
                ".mark i:nth-child(2){animation-delay:.2s}.mark i:nth-child(3){animation-delay:.4s}"
                ".mark i:nth-child(4){animation-delay:.6s}.mark i:nth-child(5){animation-delay:.8s}",
        hover="$BTN{transition:transform .3s cubic-bezier(.34,1.56,.64,1)}"
              "$BTN:hover{transform:translateY(-3px) rotate(1deg)}",
        # Confetti dots are decoration (aria-hidden), so their colours are free. A small tilt makes the card playful.
        extra=".mark{display:flex;gap:.4rem;top:.2rem}.mark i{width:.7rem;height:.7rem;border-radius:50%}"
              ".mark i:nth-child(1){background:#F08A3C}.mark i:nth-child(2){background:#419547}"
              ".mark i:nth-child(3){background:#4A90D9}.mark i:nth-child(4){background:#F2C230}"
              ".mark i:nth-child(5){background:#E0559E}.mark i:nth-child(2n){border-radius:3px}"
              ".card.sure{transform:rotate(-.6deg)}",
        voice=dict(
            headline="Flowers make everything better!",
            sure="Yay, a {flower}! {pct} sure!",
            unsure="Oh! Not sure yet. Staff will check your photo!",
            tip="Get close and fill the frame with colour!",
            caveat="Wide garden shot? Pop in close on one blossom for a surer answer!",
        ),
    ),
    "airy": dict(
        label="Airy", scheme="light",
        bg="#F0F6F9", stops=("#F4F9FB", "#E5F1F7", "#D5E8F3"), surface="#F8FBFD", text="#252F37", muted="#444F57",
        accent="#2677A1",  # contrast: accent as text, darkened (a lighter blue gave 4.38)
        btn_fill="#1F6C94", btn_label="#F0F6F9",  # a true blue, so the button looks like the mood
        fonts=google_fonts("Space Grotesk:wght@300;500", "Inter:wght@400;500;600"),
        # Body weight stays 400 (not 300) so small text stays readable.
        font_head=GROTESK, font_body=SANS, head_weight="300", body_weight="400",
        r_btn="999px", r_card="26px",
        btn_extra="letter-spacing:.04em;font-weight:500;box-shadow:0 20px 44px -18px color-mix(in srgb,var(--btn) 55%,transparent);",
        card_extra="box-shadow:0 24px 60px -28px rgba(37,47,55,.35);",
        mark='<span class="cloud"></span>',
        keyframes="@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}",
        ambient=".mark,.card{animation:float 8s ease-in-out $plays}.card.care{animation-delay:1.5s}",
        hover="$BTN{transition:transform .3s ease}$BTN:hover{transform:translateY(-2px)}",
        # A float of 8px is enough when people have to read the card.
        extra=".mark{top:.9rem;right:.6rem}.cloud{display:block;position:relative;width:4.6rem;height:1.4rem;border-radius:999px;"
              "background:color-mix(in srgb,var(--accent) 30%,#fff);"
              "filter:drop-shadow(0 8px 8px color-mix(in srgb,var(--accent) 35%,transparent))}"
              ".cloud::before,.cloud::after{content:'';position:absolute;border-radius:50%;background:inherit;pointer-events:none}"
              ".cloud::before{width:1.9rem;height:1.9rem;left:.8rem;bottom:.5rem}"
              ".cloud::after{width:2.4rem;height:2.4rem;left:1.9rem;bottom:.45rem}",
        bar="#2677A1",
        voice=dict(
            headline="Light as a petal. Name any flower.",
            sure="A {flower}, {pct} certain, drifting your way.",
            unsure="Too hazy to say. Staff will gently check your photo.",
            tip="Float closer. One bloom, soft daylight.",
            caveat="A wide view can blur things. Float in close on one blossom for a surer answer.",
        ),
    ),
    "cool": dict(
        label="Cool",
        bg="#0D1218", stops=("#0E141C", "#080E13"), surface="#141B23", text="#D0D9E1", muted="#97A0A7",
        accent="#5DCBD1", btn_fill="#5DCBD1", btn_label="#060E15",
        fonts=google_fonts("Space Grotesk:wght@500;600", "Inter:wght@400;600"),
        font_head=GROTESK, font_body=SANS, head_weight="500", case="lowercase",  # the whole page is lowercase
        r_btn="10px", r_card="14px",
        btn_extra="font-weight:600;",
        card_extra="border:1px solid var(--line);",
        # The one motion is a soft lift on hover: nothing moves by itself, which keeps this mood calm.
        hover=".card{transition:transform .35s cubic-bezier(.2,.8,.2,1),border-color .35s}"
              ".card:hover{transform:translateY(-3px);border-color:color-mix(in srgb,var(--btn) 50%,transparent)}"
              "$BTN{transition:transform .35s cubic-bezier(.2,.8,.2,1)}$BTN:hover{transform:translateY(-2px)}",
        extra='.stApp::before{content:"";position:fixed;z-index:-1;inset:0;pointer-events:none;'
              'background:radial-gradient(ellipse at 50% 20%,color-mix(in srgb,var(--accent) 12%,transparent),transparent 65%)}',
        voice=dict(
            headline="got a flower? let's see.",
            sure="looks like a {flower}. {pct} sure, no stress.",
            unsure="not sure. staff will check, all good.",
            tip="get a bit closer, one bloom, easy.",
            caveat="wide garden shot? get close on one bloom, surer answer, easy.",
        ),
    ),
    "grounded": dict(
        label="Grounded",
        bg="#111318", surface="#15181E", text="#E4E0D8", muted="#B1ABA0",
        accent="#DAB04E", btn_fill="#DAB04E", btn_label="#0B0D14",
        fonts=google_fonts("Fraunces:opsz,wght@9..144,500", "Inter:wght@400;500;600"),
        font_head=SERIF, font_body=SANS, head_weight="500",
        r_btn="10px", r_card="10px",
        btn_extra="font-weight:600;",
        card_extra="border:1px solid var(--line);",
        mark='<span class="ornament"></span>',
        # Static on purpose: no motion at all. A letterhead header, and the care guide as a numbered list of rows.
        extra=".mood-head{text-align:center;padding-bottom:1rem;border-bottom:3px double color-mix(in srgb,var(--accent) 50%,transparent)}"
              ".app-name{justify-content:center}"
              ".mark{position:static;display:block;margin:.8rem 0 .5rem}"
              ".stApp .headline{margin-right:0;margin-top:.2rem}"
              # A drawn ornament (two thin rules and a diamond) instead of three tiny dashes of text.
              ".ornament{position:relative;display:block;width:9rem;height:1rem;margin:0 auto;"
              "background:linear-gradient(var(--accent),var(--accent)) left center/3.6rem 1px no-repeat,"
              "linear-gradient(var(--accent),var(--accent)) right center/3.6rem 1px no-repeat}"
              ".ornament::before{content:'';position:absolute;left:50%;top:50%;width:.6rem;height:.6rem;"
              "background:var(--accent);transform:translate(-50%,-50%) rotate(45deg);pointer-events:none}"
              ".care ul{list-style:none;counter-reset:row;padding:0}"
              ".care li{counter-increment:row;display:grid;grid-template-columns:2.6rem 1fr;"
              "padding:.7rem 0;border-bottom:1px solid var(--line)}"
              '.care li::before{content:counter(row,decimal-leading-zero);font-family:var(--font-head);color:var(--accent)}',
        voice=dict(
            headline="Know your flower. The honest way.",
            sure="That is a {flower}. We are {pct} sure.",
            unsure="Not sure enough. Our staff will check your photo.",
            tip="Move closer. One bloom, plain light, steady hand.",
            caveat="A wide garden shot can fool the model. Photograph one blossom close up for a surer answer.",
        ),
    ),
    "jungle": dict(
        label="Jungle",
        bg="#000B02", surface="#001D07", text="#DAEAD7", muted="#AEC5AE",
        accent="#8EE258", btn_fill="#5FBF49", btn_end="#008B4E", btn_label="#000E02",  # contrast: label on the end colour is 4.52
        fonts=google_fonts("Fraunces:opsz,wght@9..144,500", "Inter:wght@400;500;600"),
        font_head=SERIF, font_body=SANS, head_weight="500",
        r_btn="999px 999px 999px 6px", r_card="28px 28px 28px 8px",  # organic: one corner stays tight, like a leaf
        btn_extra="font-weight:600;box-shadow:0 12px 40px -12px color-mix(in srgb,var(--btn) 50%,transparent);",
        card_extra="border:1px solid var(--line);",
        mark='<svg class="leaf" viewBox="0 0 24 24" width="40" height="40" aria-hidden="true"><path d="M3 21C2 10 9 3 22 2C22 15 15 22 3 21Z" fill="currentColor"/>'
         '<path d="M3 21L15 9" stroke="var(--bg)" stroke-width="1.4" stroke-linecap="round" fill="none"/></svg>',
        keyframes="@keyframes sway{0%,100%{transform:rotate(-5deg)}50%{transform:rotate(5deg)}}",
        ambient=".mark{transform-origin:50% 100%;animation:sway 9s ease-in-out $plays}",
        hover=".card{transition:transform .3s ease,box-shadow .3s ease}"
              ".card:hover{transform:translateY(-4px);box-shadow:0 14px 40px -14px color-mix(in srgb,var(--btn) 60%,transparent)}",
        # A single glyph needs a sway of about 5 degrees to be seen.
        extra=".mark{color:var(--btn);line-height:0}.leaf{display:block}.app-name::before{content:'\\273F'}",
        voice=dict(
            headline="What is growing in your garden?",
            sure="A {flower}, thriving at {pct} certainty.",
            unsure="Thick undergrowth here. A gardener will check your photo.",
            tip="Push closer through the leaves, one bloom at a time.",
            caveat="Wide garden shot? Thick leaves can hide the truth. Push in close on one blossom for a surer answer.",
        ),
    ),
    "earth": dict(
        label="Earth",
        bg="#21160C", stops=("#271A0D", "#22150B", "#1D1009", "#180C06"),  # the page fades smoothly; the sediment layers live in the margins
        surface="#2F1D0B", text="#EADFD3", muted="#CFC2B3",
        accent="#DAA75D", btn_fill="#C99B5A", btn_label="#201308", edge="#815A2D",
        fonts=google_fonts("Fraunces:opsz,wght@9..144,600", "Inter:wght@400;600;700"),
        font_head=SERIF, font_body=SANS, head_weight="600",
        r_btn="4px", r_card="6px", line="color-mix(in srgb,var(--edge) 75%,var(--bg))",
        btn_extra="font-weight:700;box-shadow:0 5px 0 var(--edge),0 14px 30px -10px rgba(10,6,3,.8);",
        card_extra="border:3px solid var(--line);",
        mark='<span class="strata"><i></i><i></i><i></i><i></i></span>',
        # The one motion is a 3D press: the button sinks 2px on hover and all the way down while pressed.
        hover="$SOLID{transition:transform .12s,box-shadow .12s}"
              "$SOLID:hover{transform:translateY(2px);box-shadow:0 3px 0 var(--edge),0 8px 20px -8px rgba(10,6,3,.8)}"
              "$SOLID:active{transform:translateY(5px);box-shadow:0 0 0 var(--edge)}",
        # Sediment layers with hard edges, but only in the side margins of wide screens, so no band edge crosses a control.
        extra="@media (min-width:900px){.stApp::before{content:'';position:fixed;z-index:-1;inset:0;pointer-events:none;"
              "background:linear-gradient(180deg,#2A1C0E 0 22%,#241709 22% 47%,#1F1209 47% 71%,#1A0E07 71%);"
              "-webkit-mask-image:linear-gradient(90deg,#000 0 14%,transparent 14% 86%,#000 86%);"
              "mask-image:linear-gradient(90deg,#000 0 14%,transparent 14% 86%,#000 86%)}}"
              ".strata{display:block;width:3.2rem}.strata i{display:block;height:.45rem;margin-bottom:.15rem}"
              ".strata i:nth-child(1){background:#5A3E1F}.strata i:nth-child(2){background:#815A2D}"
              ".strata i:nth-child(3){background:#A67A3E}.strata i:nth-child(4){background:#C99B5A}"
              ".care ul{list-style:none;padding:0}"
              ".care li{margin:.4rem 0;padding:.55rem .8rem;border-left:8px solid var(--edge);border-bottom:3px solid var(--line)}",
        voice=dict(
            headline="Solid ground for every flower.",
            sure="Rooted answer: {flower}, {pct} solid.",
            unsure="Not firm enough. Staff will check your photo.",
            tip="Step closer. One bloom, daylight, steady hands.",
            caveat="Wide garden shot? That is shaky ground. Photograph one blossom close up for firmer footing.",
        ),
    ),
    "storm": dict(
        label="Storm",  # the one mood with tension
        bg="#060713", surface="#12142B", text="#EEF1FF", muted="#9AA3CF",
        accent="#B27CFF", btn_fill="#4D8DFF", btn_label="#060713",
        fonts=google_fonts("Space Grotesk:wght@600", "Inter:wght@400;500;600"),
        font_head=GROTESK, font_body=SANS, head_weight="600",
        # clip-path cuts a notch out of the bottom right corner. It also cuts off outlines and shadows,
        # so the focus ring is drawn inside the box (ring offset below zero) and no shadows are used.
        r_btn="2px", r_card="2px", ring="-4px",
        clip_btn="polygon(0 0,100% 0,100% calc(100% - 9px),calc(100% - 9px) 100%,0 100%)",
        clip_card="polygon(0 0,100% 0,100% calc(100% - 16px),calc(100% - 16px) 100%,0 100%)",
        btn_extra="font-weight:600;", card_extra="border-top:2px solid var(--accent);",
        mark='<span class="bolt"></span>',
        # Short sparks: quiet most of the time, two flickers in a row. Two flashes in under a second, small area.
        keyframes="@keyframes spark{0%,86%,100%{opacity:.25}90%{opacity:1}93%{opacity:.4}96%{opacity:.9}}",
        ambient=".mark{animation:spark 8s linear $plays}",
        # clip-path also cuts the 1px border at the notch, so the pills (and the outline button) draw the diagonal themselves:
        # a 9px tile in the corner with one thin line along the cut.
        extra="$PILL:not([aria-checked=\"true\"]),[data-testid=\"stMain\"] [data-testid=\"stBaseButton-secondary\"]"
              "{background:linear-gradient(135deg,transparent calc(50% - 1.5px),var(--muted) calc(50% - 1.5px) 50%,transparent 50%)"
              " no-repeat right bottom/9px 9px}"
              ".mark{top:0}.bolt{display:block;width:1.3rem;height:2.1rem;background:var(--accent);"
              "clip-path:polygon(55% 0,8% 56%,44% 56%,32% 100%,92% 38%,56% 38%)}"
              '.stApp::before{content:"";position:fixed;z-index:-1;inset:0;pointer-events:none;'
              'background:radial-gradient(ellipse at 50% 0%,color-mix(in srgb,var(--accent) 14%,transparent),transparent 60%)}',
        voice=dict(
            headline="Weather report for your flower.",
            sure="Clear skies: a {flower}, {pct}.",
            unsure="Unsettled. Staff will check your photo.",
            tip="Close in on one bloom. Steady hands, good light.",
            caveat="Wide garden shot? Visibility is poor. Photograph one blossom close up for a surer answer.",
        ),
    ),
}
LABEL_TO_ID = {mood["label"]: key for key, mood in MOODS.items()}

# The colour variables that fade over 350 ms when the mood changes (registered with @property so CSS can animate them).
FADING = ("bg", "surface", "text", "muted", "accent", "btn", "btn-end", "btn-label", "p1", "p2", "p3", "p4")

CSS = Template("""
@import url("$fonts");
$properties
:root{--bg:$bg;--surface:$surface;--text:$text;--muted:$muted;--accent:$accent;--btn:$btn_fill;--btn-end:$btn_end;
  --btn-label:$btn_label;--p1:$p1;--p2:$p2;--p3:$p3;--p4:$p4;--edge:$edge;--line:$line;
  --r-btn:$r_btn;--r-card:$r_card;--clip-btn:$clip_btn;--clip-card:$clip_card;
  --font-head:$font_head;--font-body:$font_body;--head-weight:$head_weight;color-scheme:$scheme}
$keyframes
.stApp{background:$page;color:var(--text);font-family:var(--font-body);font-weight:$body_weight;
  text-transform:$case;isolation:isolate}
.stApp :is(p,li,label,small,button,div,input){font-family:var(--font-body)}
[data-testid="stAppViewContainer"],[data-testid="stMain"],[data-testid="stHeader"]{background:transparent}
[data-testid="stHeader"] :is(button,svg),[data-testid="stStatusWidget"] *{color:var(--text)}
[data-testid="stMainBlockContainer"]{padding-top:2.2rem}
@media (max-width:1000px){[data-testid="stMainBlockContainer"]{padding-top:4.4rem}}
.stApp [data-testid="stMarkdownContainer"] :is(p,li),.stApp [data-testid="stWidgetLabel"] :is(p,label){color:var(--text)}
.stApp [data-testid="stMarkdownContainer"] :is(.hint,.app-name,.chart-note){color:var(--muted)}
.stApp [data-testid="stMarkdownContainer"] .sub{color:var(--muted)}
.stApp [data-testid="stCaptionContainer"],.stApp [data-testid="stCaptionContainer"] p{color:var(--muted)}
.stApp :is(button,input,[tabindex]):focus-visible{outline:3px solid var(--text);outline-offset:$ring}

/* Header: app name + mood name as text, a decorative mark (aria-hidden, never clickable), the headline in the mood's voice */
.mood-head{position:relative;margin:0 0 .6rem}
.mark{position:absolute;right:0;top:0;pointer-events:none}
.app-name{display:flex;gap:.6rem;align-items:center;margin:0;font-size:.95rem}
.mood-tag{border:1px solid var(--muted);border-radius:999px;padding:0 .6rem;font-size:.8rem}
.stApp .headline{font-family:var(--font-head);font-weight:var(--head-weight);font-size:clamp(1.9rem,8.5vw,2.9rem);
  line-height:1.1;color:var(--text);margin:.5rem 2.6rem .2rem 0}
.hint{font-size:.9rem;margin:.1rem 0 .6rem}
.stApp [data-testid="stMarkdownContainer"] p.chart-note{font-size:.875rem;margin:-1.25rem 0 .4rem;opacity:1}

/* Widgets. Pills and buttons wear the mood's shape; solid ones wear its button fill. */
$BTN{border-radius:var(--r-btn);clip-path:var(--clip-btn)}
$PILL{min-height:2.75rem;padding:.2rem .8rem;background:transparent;border:1px solid var(--muted);box-shadow:none;color:var(--text)}
$PILL:hover{border-color:var(--btn);background:transparent}
$PILL_ON,$PILL_ON:hover{background:linear-gradient(135deg,var(--btn),var(--btn-end));border:1px solid var(--btn-end);color:var(--btn-label)}
$PILL_ON *{color:var(--btn-label)!important;font-weight:600}
$PILL,$PILL *,[data-testid="stWidgetLabel"] *{text-transform:inherit}
[data-testid="stMain"] button[data-variant="segmented_control"]{min-height:2.75rem;padding:.2rem 1rem;background:transparent;border:1px solid var(--muted);box-shadow:none;color:var(--text);text-transform:inherit}
[data-testid="stMain"] button[data-variant="segmented_control"][aria-checked="true"]{background:linear-gradient(135deg,var(--btn),var(--btn-end));border:1px solid var(--btn-end);color:var(--btn-label)}
[data-testid="stMain"] button[data-variant="segmented_control"][aria-checked="true"] *{color:var(--btn-label)!important;font-weight:600}
[data-testid="stMain"] button[data-variant="segmented_control"] *{text-transform:inherit}
$SOLID{background:linear-gradient(135deg,var(--btn),var(--btn-end));border:0;color:var(--btn-label);$btn_extra}
$SOLID *{color:var(--btn-label)!important}
[data-testid="stBaseButton-secondary"]{background:transparent;border:1px solid var(--btn);color:var(--text)}
[data-testid="stBaseButton-secondary"] *{color:var(--text)!important}
[data-testid="stFileUploaderDropzone"]{background:var(--surface);border:1px dashed var(--muted);border-radius:var(--r-card)}
[data-testid="stFileUploader"] *{color:var(--text)}
[data-testid="stFileUploader"] small,[data-testid="stFileUploader"] small *{color:var(--muted)}
[data-testid="stFileUploader"] [data-testid="stFileChip"]{background:transparent;border:1px solid var(--line);border-radius:var(--r-btn);clip-path:none}
[data-testid="stFileUploader"] [data-testid="stFileChip"] :is(div,svg){background:transparent;color:var(--text)}
[data-testid="stFileUploader"] [data-testid="stFileChip"] :is(small,button,small *,button *){color:var(--muted)}
[data-testid="stFileUploader"] [data-testid="stBaseButton-secondary"]{border-radius:var(--r-btn)}
[data-testid="stCameraInput"] :is(p,span,small,label){color:var(--text)}
[data-testid="stCameraInput"] [data-testid="stCameraInputWebcamStyledBox"]{background:var(--surface)}
[data-testid="stAlert"]{background:var(--surface);border:1px solid var(--muted);color:var(--text)}
[data-testid="stAlert"] *{color:var(--text)!important}
[data-testid="stImage"] img{border-radius:var(--r-card)}

/* Cards and notes: the result, the care guide, the tip */
.card,.note{background:var(--surface);color:var(--text);border-radius:var(--r-card);clip-path:var(--clip-card);
  padding:1rem 1.1rem;margin:.5rem 0}
.card{$card_extra}
.card.unsure{border-style:dashed}
.note{border-left:4px solid var(--btn)}
.card p,.note p{margin:0}
.card .sub{margin-top:.5rem}
.card ul{margin:.4rem 0 .2rem;padding-left:1.2rem}.card li{margin:.35rem 0;color:var(--text)}
.stApp .verdict{font-family:var(--font-head);font-weight:var(--head-weight);font-size:1.3rem;line-height:1.3;color:var(--text)}
.sub{font-size:.95rem}
.stApp .card .caveat{margin-top:.6rem;padding-top:.5rem;border-top:1px solid var(--line);color:var(--muted);font-size:.86rem;line-height:1.45;font-weight:400}
.accent{color:var(--accent);font-weight:600}
$extra

/* Motion lives only here, so people who ask for less motion get none of it. Decorative layers cannot be clicked. */
@media (prefers-reduced-motion:no-preference){
  :root{transition:$fade}
  @media (hover:hover){$hover}
  $ambient
}
""")


def build_css(mood_id, motion="loop"):
    """The page style for one mood.

    motion: "loop" (the mood plays its signature motion calmly, used when nothing is judged yet),
            "twice" (a very sure answer plays it two times, then rests), "off" (no ambient motion at all).
    """
    mood = {**DEFAULTS, **MOODS[mood_id]}
    stops = list(mood["stops"]) or [mood["bg"]]
    stops += [stops[-1]] * (4 - len(stops))
    plays = {"loop": "infinite", "twice": "2"}.get(motion)
    values = {
        **mood, "BTN": BTN, "SOLID": SOLID, "PILL": PILL, "PILL_ON": PILL_ON, "plays": plays,
        "btn_end": mood["btn_end"] or mood["btn_fill"],
        "p1": stops[0], "p2": stops[1], "p3": stops[2], "p4": stops[3],
        "properties": "".join(f"@property --{name}{{syntax:'<color>';inherits:true;initial-value:#000}}" for name in FADING),
        "fade": ",".join(f"--{name} .35s ease" for name in FADING),
        "page": "linear-gradient(180deg,var(--p1) 0%,var(--p2) 40%,var(--p3) 75%,var(--p4) 100%)",
    }
    if plays is None:
        values["ambient"] = ""  # motion off: the mood keeps its look but nothing animates by itself
    for key in ("btn_extra", "card_extra", "keyframes", "ambient", "hover", "extra"):
        values[key] = Template(values[key]).substitute(values)  # fragments may use $BTN, $SOLID, $plays
    css = re.sub(r"/\*.*?\*/", "", CSS.substitute(values), flags=re.S)
    # No blank lines: in Markdown a blank line would end the HTML block and print the rest of the style as text.
    return "<style>" + "".join(line.strip() for line in css.splitlines() if line.strip()) + "</style>"
