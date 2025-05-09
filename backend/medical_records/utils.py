import requests
from django.core.cache import cache


def fetch_medication_data(query):
    if not query:
        return None, 400, "Query parameter is required"

    cache_key = f"openfda_{query}"
    data = cache.get(cache_key)

    if data:
        return data, 200, "Data retrieved from cache"

    url = f"https://api.fda.gov/drug/event.json?search=patient.drug.medicinalproduct:{query}&limit=5"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        processed_data = {
            "raw_data": data,
            "extracted_info": extract_medication_info(data),
        }

        cache.set(cache_key, processed_data, timeout=60 * 60)
        return processed_data, 200, "Data retrieved from external API"
    except requests.RequestException as e:
        return None, 500, f"Error fetching data from external API: {str(e)}"


def extract_medication_info(data):
    """Extract important information from FDA API response"""
    extracted = {
        "brand_names": set(),
        "generic_names": set(),
        "manufacturers": set(),
        "dosage_forms": set(),
        "routes": set(),
        "substance_names": set(),
        "pharm_classes": set(),
        "reactions": set(),
    }

    if "results" not in data:
        return extracted

    for result in data.get("results", []):
        patient = result.get("patient", {})

        for reaction in patient.get("reaction", []):
            if "reactionmeddrapt" in reaction:
                extracted["reactions"].add(reaction["reactionmeddrapt"])

        for drug in patient.get("drug", []):
            if "dosageform" in drug:
                extracted["dosage_forms"].add(drug["drugdosageform"])

            openfda = drug.get("openfda", {})

            for brand in openfda.get("brand_name", []):
                extracted["brand_names"].add(brand)

            for generic in openfda.get("generic_name", []):
                extracted["generic_names"].add(generic)

            for manufacturer in openfda.get("manufacturer_name", []):
                extracted["manufacturers"].add(manufacturer)

            for route in openfda.get("route", []):
                extracted["routes"].add(route)

            for substance in openfda.get("substance_name", []):
                extracted["substance_names"].add(substance)

            for pharm_class in openfda.get("pharm_class_epc", []):
                extracted["pharm_classes"].add(pharm_class)

    return {k: list(v) for k, v in extracted.items()}
