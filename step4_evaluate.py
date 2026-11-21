import csv
import time
from step3_chat import answer, HANDOFF

# Each test: (question, list of words the answer MUST contain, or None if it should be handed off)
TESTS = [
    # ----- Questions the bot SHOULD answer -----
    ("can i bring my dog?", ["15 kg", "1,500"]),
    ("What are your office hours?", ["9:00", "6:00"]),
    ("How many rent cheques can I pay with?", ["3%"]),
    ("How much is the deposit if my rent is 90,000 AED, unfurnished?", ["4,500"]),
    ("Deposit for a furnished flat with 80,000 yearly rent?", ["8,000"]),
    ("What is your tenant fee on 60,000 AED rent?", ["3,000"]),
    ("What is your tenant fee on 20,000 AED rent?", ["2,000"]),
    ("How long until I get my deposit back?", ["14"]),
    ("How much notice do I need to end my lease early?", ["60"]),
    ("How fast do you fix a water leak?", ["4 hours"]),
    ("What is the maintenance hotline number?", ["800-555-0142"]),
    ("What is your fee when I buy a property?", ["2%"]),
    ("What down payment do I need for my first home under 5 million?", ["20%"]),
    ("How many banks do you work with for mortgages?", ["6"]),
    ("Do viewings cost anything?", ["free"]),
    ("What is the fee for full property management as a landlord?", ["8%"]),
    ("How quickly do you usually find a tenant?", ["21"]),
    ("Is there a fee for paying by card?", ["2%"]),
    ("What email do I use for complaints?", ["complaints@"]),
    ("How much is it to renew my contract?", ["500"]),
    ("How much to connect DEWA?", ["300"]),
    ("Can I do a video tour from abroad?", ["8:00 PM"]),
    ("What email is for customer support?", ["support@"]),
    ("How much more is rent on a 6 month contract?", ["10%"]),
    # ----- Questions the bot should HAND OFF (not in the FAQ) -----
    ("Do you sell cars?", None),
    ("What's the weather in Paris?", None),
    ("Do you accept Bitcoin?", None),
    ("Do you have properties in London?", None),
    ("Is the swimming pool open on Fridays?", None),
]


def normalize(text):
    """Make text comparable: no bold marks, plain dashes, no spaces of any kind."""
    text = text.replace("**", "").lower()
    for dash in ("\u2010", "\u2011", "\u2012", "\u2013", "\u2014"):
        text = text.replace(dash, "-")  # fancy dashes -> normal dash
    return "".join(text.split())  # removes normal and non-breaking spaces


def passed(reply, must_contain):
    clean = normalize(reply)
    if must_contain is None:  # should be a handoff
        return clean.startswith(normalize(HANDOFF)[:15])
    return all(normalize(word) in clean for word in must_contain)


rows, correct = [], 0
for i, (question, must) in enumerate(TESTS, 1):
    try:
        reply, dist = answer(question)
    except Exception:
        time.sleep(15)  # wait if the free API says "too many requests"
        reply, dist = answer(question)
    ok = passed(reply, must)
    correct += ok
    print(f"{i:>2}. {'PASS' if ok else 'FAIL'}  [{dist:.3f}]  {question}")
    if not ok:
        print(f"      Bot said: {reply[:150]}")
    rows.append([question, "PASS" if ok else "FAIL", round(dist, 3), reply])
    time.sleep(2.5)

score = correct / len(TESTS) * 100
print(f"\nScore: {correct}/{len(TESTS)} = {score:.0f}%")

with open("evaluation_results.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["question", "result", "distance", "bot_reply"])
    writer.writerows(rows)
print("Saved details to evaluation_results.csv")
