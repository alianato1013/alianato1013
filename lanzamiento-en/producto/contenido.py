"""Content of the In Order Co. products (English edition).

Each product is a list of blocks. Block types understood by build_binder.py:
  ("cover", title, subtitle, tagline)
  ("section", number, title, subtitle)            -> new page with the section tab
  ("ten", [quick tasks])                           -> the "If you only have 10 minutes" box
  ("p", text)                                      -> paragraph
  ("h", text)                                      -> small heading
  ("fields", [labels])                             -> one fillable line per label
  ("box", label, lines)                            -> multi-line fillable box
  ("table", title, [column headers], rows, [relative widths])
  ("checks", [labels])                             -> fillable checkboxes
  ("note", text)                                   -> highlighted tip
  ("pagebreak",)
"""

DISCLAIMER = ("This binder is a personal organizer. It is not a will, a power of attorney or a "
              "medical directive, and it is not legal, medical or financial advice. Laws differ by "
              "state and country: ask a local professional for legal documents.")

SAFETY = ("Never write full passwords or PINs in this binder. Write where things are and how your "
          "person can get to them: the name of your password manager, who holds the emergency "
          "access, and where a sealed envelope is kept.")

CORE = [
    ("cover", "The Solo Adult's", "Just-In-Case Binder",
     "Everything your person needs. Nothing they'd have to guess."),
    ("section", "", "How to use this binder", "Ten minutes today. One afternoon for everything."),
    ("p", "You are everyone's emergency contact. This binder makes sure you have one too. If "
          "something happens to you tonight, your person opens this and finds what matters in "
          "ten minutes: who to call, who feeds your pet, how to get into your home, what pays "
          "itself every month and what you want."),
    ("h", "Three rules"),
    ("checks", ["Start with section 1, 'Start Here'. It takes ten minutes and covers the urgent things.",
                "Each section opens with a short list. Do that list first; fill in the rest later.",
                "Review it once a year (section 12). Put a reminder in your calendar now."]),
    ("note", SAFETY),
    ("h", "Fill it in on screen or print it"),
    ("p", "Type directly into this PDF with any free PDF reader (Adobe Acrobat Reader, Preview on Mac, "
          "your browser) and save it. Or print it and keep it in a binder. Tell your person where it is."),
    ("fields", ["This binder lives at (place / folder / app):", "My person knows where it is (date I told them):"]),
    ("note", DISCLAIMER),

    # 1
    ("section", "1", "Start Here", "The 10-minute page. If you do nothing else, do this."),
    ("ten", ["Write the name and phone of your person", "Write your doctor and your main medication",
             "Write who has a key to your home", "If you have a pet: who picks them up today"]),
    ("fields", ["My full name:", "Date of birth:", "Address:",
                "My person (name):", "My person's phone:", "Backup person and phone:",
                "My doctor and phone:", "My main medications / allergies:",
                "Who has a key to my home:", "My pet(s) and who picks them up today:",
                "Password manager I use (no passwords!):", "Who has emergency access to it:",
                "Where my important documents are:", "Today's date:"]),

    # 2
    ("section", "2", "My Person", "The one person who should be called first and can act for you."),
    ("ten", ["Choose your person and ask them (yes, ask)", "Write how they get into your home",
             "Write one message for them in the letter box"]),
    ("fields", ["My person: full name", "Relationship to me:", "Phone(s):", "Email:", "Address:",
                "Backup person: full name", "Backup phone(s):"]),
    ("checks", ["My person has agreed to this role", "My person knows where this binder is",
                "My person has (or knows where to find) a key to my home",
                "My person is listed as emergency contact on my phone",
                "I have a legal document naming who can decide for me (where it is: section 9)"]),
    ("table", "Who to tell, and when", ["Name", "Relationship", "Phone", "Tell them when..."],
     6, [3, 2, 2.5, 3.5]),
    ("box", "A letter to my person (what to do first, what I would want)", 10),

    # 3
    ("section", "3", "Medical in 60 Seconds", "The page you hand to the emergency room."),
    ("ten", ["List allergies", "List your daily medications", "Write your doctor and insurance"]),
    ("fields", ["Allergies (medications, food, other):", "Medical conditions:", "Blood type (if known):",
                "Implants / devices (pacemaker, insulin pump...):", "Preferred hospital:",
                "Pharmacy and phone:", "Health insurance and member number (last 4 digits):",
                "Where my insurance card is:"]),
    ("table", "Medications", ["Medication", "Dose", "How often", "What it is for"], 8, [3, 1.5, 2, 3.5]),
    ("table", "My doctors", ["Name", "Specialty", "Phone", "Clinic / address"], 5, [2.5, 2, 2, 3.5]),

    # 4
    ("section", "4", "Home Access", "How your person gets in, and what keeps your home running."),
    ("ten", ["Write who has a spare key", "Write where the alarm instructions are (not the code)",
             "List your landlord or building manager"]),
    ("table", "Who has a key", ["Name", "Phone", "Which keys"], 4, [3, 2.5, 3.5]),
    ("fields", ["Spare key location (hint only):", "Alarm company and phone:",
                "Where the alarm code is kept (not the code):", "Landlord / building manager and phone:",
                "Car: where the keys and title are:", "Storage unit / mailbox / locker:"]),
    ("table", "Utilities and services", ["Service", "Provider", "Account (last 4)", "Autopay?"],
     7, [2.5, 3, 2, 1.5]),

    # 5
    ("section", "5", "Money Map", "A map, not a vault: where your money is, never your passwords."),
    ("ten", ["List your bank accounts (last 4 digits only)", "List your cards",
             "Write where your tax returns are"]),
    ("table", "Bank accounts", ["Institution", "Type", "Last 4", "Beneficiary set?"], 6, [3, 2, 1.5, 2]),
    ("table", "Credit and debit cards", ["Issuer", "Last 4", "Autopays from it?"], 5, [3.5, 1.5, 4]),
    ("table", "Loans and debts", ["Lender", "Type", "Last 4", "Monthly payment"], 5, [3, 2, 1.5, 2.5]),
    ("table", "Retirement, investments, insurance", ["Company", "Type", "Last 4", "Beneficiary"],
     6, [3, 2, 1.5, 2.5]),
    ("fields", ["Where my tax returns are:", "Accountant / advisor and phone:",
                "Safe deposit box (bank, where the key is):"]),

    # 6
    ("section", "6", "Bills & Auto-Pay Calendar", "Everything that charges you by itself."),
    ("ten", ["List the 5 biggest monthly bills", "Mark which are on autopay"]),
    ("table", "Monthly", ["Bill", "Amount", "Day", "Paid from", "Autopay?"], 10, [3, 1.5, 1, 2.5, 1.5]),
    ("table", "Yearly and subscriptions", ["Service", "Amount", "Renews (month)", "Cancel how?"],
     8, [3, 1.5, 2, 3]),

    # 7
    ("section", "7", "Digital Life & 2FA", "Your phone is the key to your whole life. Who else has it?"),
    ("ten", ["Write the name of your password manager", "Set up its emergency access for your person",
             "Write where your 2FA recovery codes are"]),
    ("note", SAFETY),
    ("fields", ["Password manager:", "Emergency / legacy access given to:",
                "Where my 2FA recovery codes are (envelope, safe, manager):",
                "How my person can unlock my phone (hint, not the PIN):",
                "Main email account(s):", "Phone carrier and account holder:"]),
    ("checks", ["I turned on the legacy / emergency contact options my phone and accounts offer",
                "My person knows which email receives my bank and bill notices",
                "I have a backup of my photos (where: ____ )"]),
    ("table", "Accounts and what I want done", ["Account", "Username / email", "Keep, memorialize or delete?"],
     8, [3, 3.5, 3]),

    # 8
    ("section", "8", "My Pet Plan", "Who feeds your pet if you don't come home tonight?"),
    ("ten", ["Write who picks up your pet today", "Write food and medication", "Print the door card (Kit)"]),
    ("fields", ["Pet name(s) and species:", "Age / breed / microchip number:", "Vet and phone:",
                "Food: brand and amount:", "Medications and schedule:",
                "Who picks them up TODAY (name, phone):", "Long-term guardian (name, phone):",
                "Money set aside for my pet (where):"]),
    ("box", "Daily routine, fears, things they love", 8),

    # 9
    ("section", "9", "Documents Locator", "Where every original is, and what you still need."),
    ("ten", ["Write where your ID and passport are", "Write where your insurance policies are"]),
    ("table", "Where things are", ["Document", "Where the original is", "Copy / digital"],
     14, [3, 4, 2.5]),
    ("checks", ["ID / driver's licence", "Passport", "Birth certificate", "Social security / national ID card",
                "Will (if I have one)", "Power of attorney (if I have one)", "Healthcare directive (if I have one)",
                "Property deed or lease", "Car title and registration", "Insurance policies",
                "Recent tax returns", "Employment / pension / benefits papers"]),

    # 10
    ("section", "10", "If I Can't Speak", "Your care wishes, so nobody has to guess."),
    ("ten", ["Write who is authorized to talk to your doctors", "Write three things that matter to you"]),
    ("note", "This section records your wishes for your person. It is not a legal healthcare directive. "
             "If you want one, ask a local professional, and write where it is in section 9."),
    ("fields", ["Person authorized to speak with my doctors:", "Their phone:",
                "I have a legal healthcare directive / living will (where):",
                "Organ donation wishes:", "Religious or cultural needs:"]),
    ("box", "What matters most to me if I am seriously ill", 9),

    # 11
    ("section", "11", "Final Wishes & Letters", "Not about death: about not leaving chaos and guessing."),
    ("ten", ["Write one sentence about what you'd want", "Write who should be told first"]),
    ("checks", ["Burial", "Cremation", "No preference", "Donate body to science",
                "Religious service", "Celebration of life", "Nothing formal"]),
    ("fields", ["Funeral home / plan already paid (where):", "Where my ashes / grave should be:",
                "Music, readings or words I'd like:", "Charity for donations in my name:"]),
    ("box", "Facts for an obituary (dates, places, people, what I loved)", 7),
    ("box", "Letters I have written and where they are", 5),

    # 12
    ("section", "12", "Annual Review", "Fifteen minutes, once a year. Pick a date you won't forget."),
    ("checks", ["My person is still the right person (and still agrees)", "Phone numbers are current",
                "Medications and doctors are current", "Accounts and cards are current",
                "Autopays and subscriptions are current", "Pet details are current",
                "Documents are where I say they are", "I told my person where this binder is"]),
    ("table", "Update log", ["Date", "What I updated", "Initials"], 10, [2, 6, 1.5]),
    ("note", "Thank you for doing this. It is one of the kindest things you can do for the people you love."),
]

KIT = [
    ("cover", "Emergency", "Cards & Quick Sheets",
     "Print, cut, and carry. The binder's best friend."),
    ("section", "", "How to use the Kit", "Fill in on screen, print on card stock, cut along the boxes."),
    ("checks", ["Wallet card: behind your ID", "Door / fridge card: for anyone who enters your home",
                "Pet alert card: inside your front door", "ER sheet: one page, folded in your bag"]),
    ("section", "A", "Wallet card", "Two copies: one for your wallet, one for your bag."),
    ("fields", ["In case of emergency call (name):", "Phone:", "Second contact and phone:",
                "Allergies:", "Medications:", "Conditions:", "My pet is home alone, call:"]),
    ("fields", ["(copy) In case of emergency call (name):", "(copy) Phone:", "(copy) Allergies:",
                "(copy) My pet is home alone, call:"]),
    ("section", "B", "Door / fridge card", "For a neighbor, a paramedic or a pet sitter."),
    ("fields", ["My name:", "My person (name, phone):", "My doctor:", "Where my medical sheet is:",
                "Pets in this home (names):", "Who takes care of them (name, phone):"]),
    ("section", "C", "Pet alert card", "Tape it inside your door or on your keyring."),
    ("fields", ["Pet name(s):", "Food and amount:", "Medication:", "Vet:", "Emergency pet carer (name, phone):"]),
    ("section", "D", "ER sheet", "One page. Hand it over at the hospital."),
    ("fields", ["Full name and date of birth:", "Allergies:", "Medications and doses:", "Conditions:",
                "Doctor and phone:", "Insurance (last 4):", "My person (name, phone):",
                "Authorized to speak with doctors:"]),
    ("note", DISCLAIMER),
]

DIGITAL = [
    ("cover", "Digital Legacy", "Deep-Dive",
     "Your phone, your accounts, your photos: ready, without sharing a single password."),
    ("section", "", "Before you start", "The goal: your person can act without ever knowing your passwords."),
    ("note", SAFETY),
    ("checks", ["I use a password manager (or will set one up today)",
                "I know where my phone's emergency / legacy contact settings are",
                "I have a place for a sealed envelope (safe, trusted drawer, attorney)"]),
    ("section", "1", "Device plan", "Phone, computer, tablet."),
    ("table", "Devices", ["Device", "How my person can access it (hint)", "Wipe, keep or give?"], 5, [2.5, 4.5, 2.5]),
    ("section", "2", "Account inventory", "By category, so nothing is forgotten."),
    ("table", "Email and phone", ["Account", "Username", "Recovery method", "What to do"], 5, [2.5, 3, 2.5, 2]),
    ("table", "Banking and money apps", ["App / site", "Username", "Recovery", "What to do"], 6, [2.5, 3, 2.5, 2]),
    ("table", "Social media", ["Platform", "Username", "Legacy contact set?", "Memorialize / delete"], 6, [2.5, 3, 2, 2.5]),
    ("table", "Shopping, streaming, subscriptions", ["Service", "Username", "Charges to", "Cancel?"], 8, [2.5, 3, 2.5, 2]),
    ("section", "3", "2FA and recovery", "The step that blocks everything else if it's missing."),
    ("fields", ["Authenticator app I use:", "Where my backup / recovery codes are:",
                "Phone number used for text codes:", "What happens if my phone is lost (plan):"]),
    ("section", "4", "Photos and memories", "What to keep, and who should have it."),
    ("fields", ["Where my photos are backed up:", "Who should receive copies:", "Videos / files that matter most:"]),
    ("box", "Notes for my person", 8),
    ("section", "5", "Legacy settings checklist", "Turn on what your devices and accounts offer."),
    ("checks", ["Phone: emergency contact on the lock screen / medical ID",
                "Phone account: legacy or inactive-account contact turned on",
                "Email: inactive-account / legacy option reviewed",
                "Social media: legacy contact or memorialization choice made",
                "Password manager: emergency access granted to my person",
                "Cloud photos: shared album or backup my person can reach"]),
    ("note", "Each company names and places these settings differently and changes them over time. "
             "Check the current help pages of each service when you turn them on."),
]
