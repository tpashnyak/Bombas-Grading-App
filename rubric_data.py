"""Teacher-developed rubric aligned to the uploaded Bombas case handout and teaching note."""

ITEMS = [
    {
        "id": "R1", "section": "Reading", "label": "Business and products",
        "max": 10,
        "criterion": "Identifies Bombas and its premium socks; recognizes expanded apparel (underwear, T-shirts, slides).",
        "key": "Bombas produces premium socks and also underwear, T-shirts, and slides."
    },
    {
        "id": "R2", "section": "Reading", "label": "People and stakeholders",
        "max": 15,
        "criterion": "Names cofounders David Heath and Randy Goldberg and explains roles; identifies other relevant stakeholders.",
        "key": "David Heath and Randy Goldberg founded Bombas. Other stakeholders include paying customers, unhoused recipients of donated socks, and crowdfunding backers. Other defensible parties may earn credit."
    },
    {
        "id": "R3", "section": "Reading", "label": "Opportunity or challenge",
        "max": 10,
        "criterion": "Describes an evidence-based opportunity or challenge (e.g., product gap, pricing, funding, design).",
        "key": "Opportunity: few high-quality, comfortable everyday socks. Challenges: design comfortable socks, price to fund sold and donated pairs while earning profits, secure startup funds, identify target buyers. One well-supported opportunity OR challenge is enough for full credit."
    },
    {
        "id": "P1", "section": "Practice", "label": "Target paying customer",
        "max": 15,
        "criterion": "Describes buyers willing/able to pay $13-$20 and motivated by giving back; distinguishes customers from recipients.",
        "key": "Paying customer has disposable income and wants to support a give-back mission, willing to pay $13-$20 a pair. Initial focus millennials, later broad age appeal. Donated-sock recipients are consumers, not paying customers. Full credit need not mention age if other characteristics correct."
    },
    {
        "id": "P2", "section": "Practice", "label": "Market gap",
        "max": 15,
        "criterion": "Identifies demand for comfortable, high-quality everyday socks between cheap basics and sport-specific socks.",
        "key": "Market lacked high-quality, comfortable everyday socks: inexpensive basics existed, as did premium sport-specific performance socks."
    },
    {
        "id": "P3", "section": "Practice", "label": "Research and problem-solution fit",
        "max": 20,
        "criterion": "Connects market research, technical research, customer testing/iteration to a product meeting buyer needs.",
        "key": "Market research found an unmet need, assessed prices/customer target and gathered user feedback from free test pairs. Technical research involved trying premium socks, identifying useful design features, consulting fashion/manufacturing experts and iterating prototypes. Explain how these methods created a comfortable everyday sock that addressed the problem; do not require jargon beyond clear reasoning."
    },
    {
        "id": "A1", "section": "Application", "label": "Product improvement proposal",
        "max": 15,
        "criterion": "Names an everyday product, proposes one specific improvement, and explains a relevant user benefit.",
        "key": "Open-ended. Any appropriate everyday product and specific plausible improvement earn credit. Reward clear connection between change and consumer value. The teaching note does not dictate a single correct product."
    },
]
MAX_TOTAL = sum(i['max'] for i in ITEMS)
TITLE = 'Bombas | Case Analysis Rubric'
ASSIGNMENT = 'AP Business with Personal Finance | Topic 1.1: What Is a Business?'
SCORE_GUIDANCE = ('Use the points available for each response. Full credit = accurate and complete; '
                  'partial credit = some accurate evidence; zero = absent/off-topic. '
                  'Give reasonable credit for equivalent language and defensible answers.')
