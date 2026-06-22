"""Local script generation engine.

The engine is deliberately dependency-free and produces useful structured drafts
without requiring a paid API key. It can later be swapped for an LLM provider
without changing the HTTP or database layers.
"""

import hashlib
import random
import re


LENGTH_CONFIG = {
    "Short": {"sections": 3, "detail": 1},
    "Medium": {"sections": 5, "detail": 2},
    "Long": {"sections": 7, "detail": 3},
}

SECTION_NAMES = [
    "The big picture",
    "What most people miss",
    "The practical framework",
    "A real-world example",
    "Common mistakes",
    "The smarter approach",
    "Your next move",
]

STYLE_VOICE = {
    "Educational": {
        "hook": "Here is a surprising truth about {topic}: understanding one simple framework can completely change the way you approach it.",
        "intro": "In this video, we are breaking down {topic} into clear, practical ideas you can use immediately. No jargon and no unnecessary detours—just the essential concepts, useful examples, and a simple path forward.",
        "transition": "Let us make that practical.",
    },
    "Storytelling": {
        "hook": "It started with a small decision about {topic}—the kind that seems harmless until everything changes.",
        "intro": "This is not just an explanation of {topic}. It is a story about the choices, turning points, and lessons hiding beneath the surface—and by the end, you may see the subject very differently.",
        "transition": "But that was only the beginning.",
    },
    "Documentary": {
        "hook": "Behind {topic} is a story far more complex—and more human—than it first appears.",
        "intro": "To understand {topic}, we need to look beyond the headlines. We will trace the forces that shaped it, examine the details that are often overlooked, and ask what its evolution means for us now.",
        "transition": "The evidence points to a deeper pattern.",
    },
    "Motivational": {
        "hook": "What if the only thing standing between you and progress with {topic} is the story you keep telling yourself?",
        "intro": "Today is about turning {topic} from something you think about into something you act on. You do not need perfect conditions. You need a clear first step, the courage to take it, and the discipline to keep moving.",
        "transition": "This is where momentum begins.",
    },
    "Listicle": {
        "hook": "These are the most important things to know about {topic}—and the final one could save you the most time.",
        "intro": "We have distilled {topic} into a focused list of ideas, mistakes, and practical moves. Each point builds on the last, so stay to the end for the complete playbook.",
        "transition": "Now, on to the next point.",
    },
    "Conversational": {
        "hook": "Can we be honest about {topic} for a minute? It is usually made way more complicated than it needs to be.",
        "intro": "So, let us talk about {topic} like two friends figuring it out together. We will separate what actually matters from the noise and leave you with a plan that feels realistic.",
        "transition": "Here is the part that gets interesting.",
    },
}


def _title_case_topic(topic: str) -> str:
    small_words = {"a", "an", "and", "as", "at", "for", "in", "of", "on", "the", "to"}
    words = topic.split()
    return " ".join(
        word.lower() if index and word.lower() in small_words else word.capitalize()
        for index, word in enumerate(words)
    )


def _sentence_topic(topic: str) -> str:
    return topic[0].lower() + topic[1:] if topic else topic


def _paragraphs(topic: str, section_index: int, detail: int, transition: str) -> list[str]:
    topic_lower = _sentence_topic(topic)
    building_blocks = [
        f"Start by defining what success with {topic_lower} actually looks like. A vague goal creates vague decisions, while a specific outcome gives every next step a purpose. Ask what should be different after a week, a month, or a year—and choose one signal that will show genuine progress.",
        f"The key idea is to treat {topic_lower} as a system, not a single trick. Inputs create patterns, patterns create results, and results give you feedback. When something does not work, change one input at a time so you can see what truly makes the difference.",
        f"Most beginners try to do too much at once. With {topic_lower}, consistency beats intensity because small repeatable actions survive busy days. Shrink the first step until it feels almost too easy, then repeat it before adding complexity.",
        f"Imagine two people starting with the same knowledge of {topic_lower}. One waits for confidence; the other runs a small experiment, reviews the outcome, and improves. After ten cycles, the second person has something far more valuable than confidence: evidence.",
        f"A common mistake is copying someone else's approach to {topic_lower} without understanding the context behind it. Borrow principles, not prescriptions. Your time, constraints, audience, and goals are different, so adapt the method before judging the result.",
        f"A better approach to {topic_lower} has three parts: choose one meaningful priority, build a repeatable process around it, and schedule a review. The review matters because it turns activity into learning and keeps effort pointed in the right direction.",
        f"Your next move is simple: pick one idea from this video and use it within the next twenty-four hours. Make the action visible, small, and measurable. Progress becomes much easier when the next step is clear enough to start now.",
    ]
    paragraphs = [building_blocks[section_index]]
    expansion = [
        f"Here is a useful test: if you cannot explain your approach to {topic_lower} in one sentence, it probably needs simplifying. Clarity makes it easier to notice distractions and say no to work that looks productive but does not move the outcome.",
        f"Keep a short record of what you tried, what happened, and what you will adjust. This creates a personal playbook for {topic_lower}; over time, your decisions stop depending on guesswork and start drawing from your own experience.",
    ]
    if detail >= 2:
        paragraphs.append(expansion[section_index % 2])
    if detail >= 3:
        paragraphs.append(
            f"{transition} Do not aim for a flawless plan. Aim for a feedback loop you trust: act, observe, refine, and repeat. That loop is how durable skill in {topic_lower} is built."
        )
    return paragraphs


def generate_script(topic: str, style: str, length: str) -> dict:
    """Create a repeatable but varied script from the selected creative controls."""
    seed = int(hashlib.sha256(f"{topic}|{style}|{length}".encode()).hexdigest()[:12], 16)
    randomizer = random.Random(seed)
    voice = STYLE_VOICE[style]
    config = LENGTH_CONFIG[length]
    display_topic = _title_case_topic(topic)

    hook = voice["hook"].format(topic=display_topic)
    introduction = voice["intro"].format(topic=display_topic)

    sections = []
    for index in range(config["sections"]):
        heading = SECTION_NAMES[index]
        if style == "Listicle":
            heading = f"{index + 1}. {heading}"
        # Keep sentence-case input in the spoken copy; title-case is reserved for
        # metadata where conventional YouTube capitalization is useful.
        paragraphs = _paragraphs(topic, index, config["detail"], voice["transition"])
        sections.append(f"{heading}\n\n" + "\n\n".join(paragraphs))
    main_content = "\n\n".join(sections)

    cta_options = [
        f"Now it is your turn: comment with the one step you will take on {display_topic} today. If this gave you a clearer path forward, like the video, subscribe, and share it with someone who needs that same spark.",
        f"Which part of {display_topic} should we unpack next? Tell me in the comments. Subscribe for more practical breakdowns, and send this video to the person you want beside you on the journey.",
        f"Do not let this become another video you simply watched. Choose one action, write it below, and start. Like and subscribe if you want more ideas you can actually put to work.",
    ]
    call_to_action = randomizer.choice(cta_options)

    titles = [
        f"{display_topic}: The Simple Guide Nobody Gave You",
        f"The Truth About {display_topic}",
        f"How to Master {display_topic} (Step by Step)",
        f"Stop Overthinking {display_topic}—Do This Instead",
        f"I Wish I Knew This About {display_topic} Sooner",
    ]
    thumbnail_ideas = [
        "START HERE",
        "THE TRUTH",
        "DO THIS NOW",
        "YOU'RE DOING IT WRONG",
        "THE SIMPLE WAY",
    ]

    full_script = (
        f"HOOK\n{hook}\n\n"
        f"INTRODUCTION\n{introduction}\n\n"
        f"MAIN CONTENT\n{main_content}\n\n"
        f"CALL TO ACTION\n{call_to_action}"
    )
    word_count = len(re.findall(r"\b[\w’'-]+\b", full_script))

    return {
        "topic": topic,
        "style": style,
        "length": length,
        "hook": hook,
        "introduction": introduction,
        "main_content": main_content,
        "call_to_action": call_to_action,
        "titles": titles,
        "thumbnail_ideas": thumbnail_ideas,
        "full_script": full_script,
        "word_count": word_count,
        "estimated_minutes": round(word_count / 145, 1),
    }
