"""
Plant Disease Knowledge Base for AgriShield AI.
Covers 38 classes across 14 crop types derived from the benchmark PlantVillage taxonomy.
Provides scientific disease metadata, symptoms, causes, prevention, and IPM treatments.
"""

DISEASE_KNOWLEDGE_BASE = {
    "Apple___Apple_scab": {
        "crop": "Apple",
        "disease": "Apple Scab",
        "is_healthy": False,
        "pathogen_type": "Fungal (Venturia inaequalis)",
        "severity": "High",
        "description": "A serious fungal disease that produces velvety olive-green to black spots on leaves and fruit, causing premature defoliation and cracked, stunted fruit.",
        "symptoms": [
            "Olive-green to dull black spots with velvety texture on leaf surfaces",
            "Yellowing around leaf lesions leading to premature leaf drop",
            "Scabby, corky, cracked circular lesions on apples",
            "Curled or distorted young leaves"
        ],
        "causes": "Thrives in prolonged leaf wetness (6+ hours) and cool spring temperatures between 15°C and 24°C with high morning humidity.",
        "prevention": [
            "Rake and destroy fallen leaves in autumn to eliminate overwintering fungal pseudothecia",
            "Prune canopy during dormancy to promote rapid leaf drying and sunlight penetration",
            "Select resistant cultivars such as Prima, Priscilla, Enterprise, or Freedom"
        ],
        "treatment": {
            "biological": [
                "Spray Bacillus subtilis bio-fungicide @ 3 g/L at bud break",
                "Neem oil 10,000 ppm @ 3 ml/L as an early-season deterrent",
                "Sulfur-based organic dusts during pre-bloom stages"
            ],
            "chemical": [
                "Difenoconazole 25% EC @ 30 ml/100L water during petal fall",
                "Mancozeb 75% WP @ 2.5 g/L as a protective contact barrier",
                "Captan 50% WP @ 2 g/L before forecasted rainfall events"
            ]
        }
    },
    "Apple___Black_rot": {
        "crop": "Apple",
        "disease": "Black Rot",
        "is_healthy": False,
        "pathogen_type": "Fungal (Botryosphaeria obtusa)",
        "severity": "High",
        "description": "Causes 'frog-eye' leaf spots, sunken limb cankers, and a firm, dark brown to black rot of maturing fruit.",
        "symptoms": [
            "Frog-eye leaf spots: circular purple-bordered lesions with light brown centers",
            "Concentric rings of black pycnidia on rotting fruit",
            "Mummified blackened apples hanging in the winter canopy",
            "Sunken, reddish-brown cankers on branches and scaffold limbs"
        ],
        "causes": "Spreads through fungal spores in dead wood, fire blight cankers, and mummified fruit during warm, wet summer weather (20°C–28°C).",
        "prevention": [
            "Prune out dead branches, twigs, and mummified fruit 15 cm below canker margins",
            "Paint cut wounds with pruning sealant to prevent fungal entry",
            "Control codling moth and other insects that create fruit puncture entry wounds"
        ],
        "treatment": {
            "biological": [
                "Trichoderma viride bio-fungicide paste @ 10 g/L on pruning cuts",
                "Liquid Copper octanoate (Copper soap) @ 4 ml/L water"
            ],
            "chemical": [
                "Thiophanate-methyl 70% WP @ 1 g/L spray",
                "Captan 80% WDG @ 1.8 g/L applied every 10–14 days from petal fall",
                "Tebuconazole 25.9% EC @ 1 ml/L for canker suppression"
            ]
        }
    },
    "Apple___Cedar_apple_rust": {
        "crop": "Apple",
        "disease": "Cedar Apple Rust",
        "is_healthy": False,
        "pathogen_type": "Fungal (Gymnosporangium juniperi-virginianae)",
        "severity": "Medium",
        "description": "A heteroecious rust fungus requiring both Apple and Eastern Red Cedar (Juniperus) to complete its complex two-year life cycle.",
        "symptoms": [
            "Bright orange-yellow circular spots on the upper leaf surface",
            "Tiny black dots (spermogonia) centered inside orange leaf spots",
            "Raised tube-like fungal aecia on the underside of leaves releasing powdery spores",
            "Swollen, distorted twigs and fruit lesions"
        ],
        "causes": "Airborne aeciospores blown from gelatinous orange galls on neighboring cedar trees during warm rainy spring spells (12°C–24°C).",
        "prevention": [
            "Remove alternate host red cedar/juniper trees within 500 meters of the orchard",
            "Plant resistant apple cultivars like Liberty, Freedom, or Williams Pride",
            "Inspect and clip out cedar galls from ornamental landscape junipers in winter"
        ],
        "treatment": {
            "biological": [
                "Wettable Sulfur @ 3 g/L applied before rain events",
                "Copper hydroxide @ 2 g/L during early pink bud stage"
            ],
            "chemical": [
                "Myclobutanil 10% WP @ 0.5 g/L applied from pink bud through petal fall",
                "Mancozeb 75% WP @ 2 g/L every 7–10 days during spore dispersal",
                "Propiconazole 25% EC @ 1 ml/L"
            ]
        }
    },
    "Apple___healthy": {
        "crop": "Apple",
        "disease": "Healthy Plant Condition",
        "is_healthy": True,
        "pathogen_type": "None",
        "severity": "Low",
        "description": "The apple foliage exhibits vibrant green coloration, uniform leaf lamina, and complete absence of fungal chlorosis or necrotic lesions.",
        "symptoms": [
            "Firm, glossy leaves with clear venation",
            "No powdery deposits, black pustules, or frog-eye spots",
            "Vigorous shoot extension and healthy terminal buds"
        ],
        "causes": "Optimal soil nutrition, balanced micronutrient uptake, and effective baseline orchard hygiene.",
        "prevention": [
            "Maintain balanced N-P-K soil fertilization (avoid excess nitrogen)",
            "Ensure regular drip irrigation avoiding overhead sprinkler wetting",
            "Continue standard seasonal monitoring for leafhoppers and spider mites"
        ],
        "treatment": {
            "biological": [
                "Prophylactic foliar seaweed extract @ 2 ml/L to enhance systemic acquired resistance"
            ],
            "chemical": []
        }
    },
    "Blueberry___healthy": {
        "crop": "Blueberry",
        "disease": "Healthy Plant Condition",
        "is_healthy": True,
        "pathogen_type": "None",
        "severity": "Low",
        "description": "Healthy blueberry foliage displaying vigorous vegetative expansion, acidic soil compatibility, and absence of mummy berry or rust symptoms.",
        "symptoms": [
            "Intense deep green waxy leaves with smooth margins",
            "Absence of chlorotic interveinal striping or shoot tip dieback",
            "Robust cane growth with clean root crown"
        ],
        "causes": "Maintained acidic soil pH (4.5–5.5), proper pine bark mulching, and optimal microclimate aeration.",
        "prevention": [
            "Test and maintain soil pH between 4.5 and 5.2 using elemental sulfur",
            "Keep 7–10 cm pine needle or wood chip mulch around root zones",
            "Water with acidulated drip water during dry spells"
        ],
        "treatment": {
            "biological": [
                "Apply mycorrhizal inoculants to reinforce nutrient uptake"
            ],
            "chemical": []
        }
    },
    "Cherry_(including_sour)___Powdery_mildew": {
        "crop": "Cherry",
        "disease": "Powdery Mildew",
        "is_healthy": False,
        "pathogen_type": "Fungal (Podosphaera clandestina)",
        "severity": "Medium",
        "description": "Produces white superficial powdery patches on young terminal leaves and fruit, causing leaf curling and distorted fruit development.",
        "symptoms": [
            "Circular patches of white powdery fungal mycelium on lower leaf surfaces",
            "Upward curling and distortion of expanding terminal leaves",
            "Dull, unripened fruit with mottled or scarred surface skin"
        ],
        "causes": "Favored by warm temperatures (18°C–28°C), high relative humidity (70%+), and dense, shaded tree canopies without direct rain wash.",
        "prevention": [
            "Prune dense suckers and water sprouts to improve sunlight interception",
            "Avoid overhead irrigation which raises night-time humidity inside the canopy"
        ],
        "treatment": {
            "biological": [
                "Potassium bicarbonate @ 3 g/L as an organic curative eradicant",
                "Neem oil (Azadirachtin 0.03%) @ 3 ml/L spray",
                "Ampelomyces quisqualis bio-fungicide"
            ],
            "chemical": [
                "Hexaconazole 5% EC @ 1 ml/L water",
                "Penconazole 10% EC @ 0.5 ml/L",
                "Wettable Sulfur 80% WDG @ 2.5 g/L"
            ]
        }
    },
    "Cherry_(including_sour)___healthy": {
        "crop": "Cherry",
        "disease": "Healthy Plant Condition",
        "is_healthy": True,
        "pathogen_type": "None",
        "severity": "Low",
        "description": "Foliage exhibits rich emerald green luster without curling, powdery mildew deposits, or shot-hole perforations.",
        "symptoms": [
            "Smooth, intact leaf blades with uniform pigmentation",
            "Healthy internode spacing and clean petiole junctions"
        ],
        "causes": "Balanced nutrient management and optimal spring airflow.",
        "prevention": [
            "Maintain annual post-harvest copper sanitation spray",
            "Monitor soil drainage to avoid wet feet root asphyxiation"
        ],
        "treatment": {
            "biological": [],
            "chemical": []
        }
    },
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "crop": "Corn (Maize)",
        "disease": "Gray Leaf Spot (Cercospora)",
        "is_healthy": False,
        "pathogen_type": "Fungal (Cercospora zeae-maydis)",
        "severity": "High",
        "description": "One of the most destructive foliar diseases of corn worldwide, causing rectangular necrotic lesions that coalesce and destroy canopy photosynthesis.",
        "symptoms": [
            "Distinct rectangular lesions strictly bounded by parallel leaf veins",
            "Initial tan spots turning grayish-brown with yellow chlorotic halos",
            "Severe blight drying out whole leaves before grain fill",
            "Stalk lodging due to plant cannibalization of carbohydrates"
        ],
        "causes": "Prolonged high relative humidity (>90%) with warm temperatures (25°C–32°C) and reduced tillage leaving crop stubbles on the soil surface.",
        "prevention": [
            "Rotate out of corn for at least one season with legumes or sunflower",
            "Plow down infected maize stubble to accelerate residue decomposition",
            "Select high-tolerance hybrid seed varieties"
        ],
        "treatment": {
            "biological": [
                "Trichoderma harzianum soil and foliar bio-protective spray",
                "Copper oxychloride 50% WP @ 2.5 g/L"
            ],
            "chemical": [
                "Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 1 ml/L",
                "Pyraclostrobin 20% WG @ 1 g/L",
                "Propiconazole 25% EC @ 1 ml/L applied at tasseling (VT stage)"
            ]
        }
    },
    "Corn_(maize)___Common_rust_": {
        "crop": "Corn (Maize)",
        "disease": "Common Rust",
        "is_healthy": False,
        "pathogen_type": "Fungal (Puccinia sorghi)",
        "severity": "Medium",
        "description": "Characterized by golden-brown to cinnamon pustules scattered across both leaf surfaces, diminishing plant vigor and yield.",
        "symptoms": [
            "Oval to elongate cinnamon-brown powdery pustules (uredinia) on upper and lower leaf surfaces",
            "Ruptured leaf epidermis releasing reddish-brown airborne spores",
            "Severe chlorosis and necrosis of leaf tissue around clustered pustules"
        ],
        "causes": "Airborne spores carried on weather fronts, thriving in moderate temperatures (16°C–25°C) with frequent dew formation.",
        "prevention": [
            "Plant resistant corn hybrids carrying the Rp resistance gene family",
            "Stagger planting dates to avoid high spore flight windows"
        ],
        "treatment": {
            "biological": [
                "Neem oil 1500 ppm @ 3 ml/L at initial pustule sighting"
            ],
            "chemical": [
                "Mancozeb 75% WP @ 2.5 g/L at early infection",
                "Tebuconazole 25.9% EC @ 1 ml/L if >5% leaf area infected before silking"
            ]
        }
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "crop": "Corn (Maize)",
        "disease": "Northern Corn Leaf Blight",
        "is_healthy": False,
        "pathogen_type": "Fungal (Exserohilum turcicum)",
        "severity": "High",
        "description": "Causes massive, cigar-shaped grayish-green to tan lesions that rapidly burn through the canopy, causing up to 50% grain yield loss.",
        "symptoms": [
            "Large, elongated cigar-shaped lesions (2.5 to 15 cm long)",
            "Lesions start grayish-green, turning tan with olive-black spore masses during wet periods",
            "Premature death of leaves giving the field a burned appearance"
        ],
        "causes": "Cool to moderate temperatures (18°C–27°C) accompanied by extended wet periods and heavy dew.",
        "prevention": [
            "Bury infected crop residues with moldboard plowing",
            "Practice 2-year crop rotation with non-host crops like soybean or alfalfa",
            "Plant certified Ht-gene resistant seed"
        ],
        "treatment": {
            "biological": [
                "Pseudomonas fluorescens @ 5 g/L foliar spray"
            ],
            "chemical": [
                "Azoxystrobin 23% SC @ 1 ml/L",
                "Chlorothalonil 75% WP @ 2 g/L",
                "Tricyclazole 75% WP @ 1.5 g/L"
            ]
        }
    },
    "Corn_(maize)___healthy": {
        "crop": "Corn (Maize)",
        "disease": "Healthy Plant Condition",
        "is_healthy": True,
        "pathogen_type": "None",
        "severity": "Low",
        "description": "Vigorous maize stalk with broad, deep green arching leaves without striping, pustules, or cigar lesions.",
        "symptoms": [
            "Broad, rich green leaves with unbroken parallel venation",
            "Sturdy stalk development and clean nodal brace roots"
        ],
        "causes": "Balanced soil fertility, adequate zinc supplementation, and weed-free field preparation.",
        "prevention": [
            "Apply side-dressed nitrogen according to soil testing results",
            "Maintain optimal plant spacing for air movement"
        ],
        "treatment": {
            "biological": [],
            "chemical": []
        }
    },
    "Grape___Black_rot": {
        "crop": "Grape",
        "disease": "Black Rot",
        "is_healthy": False,
        "pathogen_type": "Fungal (Guignardia bidwellii)",
        "severity": "High",
        "description": "A devastating fungal disease that shrivels entire grape clusters into hard, black, mummified raisins and causes circular tan leaf spots.",
        "symptoms": [
            "Circular reddish-brown leaf spots with distinct dark borders and black pycnidia dots",
            "Infected berries turn pale, then brown, shriveling into hard, wrinkled black mummies",
            "Purplish-black cankers on young shoot stems"
        ],
        "causes": "Splashing rain and warm, humid conditions (21°C–30°C) during spring and early summer flowering.",
        "prevention": [
            "Collect and destroy all mummified grapes on the vine and ground during winter pruning",
            "Open the grape vine canopy with shoot positioning and leaf pulling around fruit zones"
        ],
        "treatment": {
            "biological": [
                "Copper octanoate spray @ 3 ml/L",
                "Bacillus amyloliquefaciens strain D747"
            ],
            "chemical": [
                "Myclobutanil 40% WP @ 0.5 g/L",
                "Kresoxim-methyl 44.3% SC @ 0.7 ml/L",
                "Mancozeb 75% WP @ 2.5 g/L before bloom"
            ]
        }
    },
    "Grape___Esca_(Black_Measles)": {
        "crop": "Grape",
        "disease": "Esca (Black Measles)",
        "is_healthy": False,
        "pathogen_type": "Fungal Complex (Phaeomoniella & Phaeoacremonium)",
        "severity": "High",
        "description": "A destructive wood trunk disease causing 'tiger-stripe' interveinal leaf scorch, dark berry spotting ('measles'), and vine apoplexy (sudden wilting).",
        "symptoms": [
            "'Tiger-stripe' chlorosis: yellow/red interveinal banding with necrotic margins",
            "Berries develop tiny purple-brown speckled spots resembling measles",
            "Internal dark wood rot and black vascular streaking inside vine trunks",
            "Sudden vine collapse and leaf desiccation during hot dry spells"
        ],
        "causes": "Fungal pathogens entering through winter pruning wounds, progressing slowly through vascular wood vessels over several seasons.",
        "prevention": [
            "Delay pruning until late winter when wounds heal more rapidly",
            "Paint all large cuts (>2 cm) immediately with pruning paste containing Trichoderma or copper",
            "Remove and incinerate dead or severely declining cordons and trunks"
        ],
        "treatment": {
            "biological": [
                "Trichoderma atroviride wound-protectant paste",
                "Foliar calcium and amino acid sprays to alleviate vascular stress"
            ],
            "chemical": [
                "No systemic cure exists once inside the wood; protect new wounds with Thiophanate-methyl paste"
            ]
        }
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "crop": "Grape",
        "disease": "Leaf Blight (Isariopsis Leaf Spot)",
        "is_healthy": False,
        "pathogen_type": "Fungal (Pseudocercospora cladosporioides)",
        "severity": "Medium",
        "description": "Causes dark, angular necrotic spots on mature grape leaves, leading to premature defoliation and compromised berry sugar accumulation.",
        "symptoms": [
            "Irregular, angular dark brown to black spots on leaves",
            "Spots coalesce to form large necrotic patches",
            "Premature leaf drop exposing grape clusters to sun-scald",
            "Velvety dark fungal growth on leaf undersides during high humidity"
        ],
        "causes": "High humidity, overhead sprinkler splashing, and moderate temperatures (22°C–28°C) late in the growing season.",
        "prevention": [
            "Ensure effective trellis canopy aeration and bottom wire weed clearing",
            "Avoid excessive late-season nitrogen applications"
        ],
        "treatment": {
            "biological": [
                "Bordeaux Mixture (1%) post-pruning spray",
                "Copper oxychloride 50% WP @ 2.5 g/L"
            ],
            "chemical": [
                "Carbendazim 50% WP @ 1 g/L",
                "Azoxystrobin 23% SC @ 1 ml/L",
                "Ziram 27% SC @ 2.5 ml/L"
            ]
        }
    },
    "Grape___healthy": {
        "crop": "Grape",
        "disease": "Healthy Plant Condition",
        "is_healthy": True,
        "pathogen_type": "None",
        "severity": "Low",
        "description": "Lush, well-balanced grapevine canopy showing healthy palmate leaves, clean tendrils, and uniform photosynthetic greening.",
        "symptoms": [
            "Vibrant green palmate leaves with sharp margins",
            "No black spots, powdery deposits, or yellow chlorotic banding",
            "Clean shoots and healthy cane lignification"
        ],
        "causes": "Proper shoot positioning, balanced potassic nutrition, and regular prophylactic canopy hygiene.",
        "prevention": [
            "Maintain cane pruning schedule and annual micronutrient spray (Boron, Zinc)",
            "Drip irrigate at root line without wetting the foliage"
        ],
        "treatment": {
            "biological": [],
            "chemical": []
        }
    },
    "Orange___Haunglongbing_(Citrus_greening)": {
        "crop": "Orange (Citrus)",
        "disease": "Huanglongbing (Citrus Greening)",
        "is_healthy": False,
        "pathogen_type": "Bacterial (Candidatus Liberibacter asiaticus)",
        "severity": "High",
        "description": "One of the most catastrophic citrus diseases globally. Transmitted by the Asian Citrus Psyllid, it starves roots and produces bitter, misshapen, lopsided green fruit.",
        "symptoms": [
            "Asymmetric, blotchy yellow mottle on leaves (different pattern across the midrib)",
            "Yellow shoots appearing suddenly in an otherwise green tree canopy",
            "Small, lopsided, bitter fruit that stays green at the blossom end",
            "Dieback of feeder roots, twig mortality, and premature fruit drop"
        ],
        "causes": "Transmitted by the insect vector Diaphorina citri (Asian Citrus Psyllid) feeding on young flush and through infected budwood.",
        "prevention": [
            "Plant only certified disease-free nursery stock from screenhouses",
            "Aggressively scout and control Asian Citrus Psyllid populations using yellow sticky cards",
            "Immediately remove and eradicate infected trees to protect surrounding orchards"
        ],
        "treatment": {
            "biological": [
                "Release Tamarixia radiata parasitoid wasps to suppress psyllid populations",
                "Apply Horticultural Mineral Oils (2%) to deter psyllid egg laying"
            ],
            "chemical": [
                "Imidacloprid 17.8% SL @ 1 ml/L soil drench to control psyllid vectors",
                "Thiamethoxam 25% WG @ 0.5 g/L foliar spray during new shoot flush"
            ]
        }
    },
    "Peach___Bacterial_spot": {
        "crop": "Peach",
        "disease": "Bacterial Spot",
        "is_healthy": False,
        "pathogen_type": "Bacterial (Xanthomonas arboricola pv. pruni)",
        "severity": "High",
        "description": "Causes angular purple-black leaf spots, severe defoliation, and deep, sunken pitted craters on peach fruit.",
        "symptoms": [
            "Small, angular, water-soaked leaf spots turning dark purple-brown",
            "Centers of leaf spots drop out, producing a 'shot-hole' appearance",
            "Yellowing at the leaf tip leading to early leaf shedding",
            "Pitted, sunken, cracked gumming lesions on peach fruit skin"
        ],
        "causes": "Wind-driven rain, sand abrasion, and warm humid weather (20°C–30°C) enabling bacterial entry through stomata and leaf scars.",
        "prevention": [
            "Select resistant peach cultivars like Clayton, Candor, or Biscoe",
            "Plant windbreaks in sandy soils to minimize blowing sand wound abrasions",
            "Avoid heavy late-season nitrogen applications"
        ],
        "treatment": {
            "biological": [
                "Fixed copper hydroxide sprays during dormant bud swell",
                "Bacillus subtilis bio-fungicide during leaf emergence"
            ],
            "chemical": [
                "Oxytetracycline @ 2 g/L during bloom to shuck split",
                "Copper oxychloride 50% WP @ 2 g/L (dormant stage only to prevent phytotoxicity)"
            ]
        }
    },
    "Peach___healthy": {
        "crop": "Peach",
        "disease": "Healthy Plant Condition",
        "is_healthy": True,
        "pathogen_type": "None",
        "severity": "Low",
        "description": "Glossy, lanceolate peach leaves displaying uniform deep green hue with no shot-holes, leaf curl, or cankers.",
        "symptoms": [
            "Smooth, lanceolate leaves without puckering or perforations",
            "Uniform fruit set with clear, fuzzy skin",
            "Healthy terminal shoot growth"
        ],
        "causes": "Balanced winter pruning, dormant copper protection, and adequate drip irrigation.",
        "prevention": [
            "Maintain dormant spray schedule for peach leaf curl and shot hole",
            "Thin fruit clusters to maintain tree energy reserves"
        ],
        "treatment": {
            "biological": [],
            "chemical": []
        }
    },
    "Pepper,_bell___Bacterial_spot": {
        "crop": "Bell Pepper",
        "disease": "Bacterial Spot",
        "is_healthy": False,
        "pathogen_type": "Bacterial (Xanthomonas campestris pv. vesicatoria)",
        "severity": "High",
        "description": "A serious seed- and rain-borne bacterial disease producing dark, water-soaked leaf lesions, defoliation, and rough scabby fruit warts.",
        "symptoms": [
            "Small, circular to irregular water-soaked spots on leaf undersides",
            "Spots become necrotic, turning dark brown with pale halos",
            "Severe leaf drop exposing peppers to sun-scald",
            "Raised, blister-like corky brown scabs on bell pepper fruit"
        ],
        "causes": "Splashing overhead water, contaminated seed, and high temperatures (24°C–30°C) with persistent humidity.",
        "prevention": [
            "Use hot-water treated or certified disease-free bell pepper seed",
            "Practice 2-year crop rotation with non-solanaceous crops",
            "Use drip irrigation exclusively to keep foliage completely dry"
        ],
        "treatment": {
            "biological": [
                "Streptomyces lydicus bio-bactericide",
                "Copper octanoate organic soap spray @ 3 ml/L"
            ],
            "chemical": [
                "Copper Hydroxide 53.8% DF @ 2 g/L mixed with Mancozeb @ 2 g/L for synergistic control",
                "Kasugamycin 3% SL @ 2 ml/L"
            ]
        }
    },
    "Pepper,_bell___healthy": {
        "crop": "Bell Pepper",
        "disease": "Healthy Plant Condition",
        "is_healthy": True,
        "pathogen_type": "None",
        "severity": "Low",
        "description": "Dark green, glossy bell pepper foliage with strong branching, sturdy nodes, and complete absence of bacterial flecks.",
        "symptoms": [
            "Smooth, dark green ovate leaves without curling or spots",
            "Sturdy central stem with clean flowering nodes"
        ],
        "causes": "Healthy soil biology, balanced calcium supplementation, and drip fertigation.",
        "prevention": [
            "Maintain consistent soil moisture to prevent blossom end rot",
            "Scout weekly for thrips and aphids vectors"
        ],
        "treatment": {
            "biological": [],
            "chemical": []
        }
    },
    "Potato___Early_blight": {
        "crop": "Potato",
        "disease": "Early Blight",
        "is_healthy": False,
        "pathogen_type": "Fungal (Alternaria solani)",
        "severity": "Medium",
        "description": "Produces characteristic dark brown 'target-board' concentric rings on older lower leaves, progressively moving up the plant canopy.",
        "symptoms": [
            "Circular to irregular dark brown spots with prominent concentric rings (target board pattern)",
            "Yellow chlorotic halos surrounding lesions",
            "Lower leaves dry up, turn brown, and hang from the stem",
            "Sunken, dry, dark brown lesions on potato tubers"
        ],
        "causes": "Alternating periods of dry weather and dew/rain with temperatures of 24°C–29°C in nitrogen-deficient or senescing plants.",
        "prevention": [
            "Maintain adequate nitrogen and potassium fertility to keep foliage vigorous",
            "Rotate potato fields with cereals or legumes every 3 years",
            "Destroy potato volunteer plants and cull piles"
        ],
        "treatment": {
            "biological": [
                "Bacillus subtilis bio-fungicide @ 3 g/L",
                "Neem Seed Kernel Extract (5%) spray",
                "Trichoderma harzianum foliar application"
            ],
            "chemical": [
                "Chlorothalonil 75% WP @ 2 g/L as a protective cover spray",
                "Mancozeb 75% WP @ 2.5 g/L",
                "Difenoconazole 25% EC @ 1 ml/L applied at early lesion detection"
            ]
        }
    },
    "Potato___Late_blight": {
        "crop": "Potato",
        "disease": "Late Blight",
        "is_healthy": False,
        "pathogen_type": "Oomycete (Phytophthora infestans)",
        "severity": "High",
        "description": "The historic Irish famine pathogen. Extremely aggressive water mold that can turn an entire potato field into black rotting slime within 7–10 days.",
        "symptoms": [
            "Pale green to dark water-soaked lesions near leaf tips and margins",
            "Rapid expansion into large, purplish-black necrotic patches",
            "Delicate white cottony mold on the undersides of leaves during humid mornings",
            "Granular, reddish-brown dry rot extending into potato tubers beneath the skin"
        ],
        "causes": "Cool, overcast, wet weather with temperatures of 15°C–22°C and relative humidity above 90% for 10+ consecutive hours.",
        "prevention": [
            "Plant only certified disease-free seed tubers",
            "Hill up soil well over potato rows (15 cm) to prevent sporangia washing onto tubers",
            "Destroy haulms (vines) with desiccant 2 weeks before harvest"
        ],
        "treatment": {
            "biological": [
                "Copper oxychloride 50% WP @ 3 g/L early protective cover",
                "Pseudomonas fluorescens 0.5% @ 5 ml/L"
            ],
            "chemical": [
                "Metalaxyl 8% + Mancozeb 64% WP @ 2.5 g/L (Ridomil MZ)",
                "Cymoxanil 8% + Mancozeb 64% WP @ 2 g/L",
                "Dimethomorph 50% WP @ 1 g/L applied every 7 days during blight weather"
            ]
        }
    },
    "Potato___healthy": {
        "crop": "Potato",
        "disease": "Healthy Plant Condition",
        "is_healthy": True,
        "pathogen_type": "None",
        "severity": "Low",
        "description": "Vigorous potato foliage with compound emerald leaves, clean stem collars, and no concentric spots or mildew fuzz.",
        "symptoms": [
            "Dense, lush compound leaves with uniform green color",
            "Erect, thick succulent stems without blackleg or rot",
            "Abundant white flower clusters during tuber initiation"
        ],
        "causes": "Certified seed tuber usage, balanced hill hilling, and preventive fungicides during cool spells.",
        "prevention": [
            "Monitor weather forecasts for humidity and rain alerts",
            "Ensure ridge furrows drain effectively after heavy rainfall"
        ],
        "treatment": {
            "biological": [],
            "chemical": []
        }
    },
    "Raspberry___healthy": {
        "crop": "Raspberry",
        "disease": "Healthy Plant Condition",
        "is_healthy": True,
        "pathogen_type": "None",
        "severity": "Low",
        "description": "Healthy raspberry primocanes and floricanes displaying clean serrated leaves without cane blight, spur blight, or mosaic mottling.",
        "symptoms": [
            "Bright green serrated leaflets with pale undersides",
            "Smooth, prickled canes without brown nodal cankers",
            "Normal cane vigor and flowering clusters"
        ],
        "causes": "Trellising that promotes canopy aeration and regular removal of old spent floricanes.",
        "prevention": [
            "Cut out fruited floricanes at ground level immediately after harvest",
            "Maintain 30–45 cm cane row width to promote air circulation"
        ],
        "treatment": {
            "biological": [],
            "chemical": []
        }
    },
    "Soybean___healthy": {
        "crop": "Soybean",
        "disease": "Healthy Plant Condition",
        "is_healthy": True,
        "pathogen_type": "None",
        "severity": "Low",
        "description": "Healthy trifoliate soybean foliage with rich chlorophyll content, absence of rust pustules, and clean pod development.",
        "symptoms": [
            "Uniform trifoliate green leaves with soft pubescence",
            "No yellow mosaic mottling or powdery mildew patches",
            "Vigorous nodulation on primary taproot"
        ],
        "causes": "Rhizobium seed inoculation, good seedbed preparation, and optimal soil moisture.",
        "prevention": [
            "Practice crop rotation with corn or sorghum",
            "Scout for soybean rust during warm humid flowering stages"
        ],
        "treatment": {
            "biological": [],
            "chemical": []
        }
    },
    "Squash___Powdery_mildew": {
        "crop": "Squash",
        "disease": "Powdery Mildew",
        "is_healthy": False,
        "pathogen_type": "Fungal (Podosphaera xanthii)",
        "severity": "Medium",
        "description": "Forms dense white talcum-powder-like fungal coats over both sides of squash leaves, leading to chlorosis, leaf death, and reduced fruit size.",
        "symptoms": [
            "White talcum-powder-like circular spots expanding across leaves and stems",
            "Leaves turn yellow, then brown and dry like paper (sun-scorched appearance)",
            "Reduced fruit sweetness and premature fruit ripening with sun-scald"
        ],
        "causes": "High humidity at night followed by dry warm days (20°C–30°C) with dense shaded vine growth.",
        "prevention": [
            "Plant resistant squash varieties like Dunja or Success PM",
            "Provide ample vine spacing (1.5–2 meters) and use drip irrigation",
            "Plant in full sunlight with open air circulation"
        ],
        "treatment": {
            "biological": [
                "Potassium Bicarbonate @ 3 g/L organic foliar spray",
                "Neem oil 10,000 ppm @ 3 ml/L mixed with mild soap emulsifier",
                "Milk-water solution (40:60) sprayed in direct sunlight"
            ],
            "chemical": [
                "Azoxystrobin 23% SC @ 1 ml/L",
                "Myclobutanil 10% WP @ 0.5 g/L",
                "Wettable Sulfur 80% WP @ 2 g/L (avoid spraying above 32°C to prevent scorch)"
            ]
        }
    },
    "Strawberry___Leaf_scorch": {
        "crop": "Strawberry",
        "disease": "Leaf Scorch",
        "is_healthy": False,
        "pathogen_type": "Fungal (Diplocarpon earlianum)",
        "severity": "Medium",
        "description": "Produces numerous small, irregular dark purple to reddish blotches that coalesce, causing the entire leaf to curl upward and look scorched.",
        "symptoms": [
            "Small, irregular purple-red spots with no white center on upper leaf surfaces",
            "Spots merge turning the entire leaf brown, curled, and brittle",
            "Infected calyx leaves (fruit caps) turn brown, reducing berry commercial appeal",
            "Stunted plant vigor in multi-year strawberry beds"
        ],
        "causes": "Frequent rain, overhead irrigation, and prolonged leaf wetness at moderate temperatures (15°C–25°C).",
        "prevention": [
            "Plant on raised beds with straw mulch to prevent soil splashing",
            "Renovate strawberry beds after harvest by mowing old foliage and removing debris",
            "Select resistant cultivars such as Allstar, Earliglow, or Jewel"
        ],
        "treatment": {
            "biological": [
                "Copper octanoate (liquid copper soap) @ 3 ml/L",
                "Bacillus subtilis bio-fungicide @ 3 g/L"
            ],
            "chemical": [
                "Captan 50% WP @ 2.5 g/L",
                "Thiophanate-methyl 70% WP @ 1 g/L",
                "Pyraclostrobin + Boscalid @ 1 g/L"
            ]
        }
    },
    "Strawberry___healthy": {
        "crop": "Strawberry",
        "disease": "Healthy Plant Condition",
        "is_healthy": True,
        "pathogen_type": "None",
        "severity": "Low",
        "description": "Vibrant, trifoliate strawberry foliage with glossy green leaflets, clean serrations, and pristine calyx caps.",
        "symptoms": [
            "Vigorous trifoliate leaves without purple blotches or scorch",
            "Clean white blossoms and symmetrical bright red berry development",
            "Firm runners and healthy crown respiration"
        ],
        "causes": "Clean straw or black plastic mulch, drip irrigation, and timely renovation.",
        "prevention": [
            "Maintain crown aeration above the soil surface level",
            "Scout for two-spotted spider mites in hot dry periods"
        ],
        "treatment": {
            "biological": [],
            "chemical": []
        }
    },
    "Tomato___Bacterial_spot": {
        "crop": "Tomato",
        "disease": "Bacterial Spot",
        "is_healthy": False,
        "pathogen_type": "Bacterial (Xanthomonas perforans)",
        "severity": "High",
        "description": "An aggressive bacterial disease causing small, circular, greasy spots on leaves, extensive defoliation, and scabby raised warts on tomato fruit.",
        "symptoms": [
            "Small (less than 3 mm), dark, greasy circular spots on leaves and stems",
            "Spots turn brown, with translucent centers that occasionally drop out",
            "Blister-like, raised, scabby dark brown spots on green tomato fruit",
            "Extensive lower leaf defoliation exposing fruit to sun-scald"
        ],
        "causes": "Warm temperatures (24°C–30°C) combined with splashing rain, overhead irrigation, and handling wet plants.",
        "prevention": [
            "Use certified pathogen-free seeds treated with hot water (50°C for 25 mins)",
            "Do not work in tomato fields when foliage is wet from dew or rain",
            "Practice 2- to 3-year crop rotation away from solanaceous crops"
        ],
        "treatment": {
            "biological": [
                "Bacteriophage bio-control tailored to Xanthomonas",
                "Liquid Copper octanoate @ 3 ml/L"
            ],
            "chemical": [
                "Copper Hydroxide 53.8% DF @ 2 g/L mixed with Mancozeb 75% WP @ 2 g/L",
                "Kasugamycin 3% SL @ 2 ml/L during early vegetative development"
            ]
        }
    },
    "Tomato___Early_blight": {
        "crop": "Tomato",
        "disease": "Early Blight",
        "is_healthy": False,
        "pathogen_type": "Fungal (Alternaria solani)",
        "severity": "Medium",
        "description": "Causes dark brown to black spots with concentric rings (target pattern) starting on the oldest lower leaves and progressing upwards.",
        "symptoms": [
            "Concentric rings ('bullseye' or 'target board' pattern) inside dark brown leaf lesions",
            "Yellow halo surrounding expanding lesions",
            "Stem cankers: dark, slightly sunken concentric lesions at soil line (collar rot)",
            "Sunken leathery black lesions near the fruit stem end"
        ],
        "causes": "High humidity, heavy dews, and warm temperatures (24°C–29°C), especially in plants stressed by heavy fruit loads.",
        "prevention": [
            "Mulch around tomato stems with straw or plastic to stop soil splashing",
            "Prune bottom 30 cm of foliage to prevent contact with damp soil",
            "Stake and cage plants to promote rapid drying"
        ],
        "treatment": {
            "biological": [
                "Trichoderma harzianum @ 5 g/L foliar spray",
                "Bacillus subtilis @ 3 g/L",
                "5% Neem Seed Kernel Extract (NSKE) spray"
            ],
            "chemical": [
                "Chlorothalonil 75% WP @ 2 g/L",
                "Mancozeb 75% WP @ 2.5 g/L",
                "Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 1 ml/L"
            ]
        }
    },
    "Tomato___Late_blight": {
        "crop": "Tomato",
        "disease": "Late Blight",
        "is_healthy": False,
        "pathogen_type": "Oomycete (Phytophthora infestans)",
        "severity": "High",
        "description": "Extremely fast-moving water mold disease that causes large greasy dark brown patches on leaves, white cottony mold, and rotten greasy fruit.",
        "symptoms": [
            "Large, irregular, water-soaked greenish-black lesions on leaves and stems",
            "Delicate white fuzzy fungal sporulation on undersides of leaves during humid mornings",
            "Large, firm, greasy brown lesions with golden-bronze marbling on green fruit",
            "Rapid canopy collapse smelling of foul rotting vegetation"
        ],
        "causes": "Cool, persistently damp weather with night temperatures of 10°C–18°C and day temperatures of 15°C–22°C with 90%+ relative humidity.",
        "prevention": [
            "Select late-blight resistant tomato hybrids (e.g., Mountain Magic, Defiant, Jasper)",
            "Avoid planting near potato fields or cull piles",
            "Destroy and bag infected plants immediately—never compost late blight tissue"
        ],
        "treatment": {
            "biological": [
                "Copper oxychloride 50% WP @ 3 g/L as a protective barrier"
            ],
            "chemical": [
                "Cymoxanil 8% + Mancozeb 64% WP @ 2 g/L (Curzate M8)",
                "Metalaxyl-M 4% + Mancozeb 64% WP @ 2.5 g/L (Ridomil Gold)",
                "Dimethomorph 50% WP @ 1 g/L with non-ionic surfactant"
            ]
        }
    },
    "Tomato___Leaf_Mold": {
        "crop": "Tomato",
        "disease": "Leaf Mold",
        "is_healthy": False,
        "pathogen_type": "Fungal (Passalora fulva / Cladosporium fulvum)",
        "severity": "Medium",
        "description": "Primarily a greenhouse and polytunnel disease, producing pale yellow spots on the upper leaf surface and olive-green velvety mold on the underside.",
        "symptoms": [
            "Diffuse pale yellow to light green spots on upper leaf surfaces",
            "Plush, olive-green to grayish-brown velvety mold on corresponding leaf undersides",
            "Leaves turn completely yellow, wither, and drop prematurely"
        ],
        "causes": "Extremely high relative humidity (above 85%) and warm temperatures (20°C–26°C) common in poorly ventilated tunnels.",
        "prevention": [
            "Ventilate high tunnels and greenhouses to keep humidity strictly below 80%",
            "Space plants widely and prune suckers to allow free horizontal airflow",
            "Use drip irrigation and avoid wetting tomato foliage"
        ],
        "treatment": {
            "biological": [
                "Bacillus amyloliquefaciens bio-fungicide @ 3 g/L",
                "Copper hydroxide @ 2 g/L"
            ],
            "chemical": [
                "Chlorothalonil 75% WP @ 2 g/L",
                "Difenoconazole 25% EC @ 1 ml/L",
                "Boscalid + Pyraclostrobin @ 1 g/L"
            ]
        }
    },
    "Tomato___Septoria_leaf_spot": {
        "crop": "Tomato",
        "disease": "Septoria Leaf Spot",
        "is_healthy": False,
        "pathogen_type": "Fungal (Septoria lycopersici)",
        "severity": "Medium",
        "description": "Causes numerous small, circular water-soaked spots with dark brown margins and gray centers containing tiny black specks (pycnidia).",
        "symptoms": [
            "Tiny circular spots (1.5 to 3 mm) with dark brown borders and light gray centers",
            "Minute black specks (fruiting bodies) clearly visible inside gray lesion centers",
            "Severe yellowing of tissue between spots, causing bottom-up defoliation",
            "Fruit is rarely infected, but defoliation leads to severe sun-scald"
        ],
        "causes": "Overhead splashing water, high humidity, and temperatures between 20°C and 25°C.",
        "prevention": [
            "Clean mulch around plants to cover soil-borne fungal spores",
            "Strip bottom leaves 30 cm above soil line",
            "Rotate tomato ground for at least 2 consecutive years"
        ],
        "treatment": {
            "biological": [
                "Copper soap (Copper octanoate) @ 3 ml/L",
                "Bio-protective Bacillus subtilis foliar spray"
            ],
            "chemical": [
                "Chlorothalonil 75% WP @ 2 g/L every 7–10 days",
                "Mancozeb 75% WP @ 2.5 g/L",
                "Azoxystrobin 23% SC @ 1 ml/L"
            ]
        }
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "crop": "Tomato",
        "disease": "Two-Spotted Spider Mite Infestation",
        "is_healthy": False,
        "pathogen_type": "Pest / Acarid (Tetranychus urticae)",
        "severity": "Medium",
        "description": "Microscopic sap-sucking arachnids that feed on leaf cells, creating yellow stippling, bronzing, and dense webbing on the canopy.",
        "symptoms": [
            "Fine yellow to white speckled stippling on upper leaf surfaces",
            "Leaves turn bronze, yellow, and brittle under heavy feeding",
            "Fine silky webbing covering shoot tips, flowers, and leaf undersides",
            "Tiny moving red/yellow specks visible with a 10x hand lens"
        ],
        "causes": "Hot, dry, dusty weather (>28°C and low humidity <40%) accelerates mite reproduction from egg to adult in under 5 days.",
        "prevention": [
            "Keep farm roads and field perimeters watered to minimize dust clouds",
            "Avoid broad-spectrum pyrethroid insecticides which wipe out natural predatory mites",
            "Spray plants with clean water to wash dust from leaf undersides"
        ],
        "treatment": {
            "biological": [
                "Release predatory mites (*Phytoseiulus persimilis* or *Neoseiulus californicus*)",
                "Neem oil 10,000 ppm @ 3 ml/L targeting the undersides of leaves",
                "Insecticidal soap (potassium salts of fatty acids) @ 5 ml/L"
            ],
            "chemical": [
                "Spiromesifen 22.9% SC @ 1 ml/L",
                "Abamectin 1.9% EC @ 0.5 ml/L",
                "Fenpyroximate 5% EC @ 1 ml/L"
            ]
        }
    },
    "Tomato___Target_Spot": {
        "crop": "Tomato",
        "disease": "Target Spot",
        "is_healthy": False,
        "pathogen_type": "Fungal (Corynespora cassiicola)",
        "severity": "Medium",
        "description": "Causes circular brown lesions with light brown centers and faint concentric rings on leaves, stems, and sunken pits on fruit.",
        "symptoms": [
            "Circular brown lesions with light centers and distinct darker concentric rings",
            "Pitted, sunken brown lesions on ripening tomato fruit",
            "Upper and lower canopy blighting leading to defoliation"
        ],
        "causes": "Warm, humid tropical and sub-tropical environments (25°C–32°C) with persistent leaf wetness.",
        "prevention": [
            "Provide wide plant spacing to improve canopy dry-down time",
            "Remove all old solanaceous and cucurbit crop debris",
            "Use plastic mulch"
        ],
        "treatment": {
            "biological": [
                "Bacillus subtilis @ 3 g/L",
                "Copper oxychloride 50% WP @ 2.5 g/L"
            ],
            "chemical": [
                "Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 1 ml/L",
                "Chlorothalonil 75% WP @ 2 g/L",
                "Fluxapyroxad + Pyraclostrobin @ 0.5 ml/L"
            ]
        }
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "crop": "Tomato",
        "disease": "Tomato Yellow Leaf Curl Virus (TYLCV)",
        "is_healthy": False,
        "pathogen_type": "Viral (Begomovirus transmitted by Whiteflies)",
        "severity": "High",
        "description": "Devastating viral disease transmitted by Bemisia tabaci whiteflies. Causes severe stunting, erect cupped yellow leaves, and total blossom drop.",
        "symptoms": [
            "Upward curling and cupping of leaflet margins",
            "Interveinal chlorosis and intense yellowing of young leaves",
            "Extreme plant stunting with shortened internodes giving a bushy appearance",
            "Total flower abortion resulting in near-zero fruit set"
        ],
        "causes": "Transmitted in a persistent manner by Bemisia tabaci (Sweetpotato Whitefly); virus cannot be transmitted mechanically through pruning tools.",
        "prevention": [
            "Plant TYLCV-resistant hybrid cultivars (Ty-1, Ty-3 genes)",
            "Install 50-mesh insect-proof netting in nurseries and high tunnels",
            "Install yellow sticky cards @ 15–20 cards/acre to monitor whitefly influx"
        ],
        "treatment": {
            "biological": [
                "Spray Neem oil 10,000 ppm @ 3 ml/L to disrupt whitefly feeding and egg hatching",
                "Release Encarsia formosa parasitoids in greenhouses",
                "Spray Lecanicillium lecanii entomopathogenic fungus @ 5 g/L"
            ],
            "chemical": [
                "Diafenthiuron 50% WP @ 1.2 g/L to knock down adult whiteflies",
                "Pyriproxyfen 10% + Clothianidin 10% EC @ 1 ml/L",
                "Dinotefuran 20% SG @ 0.5 g/L systemic root drench"
            ]
        }
    },
    "Tomato___Tomato_mosaic_virus": {
        "crop": "Tomato",
        "disease": "Tomato Mosaic Virus (ToMV)",
        "is_healthy": False,
        "pathogen_type": "Viral (Tobamovirus)",
        "severity": "High",
        "description": "An extremely stable, mechanically transmitted tobamovirus causing alternating light and dark green mosaic mottling, distorted leaves, and internal fruit browning.",
        "symptoms": [
            "Light green and dark green mosaic mottling pattern on leaves",
            "Distorted, blistered, or narrow 'shoestring' fern-like leaves",
            "Uneven fruit ripening with internal brown vascular necrosis",
            "Stunted plant height with reduced leaf area"
        ],
        "causes": "Mechanically transmitted through handling, pruning tools, worker clothing, contaminated seed coats, and tobacco products. Survives in dry plant debris for years.",
        "prevention": [
            "Disinfect hands and pruning shears in 20% non-fat dry milk solution or 10% trisodium phosphate (TSP)",
            "Strictly prohibit tobacco smoking or handling near tomato greenhouses",
            "Plant resistant tomato varieties with Tm-2 or Tm-2^2 resistance alleles"
        ],
        "treatment": {
            "biological": [
                "Rogue out and destroy infected plants immediately upon mosaic confirmation",
                "Spray skimmed milk solution (10%) on seedlings to reduce mechanical viral transmission"
            ],
            "chemical": [
                "No virucide exists for plant viruses; management focuses on sanitation and eradication of infected stock"
            ]
        }
    },
    "Tomato___healthy": {
        "crop": "Tomato",
        "disease": "Healthy Plant Condition",
        "is_healthy": True,
        "pathogen_type": "None",
        "severity": "Low",
        "description": "Deep green, robust tomato foliage with aromatic glandular trichomes, sturdy branching, and pristine blossoming clusters.",
        "symptoms": [
            "Lush compound pinnate leaves without mottling, stippling, or concentric spots",
            "Sturdy main stem with active indeterminate vegetative shoots",
            "Clean yellow flowers with uniform fruit setting"
        ],
        "causes": "Balanced calcium-potassium fertigation, bottom-leaf pruning, and drip irrigation under plastic mulch.",
        "prevention": [
            "Maintain soil calcium levels to prevent blossom end rot",
            "Scout weekly for hornworms and whiteflies"
        ],
        "treatment": {
            "biological": [],
            "chemical": []
        }
    }
}

CLASS_NAMES = list(DISEASE_KNOWLEDGE_BASE.keys())

def get_disease_info(class_label: str) -> dict:
    """
    Returns disease and agronomic information for the given PlantVillage class label.
    Falls back to a structured default if an unmapped class is passed.
    """
    if class_label in DISEASE_KNOWLEDGE_BASE:
        return DISEASE_KNOWLEDGE_BASE[class_label]

    parts = class_label.split("___") if "___" in class_label else [class_label, "General Condition"]
    crop = parts[0].replace("_", " ").strip()
    disease = parts[1].replace("_", " ").strip() if len(parts) > 1 else "Unknown Condition"
    is_healthy = "healthy" in disease.lower()

    return {
        "crop": crop,
        "disease": disease,
        "is_healthy": is_healthy,
        "pathogen_type": "Unknown",
        "severity": "Low" if is_healthy else "Medium",
        "description": f"{crop} plant exhibiting signs consistent with {disease}." if not is_healthy else f"Healthy {crop} plant.",
        "symptoms": ["General leaf discoloration or unclassified foliar response"] if not is_healthy else ["Uniform green leaf tissue"],
        "causes": "Environmental stress, nutritional imbalance, or uncharacterized foliar pathogen.",
        "prevention": [
            "Ensure proper crop spacing and weed control",
            "Maintain balanced fertilization based on soil testing",
            "Use certified seed and clean nursery practices"
        ],
        "treatment": {
            "biological": ["Apply broad-spectrum bio-fungicide (Trichoderma / Bacillus subtilis)"],
            "chemical": ["Consult local agricultural extension office (KVK) for regional chemical guidelines"]
        }
    }
