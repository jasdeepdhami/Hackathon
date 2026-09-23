import pandas as pd
from math import radians, sin, cos, sqrt, atan2


# ============================================================
# CALCULATE SUCCESS RATE
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

    total_patients = treated + not_treated

    df["success_rate"] = 0.0

    valid = total_patients > 0

    df.loc[valid, "success_rate"] = (
        treated[valid]
        / total_patients[valid]
        * 100
    )

    return df


# ============================================================
# CALCULATE DISTANCE USING HAVERSINE FORMULA
# ============================================================

def calculate_distance(
    user_latitude,
    user_longitude,
    hospital_latitude,
    hospital_longitude
):

    try:

        user_latitude = float(user_latitude)
        user_longitude = float(user_longitude)

        hospital_latitude = float(hospital_latitude)
        hospital_longitude = float(hospital_longitude)

    except (ValueError, TypeError):

        return None

    # Convert degrees to radians

    user_latitude = radians(user_latitude)
    user_longitude = radians(user_longitude)

    hospital_latitude = radians(hospital_latitude)
    hospital_longitude = radians(hospital_longitude)

    # Difference

    dlat = hospital_latitude - user_latitude
    dlon = hospital_longitude - user_longitude

    # Haversine formula

    a = (
        sin(dlat / 2) ** 2
        +
        cos(user_latitude)
        * cos(hospital_latitude)
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    # Earth radius in kilometres

    earth_radius = 6371

    return earth_radius * c


# ============================================================
# ADD DISTANCE TO DATAFRAME
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
    # Disease filter
    # --------------------------------------------------------

    if disease:

        df = df[
            df["disease"]
            .astype(str)
            .str.contains(
                str(disease),
                case=False,
                na=False
            )
        ]

    # --------------------------------------------------------
    # Specialty filter
    # --------------------------------------------------------

    if specialty:

        df = df[
            df["specialties"]
            .astype(str)
            .str.contains(
                str(specialty),
                case=False,
                na=False
            )
        ]

    # --------------------------------------------------------
    # City filter
    # --------------------------------------------------------

    if city:

        df = df[
            df["city"]
            .astype(str)
            .str.lower()
            ==
            str(city).lower()
        ]

    # --------------------------------------------------------
    # State filter
    # --------------------------------------------------------

    if state:

        df = df[
            df["state"]
            .astype(str)
            .str.lower()
            ==
            str(state).lower()
        ]

    # --------------------------------------------------------
    # Hospital filter
    # --------------------------------------------------------

    if hospital:

        df = df[
            df["hospital_name"]
            .astype(str)
            .str.contains(
                str(hospital),
                case=False,
                na=False
            )
        ]

    # --------------------------------------------------------
    # Budget filter
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

    # Keep the row with the highest success rate
    # for each hospital.

    df = (
        df
        .sort_values(
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
    # Success rate
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
    # Default sorting
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
# MAIN RECOMMENDATION FUNCTION
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
    # Get information extracted by NLP
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

    sort_by = "success_rate"

    number = query_info.get(
        "number",
        5
    )

    # --------------------------------------------------------
    # Filter hospitals
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
    # Add distance if location is available
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
    # Remove duplicate hospitals
    # --------------------------------------------------------

    df = remove_duplicate_hospitals(
        df
    )

    # --------------------------------------------------------
    # Sort results
    # --------------------------------------------------------

    df = sort_hospitals(
        df,
        sort_by
    )

    # --------------------------------------------------------
    # Return requested number of hospitals
    # --------------------------------------------------------

    try:

        number = int(number)

    except (ValueError, TypeError):

        number = 5

    number = max(
        1,
        min(number, 20)
    )

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

            # If multiple dataset rows exist
            # for the same hospital, use the
            # row with the highest success rate.

            best_match = (
                matches
                .sort_values(
                    "success_rate",
                    ascending=False
                )
                .iloc[0]
            )

            results.append(
                best_match
            )

    if not results:

        return pd.DataFrame()

    comparison = pd.DataFrame(
        results
    )

    if "success_rate" in comparison.columns:
        comparison = comparison.sort_values(
            "success_rate",
            ascending=False
        )

    return comparison.reset_index(
        drop=True
    )