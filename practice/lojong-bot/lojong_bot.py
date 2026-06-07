"""
practice/lojong-bot/lojong_bot.py

Cycles through Atisha's 59 lojong slogans with commentary.
One slogan per day, rotationally. Commentary from multiple sources.
Optionally generates a contemporary application using Ollama.

Usage:
    python lojong_bot.py                    # today's slogan
    python lojong_bot.py --number 7         # specific slogan
    python lojong_bot.py --all              # list all slogans
    python lojong_bot.py --reflect          # LLM contemporary reflection
"""

import sys
import argparse
import hashlib
from datetime import date

sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent.parent))

SLOGANS = [
    # Point 1: Preliminaries
    (1,  "First, train in the preliminaries.",
         "Consider the preciousness of this human life. Reflect on death and impermanence. "
         "Reflect on karma. Reflect on the suffering of samsara. These four contemplations "
         "are the ground. Without them, the mind training has no traction."),

    # Point 2: The main practice — bodhicitta
    (2,  "Regard all dharmas as dreams.",
         "All phenomena — pleasant and unpleasant, arising and passing — are like dreams. "
         "Not nonexistent, but lacking the solidity we habitually project. This is the "
         "foundation of ultimate bodhicitta: things appear but lack inherent existence."),
    (3,  "Examine the nature of unborn awareness.",
         "The mind that observes — what is its nature? Look directly at the looker. "
         "This is the practice of recognizing rigpa or buddha-nature, the aspect of "
         "awareness that has never been born and never ceases."),
    (4,  "Self-liberate even the antidote.",
         "When you use emptiness as an antidote to clinging, do not cling to emptiness. "
         "Even the view must be released. This is the meaning of emptiness of emptiness."),
    (5,  "Rest in the nature of alaya, the essence.",
         "Let the mind rest in its natural state — open, aware, without fabrication. "
         "Not making anything happen. Not stopping anything from arising."),
    (6,  "In post-meditation, be a child of illusion.",
         "Between formal sessions, regard appearances as illusory. Not fake — illusory "
         "in the sense of appearing without inherent existence. Maintain the continuity "
         "of the view in daily activity."),

    # Point 2 continued — relative bodhicitta
    (7,  "Sending and taking should be practiced alternately. These two should ride the breath.",
         "Tonglen: on the in-breath, take in the suffering of beings. On the out-breath, "
         "send out happiness. This reverses the habitual pattern of taking pleasure and "
         "pushing away pain. Train first on yourself, then extend to others."),
    (8,  "Three objects, three poisons, three seeds of virtue.",
         "Friend, enemy, neutral — the three objects that trigger desire, aversion, and "
         "indifference. Instead of acting out these three poisons, use the arising to "
         "generate compassion. Each poison becomes a seed of virtue."),
    (9,  "In all activities, train with slogans.",
         "Use whatever arises as material for practice. Traffic, conflict, boredom, "
         "pleasure — each situation is an opportunity. Keep a slogan alive as a "
         "background orientation throughout the day."),
    (10, "Begin the sequence of sending and taking with yourself.",
         "Start tonglen with your own suffering before extending to others. "
         "This is not selfishness — you cannot genuinely take on others' suffering "
         "if you cannot face your own."),

    # Point 3: Transform adverse circumstances
    (11, "When the world is filled with evil, transform all mishaps into the path of bodhi.",
         "Everything that goes wrong is material for practice. Not toxic positivity — "
         "genuine alchemical transformation. The obstacle is the path."),
    (12, "Drive all blames into one.",
         "Blame self-grasping, not other people or circumstances. This does not mean "
         "self-punishment — it means seeing that the root of all difficulty is the "
         "habit of ego-clinging."),
    (13, "Be grateful to everyone.",
         "Enemies are precious teachers of patience. Difficult people reveal where "
         "your practice is weak. Everyone who challenges you is a benefactor."),
    (14, "Seeing confusion as the four kayas is unsurpassable shunyata protection.",
         "When disturbing emotions arise, recognize them as the display of buddha-nature. "
         "The arising itself is dharmakaya. The clarity is sambhogakaya. The expression "
         "is nirmanakaya. All three are inseparable — svabhavikakaya."),
    (15, "Four practices are the best of methods.",
         "Accumulating merit, purifying obscurations, offering to protectors/teachers, "
         "and requesting teachings. These four support all other practice."),
    (16, "Whatever you meet unexpectedly, join it with meditation.",
         "When something surprising happens — good or bad — bring it immediately "
         "into practice. Do not wait for a formal session."),

    # Point 4: Showing the utilization of practice in one's whole life
    (17, "Practice the five strengths, the condensed heart instructions.",
         "Strong determination, familiarization, positive seed, remorse, aspiration. "
         "These five are the essence of all lojong. At death, the most important "
         "practice is bodhicitta — this is what the five strengths point toward."),
    (18, "The Mahayana instruction for ejection of consciousness at death is the five strengths; how you conduct yourself is important.",
         "At death, apply the five strengths: strong intention, positive action, "
         "remorse for harm done, aspiration, and merging with the teacher. "
         "How you die reflects how you have practiced."),

    # Point 5: Evaluation of mind training
    (19, "All dharma agrees at one point.",
         "All Buddhist teachings converge on one thing: reducing self-centeredness. "
         "If your practice is not reducing ego-clinging, something is wrong — "
         "regardless of how sophisticated it seems."),
    (20, "Of the two witnesses, hold the principal one.",
         "Others witness your external behavior. You witness your actual state of mind. "
         "Your own honest self-assessment is the principal witness."),
    (21, "Always maintain only a joyful mind.",
         "Joy is not forced positivity. It is the quality of mind that is not weighed "
         "down by complaints, is genuinely pleased with small things, and does not "
         "require circumstances to be other than they are."),
    (22, "If you can practice even when distracted, you are well trained.",
         "The test is not how you practice on retreat. It is whether practice continues "
         "when you are tired, busy, in conflict, or overwhelmed."),

    # Point 6: The disciplines of mind training
    (23, "Always abide by the three basic principles.",
         "Do not violate your vows. Do not be ostentatious about your practice. "
         "Do not be partial — practice equally with all beings, not just those "
         "you find easy to love."),
    (24, "Change your attitude, but remain natural.",
         "The shift from self-centeredness to other-centeredness should happen internally. "
         "Externally, remain ordinary. Spiritual performance is counterproductive."),
    (25, "Don't talk about injured limbs.",
         "Do not mention others' defects — especially not under the guise of dharma "
         "discussion. This includes gossip about teachers and practitioners."),
    (26, "Don't ponder others.",
         "Don't speculate about others' motivations, faults, or karma. This is one "
         "of the most common ways practitioners waste practice energy."),
    (27, "Work with the greatest defilements first.",
         "Identify your strongest habitual pattern — the defilement that most "
         "controls you — and work there first. Don't only practice where it's easy."),
    (28, "Abandon any hope of fruition.",
         "Do not practice in order to achieve something. Practice itself is complete. "
         "Hoping for results is another form of grasping."),
    (29, "Abandon poisonous food.",
         "Virtuous actions motivated by ego-clinging are poisonous food — they look "
         "nutritious but increase self-grasping. Check the motivation."),
    (30, "Don't be so predictable.",
         "Don't hold grudges. Don't carry forward resentments from situation to "
         "situation. Each encounter is fresh."),
    (31, "Don't malign others.",
         "Don't speak disparagingly about others — especially not dharma practitioners, "
         "teachers, or traditions other than your own."),
    (32, "Don't wait in ambush.",
         "Don't wait for an opportunity to repay harm done to you. Patience means "
         "releasing the expectation of justice."),
    (33, "Don't bring things to a painful point.",
         "Don't say things calculated to wound. Even if true, some truths cause "
         "unnecessary harm."),
    (34, "Don't transfer the ox's load to the cow.",
         "Don't shift your responsibilities onto others. Don't avoid your own work "
         "by giving it to those less able to bear it."),
    (35, "Don't try to be the fastest.",
         "Don't compete. Don't try to win at generosity, realization, or anything else. "
         "Practice is not a competition."),
    (36, "Don't act with a twist.",
         "Don't do virtuous things with a hidden agenda. Don't give in order to "
         "receive. Don't be generous in order to be seen as generous."),
    (37, "Don't make gods into demons.",
         "Don't use dharma as a weapon — against yourself or others. Don't use "
         "spiritual practice to feel superior or to avoid ordinary responsibility."),
    (38, "Don't seek others' pain as the limbs of your own happiness.",
         "Don't benefit from others' misfortune. Don't be pleased when rivals fail. "
         "Others' suffering is not your opportunity."),

    # Point 7: Guidelines of mind training
    (39, "All activities should be done with one intention.",
         "Whatever you do, orient it toward bodhicitta. Eating, working, speaking — "
         "all with the intention of benefiting beings."),
    (40, "Correct all wrongs with one intention.",
         "When you make a mistake, apply bodhicitta immediately. Don't spiral into "
         "guilt. Acknowledge, apply the antidote, continue."),
    (41, "Two activities: one at the beginning, one at the end.",
         "In the morning: set the intention for the day. In the evening: review "
         "whether the intention was maintained. These two bookends sustain practice."),
    (42, "Whichever of the two occurs, be patient.",
         "Good fortune and bad fortune both require patience. Success can increase "
         "pride. Adversity can increase resentment. Both need the same antidote."),
    (43, "Observe these two, even at the risk of your life.",
         "Keep your root vows and your bodhicitta commitment. These two are "
         "the foundation everything else rests on."),
    (44, "Train in the three difficulties.",
         "It is difficult to recognize disturbing emotions. It is difficult to "
         "not act them out once recognized. It is difficult to break the "
         "habit completely. Work on all three."),
    (45, "Take on the three principal causes.",
         "Rely on a qualified teacher. Have favorable circumstances for practice. "
         "Develop the necessary merit and aspirations."),
    (46, "Pay heed that the three never wane.",
         "Devotion to the teacher. Enthusiasm for practice. Commitment to the precepts. "
         "These three must be consistently maintained, not just sparked occasionally."),
    (47, "Keep the three inseparable.",
         "Body, speech, and mind — keep them aligned in virtue at all times. "
         "Not just during formal practice."),
    (48, "Train without bias in all areas. It is crucial always to do this pervasively and wholeheartedly.",
         "Do not practice only with people you like or situations you find easy. "
         "Extend practice equally — universally. This is the meaning of 'all beings.'"),
    (49, "Always meditate on whatever provokes resentment.",
         "The person or situation that most activates your resentment is your "
         "most important practice partner. Don't avoid them."),
    (50, "Don't be swayed by external circumstances.",
         "Don't let your practice be determined by whether circumstances are "
         "favorable or unfavorable. Practice in all conditions."),
    (51, "This time, practice the main points.",
         "This human life is brief. Don't waste it on peripheral concerns. "
         "Practice the essence: bodhicitta and the recognition of mind's nature."),
    (52, "Don't misinterpret.",
         "Six misinterpretations: mistaken patience, mistaken longing, mistaken "
         "samayas, mistaken compassion, mistaken priorities, mistaken joy. "
         "Study what genuine patience, compassion, etc. actually require."),
    (53, "Don't vacillate.",
         "Commit to the practice. Don't oscillate between enthusiasm and abandonment. "
         "Consistency is more important than intensity."),
    (54, "Train wholeheartedly.",
         "Half-hearted practice produces half-hearted results. This does not mean "
         "forcing or straining — it means genuine engagement, without reservation."),
    (55, "Liberate yourself by examining and analyzing.",
         "Use your own intelligence. Don't accept teachings blindly. Examine whether "
         "the teaching applies to your actual experience."),
    (56, "Don't wallow in self-pity.",
         "When things go wrong, notice the tendency to feel sorry for yourself. "
         "Self-pity feeds ego-clinging rather than reducing it."),
    (57, "Don't be jealous.",
         "When others succeed or receive recognition, genuine joy — mudita — is "
         "the antidote. Practice sympathetic joy for others' good fortune."),
    (58, "Don't be frivolous.",
         "Don't make dharma into entertainment. Don't use spiritual conversation "
         "to show off. Practice seriously, without solemnity."),
    (59, "Don't expect applause.",
         "Don't practice for recognition, approval, or praise. The result of "
         "practice is the reduction of suffering — your own and others'. "
         "That is its own reward."),
]

REFLECT_PROMPT = """You are a lojong practitioner with years of experience.
Given today's slogan and its traditional commentary, write a brief contemporary
reflection (3-4 sentences) showing how this slogan applies to ordinary modern life —
work, relationships, technology, city living. Be specific. Avoid vague spirituality.

Slogan {number}: "{slogan}"

Traditional commentary: {commentary}

Contemporary reflection:"""


def get_slogan(number=None):
    if number is not None:
        idx = (number - 1) % len(SLOGANS)
    else:
        day_num = int(hashlib.md5(str(date.today()).encode()).hexdigest(), 16)
        idx = day_num % len(SLOGANS)
    return SLOGANS[idx]


def display_slogan(number=None, model=None):
    num, slogan, commentary = get_slogan(number)
    today = date.today().strftime("%A, %B %-d, %Y")

    print(f"\n  Lojong — {today}")
    print(f"  Slogan {num} of {len(SLOGANS)}")
    print()
    print(f'  "{slogan}"')
    print()
    print(f"  {commentary}")
    print()

    if model:
        try:
            import ollama
            response = ollama.chat(
                model=model,
                messages=[{
                    "role": "user",
                    "content": REFLECT_PROMPT.format(
                        number=num, slogan=slogan, commentary=commentary
                    )
                }],
                options={"temperature": 0.5}
            )
            print(f"  Contemporary reflection:")
            print(f"  {response['message']['content'].strip()}")
            print()
        except Exception as e:
            print(f"  (Reflection unavailable: {e})")


def list_all():
    print(f"\n  All {len(SLOGANS)} Lojong Slogans\n")
    point_labels = {
        1: "Point 1: Preliminaries",
        2: "Point 2: Main practice — bodhicitta",
        11: "Point 3: Transform adverse circumstances",
        17: "Point 4: Practice in one's whole life",
        19: "Point 5: Evaluation",
        23: "Point 6: Disciplines",
        39: "Point 7: Guidelines",
    }
    for num, slogan, _ in SLOGANS:
        if num in point_labels:
            print(f"\n  --- {point_labels[num]} ---")
        print(f"  {num:>2}. {slogan}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Daily lojong slogan with commentary"
    )
    parser.add_argument("--number", "-n", type=int,
                        help="Specific slogan number (1-59)")
    parser.add_argument("--all", action="store_true",
                        help="List all slogans")
    parser.add_argument("--reflect", action="store_true",
                        help="Generate contemporary reflection (needs Ollama)")
    parser.add_argument("--model", default="qwen2.5:7b")
    args = parser.parse_args()

    if args.all:
        list_all()
    else:
        model = args.model if args.reflect else None
        display_slogan(args.number, model=model)


if __name__ == "__main__":
    main()
