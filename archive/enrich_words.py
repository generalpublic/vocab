"""
One-time script to enrich 25 high-value words with full context.
Run once: python enrich_words.py
"""
import json
from datetime import date

ENRICHED = [
    {
        "word": "Visceral",
        "pronunciation": "VIS-er-ul",
        "register": ["literary", "informal"],
        "tags": ["emotion", "body", "instinct"],
        "examples": [
            {"context": "essay", "sentence": "The photograph provoked a visceral reaction — not intellectual disagreement, but gut-level revulsion.", "why": "Visceral means a raw, bodily response that bypasses thought. The contrast with 'intellectual' makes the usage precise."},
            {"context": "social media", "sentence": "There's something visceral about live music that a recording can never capture.", "why": "The sensory, physical immediacy of live sound — felt in the chest, not analyzed. This is visceral's sweet spot."},
            {"context": "professional", "sentence": "The market's visceral response to the earnings miss wiped out three months of gains in a single session.", "why": "Markets reacting on panic/instinct rather than rational analysis. 'Visceral' signals irrational, gut-driven behavior."}
        ],
        "misuses": [
            {"wrong": "I had a visceral understanding of calculus after studying all night.", "problem": "'Visceral' is about raw feeling and bodily instinct, not comprehension or mastery. Understanding is intellectual, not visceral.", "use_instead": "intuitive, innate, deep"},
            {"wrong": "The visceral design of the website impressed the client.", "problem": "'Visceral' doesn't mean 'impressive' or 'well-crafted.' It means gut-level, primal.", "use_instead": "striking, compelling, polished"}
        ],
        "related": [
            {"word": "primal", "distinction": "'Primal' emphasizes ancient/evolutionary origins. 'Visceral' emphasizes the physical, bodily sensation."},
            {"word": "instinctive", "distinction": "'Instinctive' is broader — any automatic response. 'Visceral' specifically implies a felt, almost physical quality."}
        ],
        "triggers": ["Describing a reaction that bypasses thought — felt in the body before the mind processes it", "Contrasting emotional/gut response with rational analysis", "Conveying raw, unfiltered impact of an experience"]
    },
    {
        "word": "Ingress",
        "pronunciation": "IN-gress",
        "register": ["formal", "technical"],
        "tags": ["movement", "access", "architecture"],
        "examples": [
            {"context": "professional", "sentence": "We need to control ingress to the data center during the audit period.", "why": "Technical/security context where 'ingress' signals controlled, directional access — not just walking in."},
            {"context": "essay", "sentence": "The ingress of foreign capital reshaped the local housing market within a decade.", "why": "Abstract use: the flowing-in of something into a bounded space. Works because ingress implies directional movement into."},
            {"context": "professional", "sentence": "The network firewall rules restrict ingress traffic to ports 80 and 443.", "why": "Standard technical usage in networking — incoming traffic. This is where the word lives most naturally today."}
        ],
        "misuses": [
            {"wrong": "I made my ingress into the party fashionably late.", "problem": "Way too stiff for a social setting. 'Ingress' is technical/formal. Nobody says this at a party.", "use_instead": "entrance, arrival"},
            {"wrong": "The ingress of her argument was compelling.", "problem": "'Ingress' means physical or literal entry/flow-in, not the opening of an argument or idea.", "use_instead": "premise, opening, thrust"}
        ],
        "related": [
            {"word": "egress", "distinction": "Opposite: exit vs. entry. They're often paired in technical/architectural writing."},
            {"word": "entry", "distinction": "Neutral everyday equivalent. Use 'ingress' only when formality or directionality matters."},
            {"word": "access", "distinction": "'Access' is broader (can mean ability to reach). 'Ingress' specifically means the act of entering."}
        ],
        "triggers": ["Writing about controlled access to a space or system", "Technical/architectural contexts where 'entry' feels too casual", "Describing something flowing into a bounded area (capital, data, people)"]
    },
    {
        "word": "Petrichor",
        "pronunciation": "PET-ri-kor",
        "register": ["literary", "poetic"],
        "tags": ["nature", "sensory", "weather"],
        "examples": [
            {"context": "creative writing", "sentence": "The petrichor rising from the asphalt carried something ancestral — a promise encoded in the smell itself.", "why": "Evocative literary use. The word is inherently poetic, so lean into that with rich language."},
            {"context": "essay", "sentence": "There's a reason petrichor triggers nostalgia: the scent literally carries compounds from the earth's surface into the air after drought breaks.", "why": "Grounding the poetic word in science. Works in essays that bridge the sensory and the analytical."},
            {"context": "social media", "sentence": "Stepped outside after the first rain in weeks. That petrichor hit different.", "why": "Casual but correct. The word is specific enough that using it casually signals vocabulary without pretension."}
        ],
        "misuses": [
            {"wrong": "The petrichor of fresh coffee filled the kitchen.", "problem": "Petrichor refers ONLY to the smell of rain on dry earth. It's not a synonym for 'aroma' or 'scent.'", "use_instead": "aroma, fragrance, scent"},
            {"wrong": "I love the petrichor after a week of heavy rain.", "problem": "Petrichor specifically accompanies the FIRST rain after a DRY period. Continuous rain doesn't produce petrichor.", "use_instead": "the smell of rain, the wet earth smell"}
        ],
        "related": [
            {"word": "geosmin", "distinction": "The actual chemical compound that causes petrichor. More scientific."},
            {"word": "aroma", "distinction": "Generic pleasant smell. 'Petrichor' is hyper-specific: first rain on dry earth, nothing else."}
        ],
        "triggers": ["Describing the specific sensory experience of rain after drought", "Writing about nature, seasons, or weather with precision", "When you want a single word that carries an entire sensory memory"]
    },
    {
        "word": "Cogent",
        "pronunciation": "KOH-jent",
        "register": ["formal", "academic"],
        "tags": ["argument", "logic", "persuasion"],
        "examples": [
            {"context": "professional", "sentence": "She made a cogent case for restructuring the team, backing every claim with data.", "why": "Cogent means clear + convincing + well-reasoned. The 'backing with data' reinforces that this isn't just persuasive — it's logically tight."},
            {"context": "essay", "sentence": "The most cogent criticism of social media isn't that it wastes time — it's that it fragments attention in ways we can't perceive.", "why": "Using 'cogent' to elevate one argument above others. It signals 'this one actually holds together logically.'"},
            {"context": "social media", "sentence": "Haven't heard a cogent argument against this yet. Just vibes.", "why": "Casual but precise. The contrast with 'vibes' sharpens what cogent means: structured, evidence-based, logical."}
        ],
        "misuses": [
            {"wrong": "The sunset was cogent and beautiful.", "problem": "'Cogent' applies to arguments, reasoning, and communication — not to physical beauty or scenery.", "use_instead": "striking, vivid, breathtaking"},
            {"wrong": "He spoke in a very cogent voice.", "problem": "'Cogent' describes the quality of reasoning, not the quality of someone's voice or tone.", "use_instead": "clear, authoritative, measured"}
        ],
        "related": [
            {"word": "compelling", "distinction": "'Compelling' means you feel pulled toward something — it can be emotional. 'Cogent' is specifically about logical clarity."},
            {"word": "persuasive", "distinction": "'Persuasive' is broader — you can persuade through emotion, charm, or pressure. 'Cogent' persuades through reason."},
            {"word": "pithy", "distinction": "'Pithy' means brief and meaningful. 'Cogent' means clear and logically convincing. A pithy remark can be cogent, but they're not synonyms."}
        ],
        "triggers": ["Praising an argument for its logical structure, not just its emotional pull", "Distinguishing between 'convincing because it feels right' and 'convincing because it's logically airtight'", "Writing about discourse, debate, or critical analysis"]
    },
    {
        "word": "Tenuous",
        "pronunciation": "TEN-yoo-us",
        "register": ["formal", "general"],
        "tags": ["weakness", "fragility", "connection"],
        "examples": [
            {"context": "essay", "sentence": "The connection between social media use and depression is real but tenuous — correlation, not causation, with a dozen confounding variables.", "why": "Tenuous means the connection exists but is thin, fragile, and could snap under scrutiny. Perfect for qualified claims."},
            {"context": "professional", "sentence": "Our competitive advantage in that market is tenuous at best — one regulatory change could wipe it out.", "why": "Communicates fragility without saying 'weak.' Tenuous implies it exists but barely holds."},
            {"context": "creative writing", "sentence": "He clung to a tenuous hope that she'd call, the kind of hope that feeds on its own silence.", "why": "Emotional register: a hope so thin it's almost imaginary, but still present. The word carries both existence and fragility."}
        ],
        "misuses": [
            {"wrong": "The tenuous steak was hard to chew.", "problem": "'Tenuous' means thin/fragile in an abstract sense. It doesn't describe physical thinness of objects or food.", "use_instead": "tough, chewy, overcooked"},
            {"wrong": "She gave a tenuous answer to the math problem.", "problem": "'Tenuous' doesn't mean 'tentative' or 'uncertain.' It means the thing itself is thin/weak, not that the person is unsure.", "use_instead": "tentative, hesitant, uncertain"}
        ],
        "related": [
            {"word": "fragile", "distinction": "'Fragile' means easily broken. 'Tenuous' means thin and barely holding — it emphasizes how little substance there is."},
            {"word": "tentative", "distinction": "'Tentative' describes a person's uncertainty. 'Tenuous' describes the thing itself being thin or weak."}
        ],
        "triggers": ["Describing a connection, argument, or claim that exists but barely holds together", "Qualifying a relationship or link without dismissing it entirely", "Conveying fragility of an abstract thing — a hope, a lead, a theory"]
    },
    {
        "word": "Evanescent",
        "pronunciation": "ev-uh-NES-ent",
        "register": ["literary", "formal"],
        "tags": ["time", "impermanence", "beauty"],
        "examples": [
            {"context": "essay", "sentence": "Youth is evanescent — not just short, but actively vanishing, even as you try to hold onto it.", "why": "The word captures not just brevity but the process of fading. It's disappearing as you watch."},
            {"context": "creative writing", "sentence": "The light was evanescent, lasting only the few seconds between the clouds parting and the sun dropping below the ridge.", "why": "Evanescent is perfect for moments that are beautiful precisely because they're disappearing."},
            {"context": "social media", "sentence": "Social media fame is evanescent. Today's viral moment is tomorrow's forgotten post.", "why": "Modern context: internet attention as something that dissolves almost instantly."}
        ],
        "misuses": [
            {"wrong": "The evanescent building had stood for centuries.", "problem": "'Evanescent' means quickly fading or vanishing. A centuries-old building is the opposite of evanescent.", "use_instead": "enduring, ancient, timeworn"},
            {"wrong": "She had an evanescent personality — always quiet and reserved.", "problem": "'Evanescent' doesn't mean shy or faint. It means actively disappearing or fleeting.", "use_instead": "reserved, subdued, unassuming"}
        ],
        "related": [
            {"word": "ephemeral", "distinction": "'Ephemeral' means short-lived. 'Evanescent' adds the visual quality of fading out, like mist dissolving."},
            {"word": "fleeting", "distinction": "'Fleeting' is the everyday equivalent. 'Evanescent' is more literary and implies a graceful vanishing."},
            {"word": "transient", "distinction": "'Transient' is neutral — just passing through. 'Evanescent' carries poetic weight and implies beauty in the fading."}
        ],
        "triggers": ["Describing something beautiful that's actively disappearing", "When 'fleeting' is too plain and you want the image of something dissolving", "Writing about impermanence with a poetic register"]
    },
    {
        "word": "Obsequious",
        "pronunciation": "ob-SEE-kwee-us",
        "register": ["formal", "literary"],
        "tags": ["behavior", "power", "servility"],
        "examples": [
            {"context": "essay", "sentence": "The obsequious aide laughed too hard at every joke, agreed with every opinion, and anticipated every need — all while despising the man he served.", "why": "Obsequious captures performative servility — it's not genuine respect, it's calculated submission."},
            {"context": "professional", "sentence": "There's a difference between being collaborative and being obsequious. The first earns respect; the second erodes it.", "why": "Drawing a line between healthy teamwork and sycophantic behavior. The word carries judgment."},
            {"context": "social media", "sentence": "The way some people reply to celebrity tweets is genuinely obsequious. It's not admiration — it's worship performance.", "why": "Modern parasocial context. Obsequious fan behavior as servile flattery aimed at someone who won't notice."}
        ],
        "misuses": [
            {"wrong": "The obsequious teacher was very helpful and kind.", "problem": "'Obsequious' is always negative — it implies excessive, insincere servility. A genuinely helpful person isn't obsequious.", "use_instead": "attentive, generous, accommodating"},
            {"wrong": "She was obsequious in her obedience to the law.", "problem": "'Obsequious' applies to interpersonal dynamics — fawning over a person. Following the law isn't obsequious.", "use_instead": "scrupulous, meticulous, dutiful"}
        ],
        "related": [
            {"word": "sycophant", "distinction": "A sycophant is the person. Obsequious describes the behavior."},
            {"word": "fawning", "distinction": "'Fawning' is simpler and more visceral. 'Obsequious' is more formal and implies a calculated, servile pattern."},
            {"word": "servile", "distinction": "'Servile' means slavishly submissive. 'Obsequious' adds the eagerness to please — it's not just submission, it's active flattery."}
        ],
        "triggers": ["Describing someone who flatters those in power for personal gain", "Writing about power dynamics where one person debases themselves before another", "Critiquing performative deference vs. genuine respect"]
    },
    {
        "word": "Pernicious",
        "pronunciation": "per-NISH-us",
        "register": ["formal", "academic"],
        "tags": ["harm", "danger", "hidden"],
        "examples": [
            {"context": "essay", "sentence": "The most pernicious myths are the ones that contain just enough truth to survive scrutiny.", "why": "Pernicious means harmful in a way that's gradual, subtle, and hard to detect. The 'just enough truth' captures that insidious quality."},
            {"context": "professional", "sentence": "Quiet quitting sounds harmless, but the pernicious effect on team morale only becomes visible months later.", "why": "Delayed, hidden harm — you don't see it coming. That's what separates pernicious from simply 'bad.'"},
            {"context": "social media", "sentence": "The pernicious thing about comparison culture isn't the envy — it's the slow erosion of self-worth you don't even notice happening.", "why": "Gradual, invisible damage. Pernicious is the right word when the harm sneaks up."}
        ],
        "misuses": [
            {"wrong": "The pernicious thunderstorm knocked out power across the city.", "problem": "'Pernicious' implies subtle, gradual, hidden harm. A thunderstorm is sudden and obvious — the opposite of pernicious.", "use_instead": "devastating, destructive, severe"},
            {"wrong": "The pernicious puppy chewed up my shoes again.", "problem": "'Pernicious' carries moral weight — insidious, gradually ruinous harm. A mischievous puppy isn't pernicious.", "use_instead": "mischievous, destructive, unruly"}
        ],
        "related": [
            {"word": "insidious", "distinction": "'Insidious' emphasizes the treachery/deception. 'Pernicious' emphasizes the harm itself — gradual, ruinous, and often irreversible."},
            {"word": "toxic", "distinction": "'Toxic' is broader and more casual. 'Pernicious' is more precise: the harm is specifically subtle, gradual, and hard to detect."},
            {"word": "nefarious", "distinction": "'Nefarious' means obviously evil/wicked. 'Pernicious' is worse because you don't see it coming."}
        ],
        "triggers": ["Describing harm that's gradual, subtle, and hard to detect until it's too late", "Writing about ideas, beliefs, or systems that damage slowly from within", "When 'harmful' is too weak and 'devastating' is too sudden"]
    },
    {
        "word": "Capricious",
        "pronunciation": "kuh-PRISH-us",
        "register": ["formal", "literary"],
        "tags": ["behavior", "unpredictability", "change"],
        "examples": [
            {"context": "essay", "sentence": "Social media algorithms are capricious masters — what they reward today, they bury tomorrow, with no explanation.", "why": "Capricious implies whimsical, unpredictable changes driven by no discernible logic. Perfect for opaque systems."},
            {"context": "professional", "sentence": "Working for a capricious leader is exhausting because you can never predict which version of them will show up.", "why": "Captures the specific frustration of unpredictability in authority — not just inconsistency, but seemingly random shifts."},
            {"context": "creative writing", "sentence": "Spring in the mountains is capricious: sun at noon, snow by three, and a sky that changes its mind more than the wind.", "why": "Personification of weather. Capricious works because it implies whimsy and mood, not just randomness."}
        ],
        "misuses": [
            {"wrong": "She was capricious in her dedication to the project — she worked on it every single day.", "problem": "'Capricious' means unpredictable and changeable. Consistent daily dedication is the opposite.", "use_instead": "steadfast, dedicated, resolute"},
            {"wrong": "The capricious disaster struck without warning.", "problem": "'Capricious' implies whimsy and lightness in its unpredictability — almost playful. Disasters aren't whimsical.", "use_instead": "sudden, unexpected, unforeseen"}
        ],
        "related": [
            {"word": "mercurial", "distinction": "'Mercurial' emphasizes rapid emotional changes in a person. 'Capricious' is broader — applies to systems, weather, fate."},
            {"word": "erratic", "distinction": "'Erratic' is more clinical — irregular pattern. 'Capricious' adds the suggestion of whimsy or willfulness."},
            {"word": "fickle", "distinction": "'Fickle' usually applies to loyalty or affection. 'Capricious' applies to behavior and decisions more broadly."}
        ],
        "triggers": ["Describing unpredictable behavior that seems driven by whim rather than reason", "Writing about systems, people, or forces that change without warning or logic", "When 'unpredictable' is too neutral and you want to convey the frustration of randomness"]
    },
    {
        "word": "Felicitous",
        "pronunciation": "feh-LIS-ih-tus",
        "register": ["formal", "literary"],
        "tags": ["language", "aptness", "expression"],
        "examples": [
            {"context": "essay", "sentence": "It was a felicitous choice of words — not just accurate, but perfectly suited to the moment.", "why": "Felicitous means apt, well-chosen, hitting the right note. It's about fitness for the occasion, not just correctness."},
            {"context": "professional", "sentence": "The rebrand was felicitous: it captured the company's pivot without alienating existing customers.", "why": "Something that landed perfectly — not by luck, but by appropriateness to the context."},
            {"context": "essay", "sentence": "Shakespeare's most felicitous metaphors are the ones you don't notice — they feel so natural that you forget they're figurative.", "why": "Praising artistry that works precisely because it doesn't call attention to itself."}
        ],
        "misuses": [
            {"wrong": "I had a felicitous day at the beach.", "problem": "'Felicitous' doesn't mean 'happy' or 'pleasant.' It means well-suited, apt, appropriate. A day can't be felicitous.", "use_instead": "delightful, wonderful, pleasant"},
            {"wrong": "The felicitous accident led to a new discovery.", "problem": "A lucky accident is 'fortuitous' or 'serendipitous.' 'Felicitous' implies deliberate aptness, not chance.", "use_instead": "fortuitous, serendipitous, fortunate"}
        ],
        "related": [
            {"word": "apt", "distinction": "'Apt' is the everyday equivalent. 'Felicitous' is more formal and implies a higher degree of elegance in the fitness."},
            {"word": "fortuitous", "distinction": "'Fortuitous' means lucky by chance. 'Felicitous' means well-chosen or well-suited — implying intentionality."},
            {"word": "propitious", "distinction": "'Propitious' means favorable conditions. 'Felicitous' means a well-suited expression or choice."}
        ],
        "triggers": ["Praising someone's word choice, timing, or artistic decision", "Describing something that fits its context perfectly — not just good, but right", "Writing about language, rhetoric, or communication"]
    },
    {
        "word": "Sanguine",
        "pronunciation": "SANG-gwin",
        "register": ["formal", "literary"],
        "tags": ["outlook", "emotion", "optimism"],
        "examples": [
            {"context": "professional", "sentence": "Investors remain sanguine despite the volatility — they've seen this pattern before and expect recovery.", "why": "Sanguine means optimistic specifically in the face of difficulty. It's not naive cheerfulness — it's confidence under pressure."},
            {"context": "essay", "sentence": "I'm not sanguine about AI regulation. The technology moves faster than any legislature can.", "why": "Using 'not sanguine' is powerful — it signals measured pessimism, not panic. The word carries weight even in negation."},
            {"context": "social media", "sentence": "Everyone's either panicking or pretending everything's fine. Where are the sanguine realists?", "why": "Positions sanguine as a middle ground — hopeful but grounded. Not denial, not despair."}
        ],
        "misuses": [
            {"wrong": "The sanguine sunset painted the sky red.", "problem": "'Sanguine' as an adjective for color (blood-red) is archaic. In modern usage, it means optimistic. Readers will be confused.", "use_instead": "crimson, blood-red, scarlet"},
            {"wrong": "She was sanguine about the party, excited for the music and food.", "problem": "'Sanguine' implies optimism despite adversity. Excitement about a party isn't sanguine — there's no difficulty to be optimistic through.", "use_instead": "enthusiastic, excited, eager"}
        ],
        "related": [
            {"word": "optimistic", "distinction": "'Optimistic' is neutral. 'Sanguine' implies confidence specifically in the face of challenges or uncertainty."},
            {"word": "buoyant", "distinction": "'Buoyant' suggests lightness and resilience. 'Sanguine' is more grounded — steady confidence, not bubbly energy."},
            {"word": "hopeful", "distinction": "'Hopeful' can be passive. 'Sanguine' implies active, reasoned confidence — you've assessed the situation and still believe it'll work out."}
        ],
        "triggers": ["Describing optimism that persists despite difficulty or uncertainty", "Writing about confidence in challenging circumstances", "When 'optimistic' is too flat and you want to signal resilience"]
    },
    {
        "word": "Eschew",
        "pronunciation": "es-CHOO",
        "register": ["formal"],
        "tags": ["avoidance", "choice", "deliberation"],
        "examples": [
            {"context": "essay", "sentence": "He eschewed social media entirely — not out of ignorance, but out of a deliberate commitment to presence.", "why": "Eschew implies intentional, principled avoidance. It's not that he couldn't use it — he chose not to."},
            {"context": "professional", "sentence": "The company eschews traditional advertising in favor of word-of-mouth and community building.", "why": "Strategic avoidance as a philosophy, not just a budget decision."},
            {"context": "social media", "sentence": "I eschew productivity culture. Not everything needs to be optimized.", "why": "Using a formal word in a casual context for emphasis. The formality of 'eschew' makes the rejection feel more deliberate."}
        ],
        "misuses": [
            {"wrong": "I eschewed the ball but it still hit me.", "problem": "'Eschew' means to deliberately avoid as a practice or principle. It's not a physical dodge.", "use_instead": "dodged, ducked, avoided"},
            {"wrong": "She eschewed the test because she didn't study.", "problem": "'Eschew' implies principled avoidance, not skipping something out of unpreparedness.", "use_instead": "skipped, avoided, missed"}
        ],
        "related": [
            {"word": "avoid", "distinction": "'Avoid' is neutral. 'Eschew' implies a deliberate, often principled decision to stay away."},
            {"word": "abstain", "distinction": "'Abstain' often implies restraint from something tempting. 'Eschew' implies rejecting something you don't even want."},
            {"word": "shun", "distinction": "'Shun' is social — you shun a person. 'Eschew' is philosophical — you eschew a practice or thing."}
        ],
        "triggers": ["Describing deliberate, principled avoidance of something", "Writing about lifestyle or philosophical choices", "When 'avoid' is too casual and you want to signal intentionality"]
    },
    {
        "word": "Germane",
        "pronunciation": "jer-MAYN",
        "register": ["formal", "academic"],
        "tags": ["relevance", "connection", "argument"],
        "examples": [
            {"context": "professional", "sentence": "That's an interesting point, but I'm not sure it's germane to the decision we need to make today.", "why": "Polite way to redirect — 'germane' signals 'relevant to THIS specific discussion,' not broadly relevant."},
            {"context": "essay", "sentence": "What makes the study germane isn't its sample size — it's that it finally isolates the variable everyone else was confounding.", "why": "Germane means relevant in a way that matters. The study isn't just related — it's directly applicable."},
            {"context": "social media", "sentence": "A lot of discourse would improve if people asked one question before posting: 'Is this germane?'", "why": "Using germane to call out off-topic commentary. The word itself signals intellectual rigor."}
        ],
        "misuses": [
            {"wrong": "The germane flowers bloomed beautifully in the garden.", "problem": "You might be thinking of 'geranium.' 'Germane' means relevant or pertinent — it has nothing to do with plants.", "use_instead": "beautiful, vibrant, colorful"},
            {"wrong": "His germane attitude made everyone feel welcome.", "problem": "'Germane' means relevant to a topic, not warm or welcoming.", "use_instead": "genial, affable, welcoming"}
        ],
        "related": [
            {"word": "relevant", "distinction": "'Relevant' is the everyday equivalent. 'Germane' is more precise — closely and significantly related, not just tangentially connected."},
            {"word": "pertinent", "distinction": "Nearly synonymous. 'Pertinent' is slightly more common. 'Germane' carries a slightly more formal, academic tone."},
            {"word": "apropos", "distinction": "'Apropos' means 'with regard to' or 'relevant.' 'Germane' is strictly about relevance to the matter at hand."}
        ],
        "triggers": ["Assessing whether something is relevant to the specific discussion", "Redirecting a conversation back to what matters", "Writing about discourse, debate, or analytical rigor"]
    },
    {
        "word": "Fraught",
        "pronunciation": "FRAWT",
        "register": ["formal", "general"],
        "tags": ["tension", "danger", "difficulty"],
        "examples": [
            {"context": "essay", "sentence": "The relationship between technology and privacy is fraught — every convenience comes with a surveillance cost.", "why": "Fraught (used alone, without 'with') means filled with tension, anxiety, or difficulty. This is the modern dominant usage."},
            {"context": "professional", "sentence": "Mergers are always fraught. Even when the numbers work, the culture clash can kill the deal.", "why": "Fraught as a standalone adjective meaning tense and risky. Clean, punchy usage."},
            {"context": "essay", "sentence": "The decision to leave was fraught with guilt, relief, and the terrifying freedom of having no plan.", "why": "'Fraught with' + specific things it's filled with. Classic construction."}
        ],
        "misuses": [
            {"wrong": "The fraught student studied hard for the exam.", "problem": "'Fraught' describes situations, relationships, or decisions — not people. A person can be anxious, but they can't be fraught.", "use_instead": "anxious, stressed, worried"},
            {"wrong": "The fraught meal was delicious.", "problem": "'Fraught' implies tension and difficulty. A delicious meal isn't fraught unless the dinner conversation was hostile.", "use_instead": "elaborate, sumptuous, exquisite"}
        ],
        "related": [
            {"word": "tense", "distinction": "'Tense' is simpler and more direct. 'Fraught' implies a deeper, more complex difficulty — loaded with multiple risks or emotions."},
            {"word": "laden", "distinction": "'Laden' means heavily loaded (often physically). 'Fraught' means loaded with tension, danger, or emotional weight."}
        ],
        "triggers": ["Describing a situation, decision, or relationship loaded with tension or risk", "When 'tense' or 'difficult' is too simple for the layered complexity you want to convey", "Writing about trade-offs, dilemmas, or anything with hidden costs"]
    },
    {
        "word": "Latent",
        "pronunciation": "LAY-tent",
        "register": ["formal", "academic", "general"],
        "tags": ["hidden", "potential", "dormancy"],
        "examples": [
            {"context": "essay", "sentence": "Everyone has latent abilities that never surface because no situation ever demands them.", "why": "Latent means present but not yet visible or active. The abilities exist — they just haven't been triggered."},
            {"context": "professional", "sentence": "The latent demand for remote work existed for years before the pandemic made it undeniable.", "why": "The demand was always there, hidden beneath surface behavior. The crisis didn't create it — it revealed it."},
            {"context": "social media", "sentence": "Trauma doesn't disappear. It goes latent. And latent isn't the same as gone.", "why": "Powerful distinction: latent means still present, just not active. The word corrects the assumption that invisible = resolved."}
        ],
        "misuses": [
            {"wrong": "His latent anger was obvious to everyone in the room.", "problem": "If it's obvious, it's not latent. Latent means hidden, not yet manifest.", "use_instead": "palpable, visible, overt, apparent"},
            {"wrong": "The latent painting hung on the wall for years.", "problem": "'Latent' means hidden potential, not physically present but unnoticed. A painting on a wall is just... there.", "use_instead": "overlooked, unnoticed, neglected"}
        ],
        "related": [
            {"word": "dormant", "distinction": "'Dormant' implies something that was once active and is now sleeping. 'Latent' implies something that has never yet been active."},
            {"word": "potential", "distinction": "'Potential' is the everyday equivalent but lacks the scientific precision. 'Latent' implies something that EXISTS but hasn't manifested."},
            {"word": "nascent", "distinction": "'Nascent' means just beginning to exist or develop. 'Latent' means existing but not yet emerged at all."}
        ],
        "triggers": ["Describing something that exists but hasn't yet surfaced or been activated", "Writing about hidden potential, suppressed forces, or unacknowledged realities", "Distinguishing between 'absent' and 'present but invisible'"]
    },
    {
        "word": "Specious",
        "pronunciation": "SPEE-shus",
        "register": ["formal", "academic"],
        "tags": ["deception", "argument", "logic"],
        "examples": [
            {"context": "essay", "sentence": "The argument that correlation equals causation is specious — it looks logical on the surface but collapses under scrutiny.", "why": "Specious means superficially plausible but actually wrong. It's the word for arguments that fool you at first glance."},
            {"context": "professional", "sentence": "The vendor's ROI projections were specious: impressive numbers built on assumptions that wouldn't survive a single quarter.", "why": "Looks convincing in a slide deck, falls apart in reality. That gap between appearance and substance is specious territory."},
            {"context": "social media", "sentence": "Most 'common sense' arguments are specious. They feel true because they're simple, not because they're right.", "why": "Challenges the authority of simplicity. Specious captures the dangerous gap between 'sounds right' and 'is right.'"}
        ],
        "misuses": [
            {"wrong": "The specious sunset was the most beautiful I'd ever seen.", "problem": "'Specious' doesn't mean special, spectacular, or beautiful. It means deceptively attractive but actually false.", "use_instead": "spectacular, stunning, magnificent"},
            {"wrong": "Her specious knowledge of history impressed the professor.", "problem": "If her knowledge genuinely impressed, it's not specious. Specious means superficially impressive but actually flawed.", "use_instead": "impressive, extensive, deep"}
        ],
        "related": [
            {"word": "spurious", "distinction": "'Spurious' means outright false or fake. 'Specious' is trickier — it LOOKS true but isn't. The deception is the key difference."},
            {"word": "fallacious", "distinction": "'Fallacious' is a logical term — the reasoning is flawed. 'Specious' adds the layer of surface plausibility."},
            {"word": "plausible", "distinction": "'Plausible' is neutral — it might be true. 'Specious' means it looks plausible but is specifically wrong."}
        ],
        "triggers": ["Calling out an argument that sounds convincing but is actually wrong", "Writing about rhetoric, misinformation, or deceptive logic", "When you want to say 'this looks right but isn't' in one word"]
    },
    {
        "word": "Pithy",
        "pronunciation": "PITH-ee",
        "register": ["general", "literary"],
        "tags": ["language", "brevity", "expression"],
        "examples": [
            {"context": "essay", "sentence": "The best Twitter accounts prove that pithy doesn't mean shallow — you can compress genuine insight into 280 characters.", "why": "Pithy means brief but full of substance and meaning. This example defends brevity against the charge of superficiality."},
            {"context": "professional", "sentence": "Skip the preamble. Give me the pithy version — what do we need to do and why?", "why": "Requesting communication that's compressed but complete. Pithy as a quality of effective leadership communication."},
            {"context": "social media", "sentence": "Oscar Wilde was the king of pithy one-liners. Every sentence a grenade.", "why": "Pithy captures Wilde's gift: maximum impact in minimum words."}
        ],
        "misuses": [
            {"wrong": "The pithy novel was 800 pages long.", "problem": "'Pithy' means brief and forceful. An 800-page novel is the opposite of pithy by definition.", "use_instead": "dense, rich, expansive, comprehensive"},
            {"wrong": "His pithy appearance made him look handsome.", "problem": "'Pithy' describes expression and language, not physical appearance.", "use_instead": "striking, sharp, polished"}
        ],
        "related": [
            {"word": "terse", "distinction": "'Terse' means brief but can imply curtness or coldness. 'Pithy' means brief AND meaningful — it's a compliment."},
            {"word": "concise", "distinction": "'Concise' means using few words. 'Pithy' means using few words AND packing them with substance and force."},
            {"word": "laconic", "distinction": "'Laconic' means using very few words, sometimes to the point of seeming unfriendly. 'Pithy' is always positive — dense with meaning."}
        ],
        "triggers": ["Praising communication that's both brief and substantive", "Writing about effective expression, rhetoric, or writing craft", "When you want to say 'short but powerful' in one word"]
    },
    {
        "word": "Nascent",
        "pronunciation": "NAY-sent",
        "register": ["formal", "academic"],
        "tags": ["beginning", "emergence", "potential"],
        "examples": [
            {"context": "essay", "sentence": "AI regulation is still nascent — we're writing rules for a technology that changes faster than any committee can convene.", "why": "Nascent means just beginning to exist or develop. The regulation exists but is in its infancy."},
            {"context": "professional", "sentence": "The nascent partnership showed early promise, but it was too soon to predict whether the cultures would mesh.", "why": "Just starting, not yet mature enough to evaluate fully. Nascent signals 'give it time.'"},
            {"context": "social media", "sentence": "Every revolution starts as a nascent idea that most people dismiss as naive.", "why": "Nascent captures the vulnerable, embryonic stage where something could become huge or die quietly."}
        ],
        "misuses": [
            {"wrong": "The nascent company has been operating for 25 years.", "problem": "A 25-year-old company isn't nascent. Nascent means just beginning — days, months, maybe a year or two at most.", "use_instead": "established, mature, longstanding"},
            {"wrong": "She had a nascent dislike for him that had been growing for years.", "problem": "If it's been growing for years, it's not nascent. Nascent means just beginning to form.", "use_instead": "deep-seated, long-held, entrenched"}
        ],
        "related": [
            {"word": "embryonic", "distinction": "'Embryonic' is more informal and implies even earlier stage. 'Nascent' is the moment something starts to exist."},
            {"word": "incipient", "distinction": "Nearly synonymous. 'Incipient' slightly emphasizes the very beginning. 'Nascent' emphasizes emergence and growth potential."},
            {"word": "latent", "distinction": "'Latent' means existing but not yet visible. 'Nascent' means just starting to become visible — it's crossed the threshold from hidden to emerging."}
        ],
        "triggers": ["Describing something in its earliest stage of development", "Writing about emerging trends, ideas, or movements", "Signaling that something is too new to judge but worth watching"]
    },
    {
        "word": "Insidious",
        "pronunciation": "in-SID-ee-us",
        "register": ["formal", "general"],
        "tags": ["danger", "deception", "hidden"],
        "examples": [
            {"context": "essay", "sentence": "The insidious thing about algorithmic feeds isn't the content they show you — it's the content they quietly hide.", "why": "Insidious means treacherous in a way you don't detect. The harm is in what you never see, not what you do."},
            {"context": "professional", "sentence": "Scope creep is insidious. No single request seems unreasonable, but together they double the timeline.", "why": "Each small addition looks harmless. The pattern is only visible in hindsight. That's insidious."},
            {"context": "social media", "sentence": "The most insidious form of self-sabotage is the one that looks like productivity.", "why": "Hidden harm disguised as virtue. Insidious captures the betrayal of something that seems good but isn't."}
        ],
        "misuses": [
            {"wrong": "The insidious explosion destroyed the building.", "problem": "'Insidious' means gradual, hidden, creeping. An explosion is sudden and obvious — the opposite.", "use_instead": "devastating, catastrophic, violent"},
            {"wrong": "She made an insidious effort to help the community.", "problem": "'Insidious' is always negative — it implies harmful intent or effect. A helpful effort can't be insidious.", "use_instead": "tireless, dedicated, sustained"}
        ],
        "related": [
            {"word": "pernicious", "distinction": "'Pernicious' emphasizes the HARM (gradual and destructive). 'Insidious' emphasizes the DECEPTION (you don't see it coming)."},
            {"word": "surreptitious", "distinction": "'Surreptitious' means done in secret. 'Insidious' means the secrecy itself causes harm — the hiding IS the danger."},
            {"word": "subtle", "distinction": "'Subtle' is neutral — it can be positive. 'Insidious' is always negative: subtle AND harmful."}
        ],
        "triggers": ["Describing harm that disguises itself as harmless or even beneficial", "Writing about hidden dangers in systems, habits, or cultural norms", "When 'dangerous' is too blunt and you want to convey the stealth of the threat"]
    },
    {
        "word": "Recalcitrant",
        "pronunciation": "reh-KAL-sih-trant",
        "register": ["formal"],
        "tags": ["resistance", "stubbornness", "authority"],
        "examples": [
            {"context": "essay", "sentence": "The recalcitrant minority held up the vote for three sessions, not because they had better ideas, but because they could.", "why": "Recalcitrant means stubbornly resistant to authority or control. It implies defiance, not just disagreement."},
            {"context": "professional", "sentence": "We've got one recalcitrant stakeholder who refuses to sign off on the migration, despite every risk being mitigated.", "why": "Not just resistant — actively refusing to comply even when the objections have been addressed."},
            {"context": "social media", "sentence": "My toddler is magnificently recalcitrant. Every request is met with the full force of a tiny dictator's defiance.", "why": "Humorous formality applied to a toddler. The word's weight makes the mundane situation funnier."}
        ],
        "misuses": [
            {"wrong": "The recalcitrant student studied hard every night.", "problem": "A diligent student isn't recalcitrant. Recalcitrant means resisting authority or rules.", "use_instead": "diligent, dedicated, studious"},
            {"wrong": "She was recalcitrant about the good news.", "problem": "'Recalcitrant' means resistant to authority, not reluctant to accept something. The word implies defiance, not hesitation.", "use_instead": "skeptical, hesitant, wary"}
        ],
        "related": [
            {"word": "obstinate", "distinction": "'Obstinate' means stubborn in general. 'Recalcitrant' specifically means resistant to AUTHORITY or control."},
            {"word": "intransigent", "distinction": "'Intransigent' means refusing to compromise. 'Recalcitrant' means refusing to obey or comply — it implies a power dynamic."},
            {"word": "defiant", "distinction": "'Defiant' is more openly confrontational. 'Recalcitrant' can be passive resistance — just refusing to move."}
        ],
        "triggers": ["Describing stubborn resistance specifically to authority or direction", "Writing about power dynamics where someone refuses to comply", "When 'stubborn' is too mild and you want to convey active defiance"]
    },
    {
        "word": "Ameliorate",
        "pronunciation": "uh-MEEL-yuh-rayt",
        "register": ["formal", "academic"],
        "tags": ["improvement", "change", "relief"],
        "examples": [
            {"context": "essay", "sentence": "Technology can ameliorate poverty, but it cannot eliminate it — the structural causes run deeper than any app.", "why": "Ameliorate means to make something bad slightly better, not to fix it entirely. The distinction from 'solve' is the whole point."},
            {"context": "professional", "sentence": "This patch ameliorates the performance issue but doesn't resolve the underlying architecture problem.", "why": "Precise: it improves the situation without claiming to fix it. Sets expectations accurately."},
            {"context": "social media", "sentence": "Therapy doesn't fix you. It ameliorates the suffering enough that you can function while doing the real work.", "why": "Captures the honest, partial nature of improvement. Not a cure — a meaningful reduction of harm."}
        ],
        "misuses": [
            {"wrong": "The chef ameliorated the recipe by adding truffle oil.", "problem": "'Ameliorate' is for making bad things better, not making good things fancier. A recipe isn't a problem to be ameliorated.", "use_instead": "elevated, enhanced, refined"},
            {"wrong": "She ameliorated the already successful business.", "problem": "'Ameliorate' implies improving something that's currently BAD. You don't ameliorate success.", "use_instead": "expanded, grew, strengthened"}
        ],
        "related": [
            {"word": "alleviate", "distinction": "'Alleviate' means to reduce suffering or a burden. 'Ameliorate' means to make an overall situation better — broader scope."},
            {"word": "mitigate", "distinction": "'Mitigate' means to make less severe. 'Ameliorate' means to actually improve, not just reduce the damage."},
            {"word": "improve", "distinction": "'Improve' is neutral. 'Ameliorate' specifically implies improving something that was bad — it carries the weight of the original problem."}
        ],
        "triggers": ["Describing partial improvement of a bad situation (not a complete fix)", "Writing about nuanced progress — when things get better but aren't solved", "When 'improve' is too generic and you want to signal the severity of what's being improved"]
    },
    {
        "word": "Tacit",
        "pronunciation": "TAS-it",
        "register": ["formal", "general"],
        "tags": ["communication", "silence", "understanding"],
        "examples": [
            {"context": "essay", "sentence": "There was a tacit agreement among the team: we don't talk about the layoffs, and leadership doesn't ask why morale is low.", "why": "Tacit means understood without being stated. Nobody agreed to this — everyone just knows."},
            {"context": "professional", "sentence": "His silence wasn't ignorance — it was tacit approval. He knew what was happening and chose not to intervene.", "why": "Silence as communication. Tacit approval means you didn't object, which is its own kind of endorsement."},
            {"context": "social media", "sentence": "Every society runs on tacit rules. The written ones are just the ones we couldn't trust each other to follow silently.", "why": "Tacit captures the invisible social contracts we all observe without ever discussing them."}
        ],
        "misuses": [
            {"wrong": "She gave a tacit speech about her beliefs.", "problem": "'Tacit' means unspoken — silent. You can't give a tacit speech. That's a contradiction.", "use_instead": "impassioned, candid, heartfelt"},
            {"wrong": "The tacit explosion shook the building.", "problem": "'Tacit' means silent and implied. Explosions are the opposite of tacit.", "use_instead": "sudden, massive, deafening"}
        ],
        "related": [
            {"word": "implicit", "distinction": "'Implicit' means implied but could be made explicit. 'Tacit' means understood through silence — it's the absence of speech that carries the meaning."},
            {"word": "unspoken", "distinction": "Direct synonym, just less formal. 'Tacit' carries more weight and is more precise."},
            {"word": "explicit", "distinction": "Opposite. 'Explicit' means stated directly. 'Tacit' means understood without being stated."}
        ],
        "triggers": ["Describing understanding or agreement that exists without being spoken", "Writing about silence as communication", "When you want to name the invisible rules or agreements that govern behavior"]
    },
    {
        "word": "Magnanimous",
        "pronunciation": "mag-NAN-ih-mus",
        "register": ["formal", "literary"],
        "tags": ["character", "generosity", "forgiveness"],
        "examples": [
            {"context": "essay", "sentence": "The magnanimous response to betrayal isn't forgetting — it's choosing not to retaliate when you easily could.", "why": "Magnanimous means generous and forgiving from a position of power. The 'could retaliate but chooses not to' is essential."},
            {"context": "professional", "sentence": "The CEO was magnanimous in victory, publicly crediting the team rather than claiming the turnaround as his own.", "why": "Generosity from someone who could have taken all the credit. Magnanimity requires the power to be otherwise."},
            {"context": "social media", "sentence": "Being magnanimous when you've won is easy. Being magnanimous when you've been wronged? That's character.", "why": "Challenges the idea that magnanimity is just for victors. Extends it to moral generosity after being harmed."}
        ],
        "misuses": [
            {"wrong": "The magnanimous child shared her toy with her brother.", "problem": "A child sharing is nice, but 'magnanimous' implies greatness of spirit from a position of significant power or advantage. It's too grand for small gestures.", "use_instead": "generous, kind, sharing"},
            {"wrong": "He made a magnanimous donation of five dollars.", "problem": "'Magnanimous' implies exceptional generosity. Five dollars doesn't reach that threshold.", "use_instead": "small, modest, token"}
        ],
        "related": [
            {"word": "generous", "distinction": "'Generous' is general. 'Magnanimous' implies generosity from a position of power, specifically toward someone who wronged you or who you've defeated."},
            {"word": "benevolent", "distinction": "'Benevolent' means well-meaning and kind. 'Magnanimous' means noble and forgiving — it carries more moral weight."},
            {"word": "gracious", "distinction": "'Gracious' is about manner and politeness. 'Magnanimous' is about the scale and nobility of spirit — it's grander."}
        ],
        "triggers": ["Describing generosity or forgiveness from a position of power", "Writing about leadership, character, or moral excellence", "When 'generous' doesn't capture the nobility of choosing forgiveness over revenge"]
    },
    {
        "word": "Ostensible",
        "pronunciation": "ah-STEN-sih-bul",
        "register": ["formal", "general"],
        "tags": ["appearance", "deception", "surface"],
        "examples": [
            {"context": "essay", "sentence": "The ostensible purpose of the meeting was to discuss budgets, but everyone knew it was really about the restructuring.", "why": "Ostensible means appearing to be true on the surface but likely hiding the real truth. It's a polite way to say 'stated but not believed.'"},
            {"context": "professional", "sentence": "The ostensible reason for the acquisition was market expansion, but the real driver was eliminating a competitor.", "why": "The official explanation vs. the actual motivation. 'Ostensible' flags the gap."},
            {"context": "social media", "sentence": "The ostensible point of networking events is professional growth. The actual point is free drinks and ego validation.", "why": "Humorous use: the gap between what something claims to be and what it actually is."}
        ],
        "misuses": [
            {"wrong": "The ostensible leader was genuinely respected and followed by everyone.", "problem": "If the leader is genuinely respected, they're not 'ostensible.' Ostensible implies the label might not match reality.", "use_instead": "recognized, respected, established"},
            {"wrong": "She gave an ostensible effort on the project.", "problem": "'Ostensible' modifies claims and appearances, not quality of effort. An effort can't be ostensible.", "use_instead": "genuine, sincere, substantial (or 'token, minimal' if you mean the opposite)"}
        ],
        "related": [
            {"word": "apparent", "distinction": "'Apparent' is more neutral — it might be true. 'Ostensible' carries a stronger implication that it's probably NOT true."},
            {"word": "purported", "distinction": "'Purported' means claimed to be. 'Ostensible' means appearing to be. Purported is more accusatory."},
            {"word": "nominal", "distinction": "'Nominal' means in name only. 'Ostensible' means in appearance — broader than just a title."}
        ],
        "triggers": ["Flagging a gap between stated purpose and actual purpose", "Writing about spin, PR, or institutional messaging", "When you want to say 'supposedly' but with more precision and less sarcasm"]
    },
    {
        "word": "Acquiesce",
        "pronunciation": "ak-wee-ES",
        "register": ["formal"],
        "tags": ["agreement", "submission", "compliance"],
        "examples": [
            {"context": "essay", "sentence": "She didn't agree with the policy — she acquiesced to it, which is a fundamentally different act.", "why": "Acquiesce means to accept something reluctantly, without protest, but not with genuine agreement. The distinction from 'agree' is everything."},
            {"context": "professional", "sentence": "The board acquiesced to the CEO's plan, not because they believed in it, but because fighting it wasn't worth the political cost.", "why": "Strategic non-resistance. They didn't agree — they stopped objecting. That's acquiescence."},
            {"context": "social media", "sentence": "Most people don't consent to terms of service. They acquiesce. There's a difference, and companies know it.", "why": "Drawing the line between genuine consent and resigned compliance. Acquiesce captures the powerlessness."}
        ],
        "misuses": [
            {"wrong": "She enthusiastically acquiesced to the promotion.", "problem": "'Acquiesce' implies reluctance or resignation. If she's enthusiastic, she didn't acquiesce — she accepted eagerly.", "use_instead": "accepted, embraced, jumped at"},
            {"wrong": "He acquiesced his own plan to the committee.", "problem": "'Acquiesce' is intransitive — you acquiesce TO something. You don't acquiesce something.", "use_instead": "presented, proposed, submitted"}
        ],
        "related": [
            {"word": "concede", "distinction": "'Concede' means admitting the other side is right. 'Acquiesce' means giving in without necessarily agreeing."},
            {"word": "capitulate", "distinction": "'Capitulate' means surrendering completely, often after resistance. 'Acquiesce' is quieter — you simply stop fighting."},
            {"word": "comply", "distinction": "'Comply' is neutral — following instructions. 'Acquiesce' carries the emotional weight of reluctant acceptance."}
        ],
        "triggers": ["Describing reluctant acceptance without genuine agreement", "Writing about power dynamics where someone gives in but doesn't agree", "Distinguishing between genuine consent and resigned compliance"]
    },
]

def main():
    with open("vocab_db.json", "r", encoding="utf-8") as f:
        db = json.load(f)

    enrichment_map = {e["word"].lower(): e for e in ENRICHED}
    enriched_count = 0

    for entry in db["words"]:
        key = entry["word"].lower()
        if key in enrichment_map:
            e = enrichment_map[key]
            entry["pronunciation"] = e.get("pronunciation", entry["pronunciation"])
            entry["register"] = e["register"]
            entry["tags"] = e["tags"]
            entry["examples"] = e["examples"]
            entry["misuses"] = e["misuses"]
            entry["related"] = e["related"]
            entry["triggers"] = e["triggers"]
            entry["enriched"] = True
            enriched_count += 1

    db["meta"]["last_updated"] = str(date.today())

    with open("vocab_db.json", "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

    print(f"Enriched {enriched_count} words")

if __name__ == "__main__":
    main()
