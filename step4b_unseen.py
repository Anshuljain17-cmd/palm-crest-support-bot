import time
from step3_chat import answer, HANDOFF

# 10 NEW questions, written in messy everyday wording and never used while building the bot.
# (question, words the answer must contain, or None if it should be handed off)
UNSEEN = [
    ("can my cat stay with me in the flat", ["15 kg"]),
    ("can i pay my rent in 12 cheques", ["not"]),
    ("i want to leave after 3 months, how much notice and any penalty", ["60"]),
    ("who pays if the AC breaks", ["landlord"]),
    ("buying a 6 million flat, what percent do i put down", ["35%"]),
    ("are u open on fridays", ["12:00"]),
    ("can i pay rent in cash", ["not"]),
    ("my landlord wants more rent, when will you tell me", ["90"]),
    # Should be handed off: not covered by the FAQ
    ("can you recommend a good school near Dubai Marina", None),
    ("what is the penalty if I pay my rent late", None),
]


def normalize(text):
    text = text.replace("**", "").lower()
    for dash in ("\u2010", "\u2011", "\u2012", "\u2013", "\u2014"):
        text = text.replace(dash, "-")
    return "".join(text.split())


def passed(reply, must_contain):
    clean = normalize(reply)
    if must_contain is None:
        return clean.startswith(normalize(HANDOFF)[:15])
    return all(normalize(w) in clean for w in must_contain)


correct = 0
for i, (question, must) in enumerate(UNSEEN, 1):
    try:
        reply, dist = answer(question)
    except Exception:
        time.sleep(15)
        reply, dist = answer(question)
    ok = passed(reply, must)
    correct += ok
    print(f"{i:>2}. {'PASS' if ok else 'CHECK'}  [{dist:.3f}]  {question}")
    print(f"      Bot said: {reply[:300]}\n")
    time.sleep(2.5)

print(f"Unseen score: {correct}/{len(UNSEEN)}")
print("Read each reply yourself: 'CHECK' may be a wording mismatch, not a bot error.")
