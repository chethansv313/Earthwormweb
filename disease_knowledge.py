"""
disease_knowledge.py
--------------------
Complete Agronomic Knowledge Base mapped to your exact local dataset directories.
Provides clean display titles, biological causes, and recommended treatments.
"""

import re

DISEASE_KNOWLEDGE = {
    # =========================================================================
    # 1. APPLE (D:/major project/apple/train)
    # =========================================================================
    "apple_apple_scab": {
        "name": "Apple Scab",
        "cause": (
            "Fungus (Venturia inaequalis). Spores overwinter in fallen leaves"
            " and spread during cool, wet spring conditions."
        ),
        "treatment": (
            "Apply Captan, Mancozeb, or Myclobutanil at green tip and petal"
            " fall. Rake and destroy fallen leaves in autumn."
        ),
    },
    "apple_black_rot": {
        "name": "Apple Black Rot (Frogeye Spot)",
        "cause": (
            "Fungus (Botryosphaeria obtusa). Enters via pruning cuts, leaf"
            " wounds, and fruit injuries."
        ),
        "treatment": (
            "Prune out dead wood, cankers, and mummified fruit. Apply"
            " copper-based fungicides or Captan early in the season."
        ),
    },
    "apple_cedar_apple_rust": {
        "name": "Cedar Apple Rust",
        "cause": (
            "Fungus (Gymnosporangium juniperi-virginianae). Requires nearby"
            " juniper/cedar trees to complete its life cycle."
        ),
        "treatment": (
            "Remove galls from nearby junipers. Apply Myclobutanil or Mancozeb"
            " when flower buds show pink."
        ),
    },
    # =========================================================================
    # 2. CORN (D:/major project/corn/train)
    # =========================================================================
    "corn_cercospora_leaf_spot": {
        "name": "Corn Gray Leaf Spot",
        "cause": (
            "Fungus (Cercospora zeae-maydis). Survives in soil debris and"
            " thrives in warm, highly humid conditions."
        ),
        "treatment": (
            "Rotate crops with legumes, bury crop residue, and apply"
            " strobilurin or triazole fungicides at VT-R1 stage."
        ),
    },
    "corn_common_rust": {
        "name": "Corn Common Rust",
        "cause": (
            "Fungus (Puccinia sorghi). Wind-borne spores flourish during"
            " moderate temperatures (16–25°C) and high humidity."
        ),
        "treatment": (
            "Plant rust-resistant hybrids. Apply Azoxystrobin or Pyraclostrobin"
            " if pustules appear before tasseling."
        ),
    },
    "corn_northern_leaf_blight": {
        "name": "Northern Corn Leaf Blight",
        "cause": (
            "Fungus (Exserohilum turcicum). Causes long, cigar-shaped grayish"
            " lesions during wet periods."
        ),
        "treatment": (
            "Use resistant hybrids, practice 2-year crop rotation, and spray"
            " Propiconazole upon first sign of lesions."
        ),
    },
    # =========================================================================
    # 3. COTTON (D:/major project/cotton/cotton_processed/train)
    # =========================================================================
    "cotton_bacterial_blight": {
        "name": "Cotton Bacterial Blight",
        "cause": (
            "Bacterium (Xanthomonas citri pv. malvacearum). Spreads through rain"
            " splash and infected seeds."
        ),
        "treatment": (
            "Use acid-delinted certified seeds. Spray Copper Oxychloride (0.25%)"
            " mixed with Streptocycline (100 ppm)."
        ),
    },
    "cotton_curl_virus": {
        "name": "Cotton Leaf Curl Virus",
        "cause": (
            "Begomovirus complex transmitted by the Silverleaf Whitefly"
            " (Bemisia tabaci)."
        ),
        "treatment": (
            "Control whitefly vectors using Diafenthiuron or Imidacloprid (0.3"
            " ml/L). Eradicate host weeds around field borders."
        ),
    },
    "cotton_herbicide_growth_damage": {
        "name": "Cotton Herbicide Damage",
        "cause": (
            "Non-pathogenic chemical injury caused by 2,4-D drift, accidental"
            " glyphosate contact, or sprayer contamination."
        ),
        "treatment": (
            "Flush fields with fresh water. Apply foliar bio-stimulants and"
            " balanced micro-nutrients (Zinc + Boron) to assist plant recovery."
        ),
    },
    "cotton_leaf_hopper_jassids": {
        "name": "Cotton Leafhopper / Jassids",
        "cause": (
            "Insect pest (Amrasca biguttula). Nymphs and adults suck sap from"
            " leaf undersides, causing hopper burn."
        ),
        "treatment": (
            "Spray Flonicamid 50 WG (0.4 g/L) or Thiamethoxam 25 WG (0.2 g/L)"
            " upon noticing leaf curling."
        ),
    },
    "cotton_leaf_redding": {
        "name": "Cotton Leaf Reddening",
        "cause": (
            "Physiological disorder triggered by magnesium/nitrogen"
            " deficiency, cold night temperatures, or waterlogging."
        ),
        "treatment": (
            "Foliar spray of 1% Magnesium Sulfate (MgSO4) + 1% Urea at 15-day"
            " intervals during boll development."
        ),
    },
    "cotton_leaf_variegation": {
        "name": "Cotton Leaf Variegation",
        "cause": (
            "Genetic mutation or physiological chimera causing chlorophyll"
            " loss in irregular leaf patches."
        ),
        "treatment": (
            "No chemical treatment required. Ensure adequate nitrogen and zinc"
            " nutrition to support overall vegetative vigor."
        ),
    },
    # =========================================================================
    # 4. GRAPE (D:/major project/grape/train)
    # =========================================================================
    "grape_black_rot": {
        "name": "Grape Black Rot",
        "cause": (
            "Fungus (Guignardia bidwellii). Overwinters in mummified berries"
            " and spreads in warm, wet weather."
        ),
        "treatment": (
            "Spray Mancozeb, Captan, or Myclobutanil starting from early bud"
            " break until 4 weeks after bloom."
        ),
    },
    "grape_esca": {
        "name": "Grape Esca (Black Measles)",
        "cause": (
            "Complex of wood-decay fungi (Phaeomoniella chlamydospora and"
            " Fomitiporia mediterranea)."
        ),
        "treatment": (
            "Disinfect pruning shears, seal cut wounds with wound paint, and"
            " remove dead infected wood."
        ),
    },
    "grape_leaf_blight": {
        "name": "Grape Leaf Blight (Isariopsis)",
        "cause": (
            "Fungus (Pseudocercospora cladosporioides). Attacks leaves in late"
            " season under warm, humid conditions."
        ),
        "treatment": (
            "Apply Copper Hydroxide or Mancozeb post-bloom. Maintain open canopy"
            " trellising for rapid leaf drying."
        ),
    },
    # =========================================================================
    # 5. ONION (D:/major project/onion/onion_processed/train)
    # =========================================================================
    "onion_alternaria": {
        "name": "Onion Purple Blotch (Alternaria)",
        "cause": (
            "Fungus (Alternaria porri). Enters through thrips wounds during warm"
            " and wet conditions."
        ),
        "treatment": (
            "Spray Difenoconazole (1 ml/L) or Mancozeb (2.5 g/L) with a"
            " sticker/spreader. Control thrips promptly."
        ),
    },
    "onion_botrytis_leaf_blight": {
        "name": "Onion Botrytis Leaf Blight",
        "cause": (
            "Fungus (Botrytis squamosa). Causes small white necrotic spots with"
            " greenish halos during cool, damp weather."
        ),
        "treatment": (
            "Apply Iprodione, Chlorothalonil, or Boscalid. Avoid high-density"
            " planting to maintain canopy airflow."
        ),
    },
    "onion_bulb_rot": {
        "name": "Onion Bulb Rot",
        "cause": (
            "Fungal/bacterial rot complex (Fusarium / Pectobacterium) entering"
            " bulbs in waterlogged soils."
        ),
        "treatment": (
            "Improve soil drainage, practice 3-year crop rotation, and cure"
            " harvested bulbs in a dry, ventilated area."
        ),
    },
    "onion_bulb_blight": {
        "name": "Onion Bulb Blight",
        "cause": (
            "Soil-borne fungal pathogen (Stemphylium vesicarium) attacking"
            " dying leaf tips and moving to bulb necks."
        ),
        "treatment": (
            "Foliar spray of Azoxystrobin + Difenoconazole. Ensure fields are not"
            " over-irrigated near maturity."
        ),
    },
    "onion_caterpillar": {
        "name": "Onion Caterpillar / Cutworm",
        "cause": (
            "Larvae of Spodoptera exigua / Spodoptera litura feeding on hollow"
            " onion foliage."
        ),
        "treatment": (
            "Spray Emamectin Benzoate 5% SG (0.4 g/L) or Chlorantraniliprole (0.3"
            " ml/L) during early evening."
        ),
    },
    "onion_downy_mildew": {
        "name": "Onion Downy Mildew",
        "cause": (
            "Oomycete (Peronospora destructor). Spreads rapidly during cool,"
            " humid nights and misty mornings."
        ),
        "treatment": (
            "Apply Metalaxyl-Mancozeb (2 g/L) or Cymoxanil. Avoid overhead"
            " sprinkler irrigation."
        ),
    },
    "onion_fusarium": {
        "name": "Onion Fusarium Basal Rot",
        "cause": (
            "Fungus (Fusarium oxysporum f. sp. cepae). Attacks roots and bulb"
            " basal plate."
        ),
        "treatment": (
            "Treat seeds/sets with Trichoderma viride or Carbendazim (2 g/kg)."
            " Practice a 4-year crop rotation."
        ),
    },
    "onion_iris_yellow_virus": {
        "name": "Onion Iris Yellow Spot Virus",
        "cause": (
            "Tospovirus transmitted exclusively by Onion Thrips (Thrips"
            " tabaci)."
        ),
        "treatment": (
            "Manage thrips using Spinosad (0.3 ml/L) or Fipronil. Remove weed"
            " hosts from field boundaries."
        ),
    },
    # =========================================================================
    # 6. POTATO (D:/major project/potato/train)
    # =========================================================================
    "potato_early_blight": {
        "name": "Potato Early Blight",
        "cause": (
            "Fungus (Alternaria solani). Concentric brown target rings on older"
            " leaves."
        ),
        "treatment": (
            "Apply Chlorothalonil or Azoxystrobin. Maintain optimal balanced"
            " nitrogen fertilization."
        ),
    },
    "potato_late_blight": {
        "name": "Potato Late Blight",
        "cause": (
            "Oomycete (Phytophthora infestans). Rapid rot in cold, humid"
            " weather (<20°C, >90% RH)."
        ),
        "treatment": (
            "Spray systemic fungicides immediately: Dimethomorph or Cymoxanil +"
            " Mancozeb."
        ),
    },
    # =========================================================================
    # 7. RICE (D:/major project/rice/train)
    # =========================================================================
    "rice_bacterialblight": {
        "name": "Rice Bacterial Leaf Blight",
        "cause": (
            "Bacterium (Xanthomonas oryzae pv. oryzae). Enters via leaf tips and"
            " wounds after wind/rain."
        ),
        "treatment": (
            "Drain field water for 3 days. Avoid excess nitrogen. Spray Copper"
            " Hydroxide (2 g/L) + Streptocycline (0.1 g/L)."
        ),
    },
    "rice_blast": {
        "name": "Rice Leaf Blast",
        "cause": (
            "Fungus (Magnaporthe oryzae). Spindle-shaped lesions with gray"
            " centers during cloudy, humid weather."
        ),
        "treatment": (
            "Apply Tricyclazole 75% WP (0.6 g/L) or Isoprothiolane (1.5 ml/L)"
            " at tillering and heading."
        ),
    },
    "rice_brownspot": {
        "name": "Rice Brown Spot",
        "cause": (
            "Fungus (Bipolaris oryzae). Common in soils with nutrient"
            " deficiencies or moisture stress."
        ),
        "treatment": (
            "Apply balanced NPK + Zinc. Spray Propiconazole (1 ml/L) or"
            " Mancozeb (2 g/L)."
        ),
    },
    "rice_tungro": {
        "name": "Rice Tungro Virus",
        "cause": (
            "Viral complex transmitted by the Green Leafhopper (Nephotettix"
            " virescens)."
        ),
        "treatment": (
            "Apply Dinotefuran or Imidacloprid to control leafhoppers. Uproot"
            " and destroy severely stunted yellow clumps."
        ),
    },
    # =========================================================================
    # 8. SUGARCANE (D:/major project/sugarcane/sugarcane_processed/train)
    # =========================================================================
    "sugarcane_bacterialblights": {
        "name": "Sugarcane Bacterial Blight",
        "cause": (
            "Bacterium (Acidovorax avenae). Causes leaf stripe necrosis and"
            " top rot."
        ),
        "treatment": (
            "Use certified clean seed sets. Spray Copper Oxychloride (0.25%)"
            " during early tillering."
        ),
    },
    "sugarcane_mosaic": {
        "name": "Sugarcane Mosaic Virus",
        "cause": (
            "Potyvirus transmitted by aphids (Rhopalosiphum maidis) causing"
            " green and yellow leaf mottling."
        ),
        "treatment": (
            "Plant mosaic-resistant varieties. Use healthy setts and spray Neem"
            " oil or Acetamiprid to suppress aphid vectors."
        ),
    },
    "sugarcane_redrot": {
        "name": "Sugarcane Red Rot",
        "cause": (
            "Fungus (Colletotrichum falcatum). Internal stem reddening with"
            " crosswise white patches and midrib spots."
        ),
        "treatment": (
            "Use hot-water treated setts (50°C for 30 mins) with Carbendazim"
            " (0.1%). Uproot and burn infected clumps."
        ),
    },
    "sugarcane_rust": {
        "name": "Sugarcane Rust",
        "cause": (
            "Fungus (Puccinia melanocephala). Orange-brown elongated pustules"
            " on both leaf surfaces."
        ),
        "treatment": (
            "Apply Mancozeb (2 g/L) or Propiconazole (1 ml/L) at first symptom"
            " appearance."
        ),
    },
    "sugarcane_yellow": {
        "name": "Sugarcane Yellow Leaf Disease",
        "cause": (
            "Sugarcane Yellow Leaf Virus (SCYLV) transmitted by the Sugarcane"
            " Aphid (Melanaphis sacchari)."
        ),
        "treatment": (
            "Ensure proper irrigation to prevent stress. Spray systemic"
            " insecticides for aphid control."
        ),
    },
    # =========================================================================
    # 9. TOMATO (D:/major project/tomato/trained)
    # =========================================================================
    "tomato_bacterial_spot": {
        "name": "Tomato Bacterial Spot",
        "cause": (
            "Bacterium (Xanthomonas spp.). Spreads through overhead water"
            " splash and tools."
        ),
        "treatment": (
            "Apply Copper Hydroxide mixed with Mancozeb. Avoid overhead"
            " irrigation."
        ),
    },
    "tomato_early_blight": {
        "name": "Tomato Early Blight",
        "cause": (
            "Fungus (Alternaria solani). Dark brown concentric target lesions"
            " starting from lower foliage."
        ),
        "treatment": (
            "Prune bottom leaves touching the soil. Apply Chlorothalonil or"
            " Difenoconazole every 10 days."
        ),
    },
    "tomato_late_blight": {
        "name": "Tomato Late Blight",
        "cause": (
            "Oomycete (Phytophthora infestans). Rapidly rots leaves and green"
            " fruits with water-soaked margins."
        ),
        "treatment": (
            "Apply Metalaxyl + Mancozeb or Fenamidone immediately. Remove"
            " infected plants."
        ),
    },
    "tomato_leaf_mold": {
        "name": "Tomato Leaf Mold",
        "cause": (
            "Fungus (Passalora fulva). High relative humidity (>85%) in"
            " greenhouses."
        ),
        "treatment": (
            "Improve air circulation and ventilation. Spray Copper fungicides"
            " or Azoxystrobin."
        ),
    },
    "tomato_septoria_leaf_spot": {
        "name": "Tomato Septoria Leaf Spot",
        "cause": (
            "Fungus (Septoria lycopersici). Small circular spots with dark"
            " borders and tiny black specks."
        ),
        "treatment": (
            "Mulch base of plants to prevent soil splashing. Spray Mancozeb or"
            " Chlorothalonil."
        ),
    },
    "tomato_spider_mites": {
        "name": "Tomato Two-Spotted Spider Mites",
        "cause": (
            "Pest (Tetranychus urticae). Causes fine leaf stippling,"
            " yellowing, and webbing under hot, dry conditions."
        ),
        "treatment": (
            "Spray Abamectin (0.5 ml/L) or Spiromesifen (1 ml/L). Ensure"
            " thorough coverage of leaf undersides."
        ),
    },
    "tomato_target_spot": {
        "name": "Tomato Target Spot",
        "cause": (
            "Fungus (Corynespora cassiicola). Brown necrotic lesions with light"
            " brown centers on foliage."
        ),
        "treatment": (
            "Apply Azoxystrobin or Fluxapyroxad. Avoid prolonged leaf wetness."
        ),
    },
    "tomato_mosaic_virus": {
        "name": "Tomato Mosaic Virus (ToMV)",
        "cause": (
            "Tobamovirus transmitted mechanically via hands, shears, and"
            " infected seeds."
        ),
        "treatment": (
            "Wash hands and tools in 20% non-fat milk solution. Remove and"
            " destroy infected plants immediately."
        ),
    },
    "tomato_yellow_leaf_curl_virus": {
        "name": "Tomato Yellow Leaf Curl Virus (TYLCV)",
        "cause": (
            "Begomovirus transmitted by Silverleaf Whiteflies (Bemisia tabaci)."
        ),
        "treatment": (
            "Install yellow sticky cards. Spray Acetamiprid or Neem oil (3%) to"
            " control whiteflies."
        ),
    },
    # =========================================================================
    # 10. WHEAT (D:/major project/wheat/archive (1)/Wheat Leaf Disease/train)
    # =========================================================================
    "wheat_blackpoint": {
        "name": "Wheat Black Point",
        "cause": (
            "Fungal complex (Bipolaris sorokiniana / Alternaria alternata)"
            " discolouring embryo ends during humid grain-fill."
        ),
        "treatment": (
            "Apply Propiconazole at flag leaf / heading stage. Avoid excessive"
            " irrigation during grain filling."
        ),
    },
    "wheat_fusariumfootrot": {
        "name": "Wheat Fusarium Foot Rot / Head Blight",
        "cause": (
            "Fungus (Fusarium graminearum). Causes crown browning, root rot,"
            " and bleached spikelets."
        ),
        "treatment": (
            "Treat seed with Tebuconazole (1.5 g/kg). Practice non-cereal crop"
            " rotation."
        ),
    },
    "wheat_leafblight": {
        "name": "Wheat Leaf Blight (Septoria)",
        "cause": (
            "Fungus (Zymoseptoria tritici / Pyrenophora tritici-repentis)"
            " causing irregular necrotic leaf spots."
        ),
        "treatment": (
            "Apply Propiconazole or Azoxystrobin at flag leaf emergence (GS"
            " 39)."
        ),
    },
    "wheat_wheatblast": {
        "name": "Wheat Blast",
        "cause": (
            "Fungus (Magnaporthe oryzae Triticum pathotype). Bleaches spikelets"
            " and causes elliptical foliar lesions."
        ),
        "treatment": (
            "Apply Tebuconazole + Trifloxystrobin at heading stage."
            " Implement strict quarantine of infected seeds."
        ),
    },
    # =========================================================================
    # GENERAL HEALTHY TISSUE
    # =========================================================================
    "healthy": {
        "name": "Healthy Plant Tissue",
        "cause": (
            "No active fungal, bacterial, or viral pathogens detected. The"
            " foliage displays healthy chlorophyll and vigor."
        ),
        "treatment": (
            "Maintain balanced NPK fertigation, periodic field scouting, and"
            " preventive neem oil sprays."
        ),
    },
}


def get_disease_details(crop_name, raw_str):
  """Matches any folder name from the dataset and returns:

  (Clean Display Title, Biological Cause, Recommended Treatment)
  """
  clean_key = (
      raw_str.lower()
      .replace("___", "_")
      .replace("__", "_")
      .replace(" ", "_")
      .replace("-", "_")
      .replace("(", "")
      .replace(")", "")
  )

  # Check for Healthy
  if "healthy" in clean_key:
    h = DISEASE_KNOWLEDGE["healthy"]
    return f"{crop_name.capitalize()} Healthy", h["cause"], h["treatment"]

  # Check exact dictionary key or token match
  for key, data in DISEASE_KNOWLEDGE.items():
    key_stem = key.replace(f"{crop_name.lower()}_", "")
    if key in clean_key or (len(key_stem) > 4 and key_stem in clean_key):
      title = data["name"]
      if not title.lower().startswith(crop_name.lower()):
        title = f"{crop_name.capitalize()} {title}"
      return title, data["cause"], data["treatment"]

  # Fallback for dynamic/unregistered names
  words = (
      raw_str.replace("___", " ")
      .replace("__", " ")
      .replace("_", " ")
      .replace("-", " ")
      .split()
  )
  deduped = []
  for w in words:
    if not deduped or w.lower() != deduped[-1].lower():
      deduped.append(w)
  clean_title = " ".join(deduped).title()

  if not clean_title.lower().startswith(crop_name.lower()):
    clean_title = f"{crop_name.capitalize()} {clean_title}"

  return (
      clean_title,
      (
          f"Foliar pathogen detected affecting {crop_name.capitalize()} plant"
          " vitality."
      ),
      (
          "Isolate affected foliage, check canopy aeration, and consult an"
          " agronomist for targeted treatment."
      ),
  )