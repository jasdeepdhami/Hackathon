import pandas as pd
import re

from math import radians, sin, cos, sqrt, atan2


def _term_in_query(term, query, min_length=3):
    term = str(term).strip().lower()
    short_allowed = {"tb"}
    if not term or term in {"nan", "none", "null"}:
        return False
    if len(term) < min_length and term not in short_allowed:
        return False
    return re.search(r"\b" + re.escape(term) + r"\b", str(query).lower()) is not None


# ============================================================
# ANALYZE QUERY
# ============================================================

def analyze_query(query, hospital_data=None):

    if not query:
        return {
            "disease": None,
            "specialty": None,
            "city": None,
            "state": None,
            "hospital": None,
            "hospitals": [],
            "budget": None,
            "sort_by": "success_rate",
            "intent": "search",
            "number": 5
        }

    query = str(query).lower().strip()

    result = {
        "disease": None,
        "specialty": None,
        "city": None,
        "state": None,
        "hospital": None,
        "hospitals": [],
        "budget": None,
        "sort_by": "success_rate",
        "intent": "search",
        "number": 5
    }

    # ========================================================
    # NUMBER OF RESULTS
    # ========================================================

    number_match = re.search(
        r"\b(\d+)\s+(?:hospital|hospitals|options|results)\b",
        query
    )

    if number_match:
        result["number"] = int(number_match.group(1))

    # ========================================================
    # BUDGET
    # ========================================================

    budget_patterns = [
        r"(?:under|below|less than|within|maximum|max)\s*(?:₹|rs\.?|inr)?\s*([\d,]+)",
        r"(?:budget|cost)\s*(?:of|is)?\s*(?:₹|rs\.?|inr)?\s*([\d,]+)"
    ]

    for pattern in budget_patterns:

        budget_match = re.search(
            pattern,
            query,
            re.IGNORECASE
        )

        if budget_match:

            try:
                result["budget"] = float(
                    budget_match.group(1).replace(",", "")
                )

                break

            except ValueError:
                pass

    result["sort_by"] = "success_rate"

    # ========================================================
    # DISEASE
    # ========================================================

    diseases = [
        "heart disease",
        "cardiac disease",
        "kidney disease",
        "kidney problems",
        "liver disease",
        "lung disease",
        "blood cancer",
        "breast cancer",
        "prostate cancer",
        "cancer",
        "diabetes",
        "asthma",
        "pneumonia",
        "tuberculosis",
        "tb",
        "dengue",
        "malaria",
        "typhoid",
        "covid-19",
        "covid",
        "arthritis",
        "migraine",
        "stroke",
        "hypertension",
        "high blood pressure",
        "blood pressure"
    ]

    if hospital_data is not None and "disease" in hospital_data.columns:
        diseases.extend(
            hospital_data["disease"]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )

    diseases = sorted(
        {str(item).strip() for item in diseases if str(item).strip()},
        key=len,
        reverse=True
    )

    for disease in diseases:
        if _term_in_query(disease, query, min_length=3):
            result["disease"] = disease
            break

    # ========================================================
    # SPECIALTY
    # ========================================================

    specialties = [
        "general surgery",
        "internal medicine",
        "cardiology",
        "neurology",
        "neurosurgery",
        "oncology",
        "orthopedics",
        "orthopaedics",
        "dermatology",
        "pediatrics",
        "paediatrics",
        "gynecology",
        "gynaecology",
        "urology",
        "nephrology",
        "gastroenterology",
        "pulmonology",
        "psychiatry",
        "ophthalmology",
        "dentistry",
        "ent"
    ]

    specialties = sorted(
        specialties,
        key=len,
        reverse=True
    )

    for specialty in specialties:
        if _term_in_query(specialty, query, min_length=3):
            result["specialty"] = specialty
            break

    # ========================================================
    # CITY
    # ========================================================

    if hospital_data is not None and "city" in hospital_data.columns:

        cities = (
            hospital_data["city"]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )

        cities = sorted(
            cities,
            key=len,
            reverse=True
        )

        for city in cities:

            if re.search(
                r"\b" + re.escape(city.lower()) + r"\b",
                query
            ):

                result["city"] = city
                break

    # ========================================================
    # STATE
    # ========================================================

    if hospital_data is not None and "state" in hospital_data.columns:

        states = (
            hospital_data["state"]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )

        states = sorted(
            states,
            key=len,
            reverse=True
        )

        for state in states:

            if re.search(
                r"\b" + re.escape(state.lower()) + r"\b",
                query
            ):

                result["state"] = state
                break

    # ========================================================
    # HOSPITAL NAME
    # ========================================================

    if (
        hospital_data is not None
        and "hospital_name" in hospital_data.columns
    ):

        hospitals = (
            hospital_data["hospital_name"]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )

        hospitals = sorted(
            hospitals,
            key=len,
            reverse=True
        )

        remaining = query
        matched = []

        for hospital in hospitals:
            if _term_in_query(hospital, remaining, min_length=4):
                matched.append(hospital)
                remaining = re.sub(
                    r"\b" + re.escape(hospital.lower()) + r"\b",
                    " ",
                    remaining,
                    count=1,
                )
                if len(matched) >= 2:
                    break

        result["hospitals"] = matched
        if matched:
            result["hospital"] = matched[0]

    compare_words = bool(re.search(
        r"\b(compare|versus|vs|or|better|difference between|which (?:one )?is better)\b",
        query
    ))

    if len(result["hospitals"]) >= 2 or (
        compare_words and len(result["hospitals"]) >= 1
    ):
        result["intent"] = "compare"

    return result


# ============================================================
# SUCCESS RATE
# ============================================================

def calculate_success_rate(df):

    df = df.copy()

    treated = pd.to_numeric(
        df["patients_treated_well"],
        errors="coerce"
    ).fillna(0)

    not_treated = pd.to_numeric(
        df["patients_not_treated_well"],
        errors="coerce"
    ).fillna(0)

    total = treated + not_treated

    df["success_rate"] = (
        treated
        / total.replace(0, pd.NA)
        * 100
    )

    df["success_rate"] = (
        df["success_rate"]
        .fillna(0)
        .round(2)
    )

    return df


# ============================================================
# HAVERSINE DISTANCE
# ============================================================

def calculate_distance(
    lat1,
    lon1,
    lat2,
    lon2
):

    try:

        lat1 = float(lat1)
        lon1 = float(lon1)
        lat2 = float(lat2)
        lon2 = float(lon2)

    except (ValueError, TypeError):

        return None

    lat1 = radians(lat1)
    lon1 = radians(lon1)

    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        +
        cos(lat1)
        * cos(lat2)
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    radius = 6371

    return radius * c


# ============================================================
# ADD DISTANCE
# ============================================================

def add_distance(
    df,
    user_latitude,
    user_longitude
):

    df = df.copy()

    df["distance_km"] = df.apply(
        lambda row: calculate_distance(
            user_latitude,
            user_longitude,
            row["latitude"],
            row["longitude"]
        ),
        axis=1
    )

    return df


# ============================================================
# FILTER HOSPITALS
# ============================================================

def filter_hospitals(
    hospital_data,
    disease=None,
    specialty=None,
    city=None,
    state=None,
    hospital=None,
    budget=None
):

    df = hospital_data.copy()

    # --------------------------------------------------------
    # Disease
    # --------------------------------------------------------

    if disease:

        mask = (
            df["disease"]
            .astype(str)
            .str.contains(
                str(disease),
                case=False,
                na=False
            )
        )

        df = df[mask]

    # --------------------------------------------------------
    # Specialty
    # --------------------------------------------------------

    if specialty:

        mask = (
            df["specialties"]
            .astype(str)
            .str.contains(
                str(specialty),
                case=False,
                na=False
            )
        )

        df = df[mask]

    # --------------------------------------------------------
    # City
    # --------------------------------------------------------

    if city:

        mask = (
            df["city"]
            .astype(str)
            .str.lower()
            ==
            str(city).lower()
        )

        df = df[mask]

    # --------------------------------------------------------
    # State
    # --------------------------------------------------------

    if state:

        mask = (
            df["state"]
            .astype(str)
            .str.lower()
            ==
            str(state).lower()
        )

        df = df[mask]

    # --------------------------------------------------------
    # Hospital
    # --------------------------------------------------------

    if hospital:

        mask = (
            df["hospital_name"]
            .astype(str)
            .str.contains(
                str(hospital),
                case=False,
                na=False
            )
        )

        df = df[mask]

    # --------------------------------------------------------
    # Budget
    # --------------------------------------------------------

    if budget is not None:

        df["treatment_cost_inr"] = pd.to_numeric(
            df["treatment_cost_inr"],
            errors="coerce"
        )

        df = df[
            df["treatment_cost_inr"] <= budget
        ]

    return df


# ============================================================
# REMOVE DUPLICATE HOSPITALS
# ============================================================

def remove_duplicate_hospitals(df):

    if df.empty:
        return df

    df = (
        df.sort_values(
            "success_rate",
            ascending=False
        )
        .drop_duplicates(
            subset=["hospital_name"],
            keep="first"
        )
    )

    return df


# ============================================================
# SORT HOSPITALS
# ============================================================

def sort_hospitals(
    df,
    sort_by=None
):

    if df.empty:
        return df

    # --------------------------------------------------------
    # Distance
    # --------------------------------------------------------

    if sort_by == "distance":

        if "distance_km" in df.columns:

            df = df.sort_values(
                "distance_km",
                ascending=True
            )

    # --------------------------------------------------------
    # Cost
    # --------------------------------------------------------

    elif sort_by == "cost":

        df["treatment_cost_inr"] = pd.to_numeric(
            df["treatment_cost_inr"],
            errors="coerce"
        )

        df = df.sort_values(
            "treatment_cost_inr",
            ascending=True
        )

    # --------------------------------------------------------
    # Success Rate
    # --------------------------------------------------------

    elif sort_by == "success_rate":

        df = df.sort_values(
            "success_rate",
            ascending=False
        )

    # --------------------------------------------------------
    # Rating
    # --------------------------------------------------------

    elif sort_by == "rating":

        df["rating"] = pd.to_numeric(
            df["rating"],
            errors="coerce"
        )

        df = df.sort_values(
            "rating",
            ascending=False
        )

    # --------------------------------------------------------
    # Default
    # --------------------------------------------------------

    else:

        df["rating"] = pd.to_numeric(
            df["rating"],
            errors="coerce"
        )

        df = df.sort_values(
            "rating",
            ascending=False
        )

    return df


# ============================================================
# RECOMMEND HOSPITALS
# ============================================================

def recommend_hospitals(
    hospital_data,
    query_info,
    user_latitude=None,
    user_longitude=None
):

    # --------------------------------------------------------
    # Calculate success rate
    # --------------------------------------------------------

    df = calculate_success_rate(
        hospital_data
    )

    # --------------------------------------------------------
    # Extract NLP information
    # --------------------------------------------------------

    disease = query_info.get(
        "disease"
    )

    specialty = query_info.get(
        "specialty"
    )

    city = query_info.get(
        "city"
    )

    state = query_info.get(
        "state"
    )

    hospital = query_info.get(
        "hospital"
    )

    budget = query_info.get(
        "budget"
    )

    sort_by = query_info.get(
        "sort_by"
    )

    number = query_info.get(
        "number",
        5
    )

    # --------------------------------------------------------
    # Filter
    # --------------------------------------------------------

    df = filter_hospitals(
        df,
        disease=disease,
        specialty=specialty,
        city=city,
        state=state,
        hospital=hospital,
        budget=budget
    )

    # --------------------------------------------------------
    # Calculate distance
    # --------------------------------------------------------

    if (
        user_latitude is not None
        and user_longitude is not None
    ):

        df = add_distance(
            df,
            user_latitude,
            user_longitude
        )

    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    df = remove_duplicate_hospitals(
        df
    )

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    df = sort_hospitals(
        df,
        sort_by
    )

    # --------------------------------------------------------
    # Limit results
    # --------------------------------------------------------

    df = df.head(
        number
    )

    return df.reset_index(
        drop=True
    )


# ============================================================
# COMPARE HOSPITALS
# ============================================================

def compare_hospitals(
    hospital_data,
    hospital_names
):

    df = calculate_success_rate(
        hospital_data
    )

    results = []

    for hospital_name in hospital_names:

        matches = df[
            df["hospital_name"]
            .astype(str)
            .str.contains(
                str(hospital_name),
                case=False,
                na=False
            )
        ]

        if not matches.empty:

            row = (
                matches
                .sort_values(
                    "success_rate",
                    ascending=False
                )
                .iloc[0]
            )

            results.append(row)

    if not results:

        return pd.DataFrame()

    comparison = pd.DataFrame(
        results
    )

    return comparison.reset_index(
        drop=True
    )