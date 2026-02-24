import plotly.express as px
import pandas as pd

# update/add code below ...

df = pd.read_csv('https://raw.githubusercontent.com/leontoddjohnson/datasets/main/data/titanic.csv')

def survival_demographics():
    """
    Group Titanic passengers by class, sex, and age group, then compute survival statistics.

    Creates an age_group column with categories: Child (0-12), Teen (13-19), Adult (20-59), Senior (60+).
    Groups passengers by (pclass, sex, age_group) and calculates:
        - n_passengers: total number of passengers in the group
        - n_survivors: number of survivors in the group
        - survival_rate: proportion of survivors (0.0 if no passengers)

    Returns:
        pd.DataFrame: A DataFrame with columns:
            - pclass (int): Passenger class (1, 2, or 3)
            - sex (category): 'female' or 'male'
            - age_group (category): 'Child', 'Teen', 'Adult', or 'Senior'
            - n_passengers (int): Count of passengers
            - n_survivors (int): Count of survivors
            - survival_rate (float): Survival rate (n_survivors / n_passengers)
    """
    df_fresh = pd.read_csv('https://raw.githubusercontent.com/leontoddjohnson/datasets/main/data/titanic.csv')
    
    age_bins = [-1, 12, 19, 59, float("inf")]
    age_labels = ["Child", "Teen", "Adult", "Senior"]

    df_fresh["age_group"] = pd.cut(df_fresh["Age"], bins=age_bins, labels=age_labels, include_lowest=True)
    df_fresh["age_group"] = pd.Categorical(df_fresh["age_group"], categories=age_labels, ordered=True)

    grouped = (
        df_fresh.groupby(["Pclass", "Sex", "age_group"], observed=False)
        .agg(
            n_passengers=("PassengerId", "size"),
            n_survivors=("Survived", "sum")
        )
        .reset_index()
    )

    grouped["n_passengers"] = grouped["n_passengers"].astype(int)
    grouped["n_survivors"] = grouped["n_survivors"].astype(int)

    grouped = grouped.rename(columns={"Pclass": "pclass", "Sex": "sex"})
    grouped["sex"] = grouped["sex"].str.lower()

    grouped["survival_rate"] = 0.0
    mask = grouped["n_passengers"] > 0
    grouped.loc[mask, "survival_rate"] = (
        grouped.loc[mask, "n_survivors"] / grouped.loc[mask, "n_passengers"]
    )

    grouped["sex"] = pd.Categorical(grouped["sex"], categories=["female", "male"], ordered=True)
    grouped["age_group"] = pd.Categorical(grouped["age_group"], categories=age_labels, ordered=True)

    return grouped.sort_values(["pclass", "sex", "age_group"]).reset_index(drop=True)

def visualize_demographic():
    """
    Visualize the difference in survivors between men and children by passenger class.

    This chart directly answers:
    "In which passenger class did more men survive than children—and by how many?"

    Returns:
        A Plotly figure showing:
        - bars for n_survivors (men vs. children) within each class
        - faded bars for total passengers
    """
    results = survival_demographics()

    # Keep only the rows we need for the question
    men = results[results["sex"] == "male"].groupby("pclass", as_index=False)["n_survivors"].sum()
    men = men.rename(columns={"n_survivors": "men_survivors"})

    children = results[results["age_group"] == "child"].groupby("pclass", as_index=False)["n_survivors"].sum()
    children = children.rename(columns={"n_survivors": "child_survivors"})

    

    compare = men.merge(children, on="pclass", how="outer").fillna(0)
    compare["men_survivors"] = compare["men_survivors"].astype(int)
    compare["child_survivors"] = compare["child_survivors"].astype(int)
    compare["difference_men_minus_children"] = compare["men_survivors"] - compare["child_survivors"]

        # --- add these lines after you create `compare` ---
    men_total = (
        df[df["Sex"] == "male"]
        .groupby("Pclass", as_index=False)
        .size()
        .rename(columns={"size": "men_total"})
    )

    child_total = (
    df[
        pd.cut(
            df["Age"],
            bins=[-1, 12, 19, 59, float("inf")],
            labels=["Child", "Teen", "Adult", "Senior"],
            include_lowest=True,
        )
        == "Child"
    ]
    .groupby("Pclass", as_index=False)
    .size()
    .rename(columns={"size": "child_total"})
    )
    men_total = men_total.rename(columns={"Pclass": "pclass"})
    child_total = child_total.rename(columns={"Pclass": "pclass"})

    compare = compare.merge(men_total, on="pclass", how="left").merge(child_total, on="pclass", how="left").fillna(0)
    compare["men_total"] = compare["men_total"].astype(int)
    compare["child_total"] = compare["child_total"].astype(int)

    bars = compare.melt(
        id_vars=["pclass", "difference_men_minus_children"],
        value_vars=["men_survivors", "child_survivors", "men_total", "child_total"],
        var_name="group",
        value_name="count",
    )

    label_map = {
        "men_total": "Men total (in class)",
        "men_survivors": "Men survivors",
        "child_total": "Children total (in class)",
        "child_survivors": "Child survivors",
    }
    bars["group"] = bars["group"].map(label_map)

   
    color_map = {
        "Men survivors": "#4C9AFF",
        "Men total (in class)": "#4C9AFF",
        "Child survivors": "#1F4E8C",
        "Children total (in class)": "#1F4E8C",
    }

    fig = px.bar(
    bars,
    x="pclass",
    y="count",
    color="group",
    barmode="group",
    title="Men vs. Children by Class",
    labels={"pclass": "Passenger Class", "count": "Count", "group": ""},
    color_discrete_map=color_map)

    # Make the "total" bars faded
    fig.update_traces(
        selector=dict(name="Men total (in class)"),
        opacity=0.25,
        texttemplate="%{y}",
        textposition="outside",
    )
    fig.update_traces(
        selector=dict(name="Children total (in class)"),
        opacity=0.23,
        texttemplate="%{y}",
        textposition="outside",
    )

    # Keep survivors fully opaque
    fig.update_traces(
        selector=dict(name="Men survivors"),
        opacity=1.0,
        texttemplate="%{y}",
        textposition="outside",
    )
    fig.update_traces(
        selector=dict(name="Child survivors"),
        opacity=1.0,
        texttemplate="%{y}",
        textposition="outside",
    )

    return fig

def family_groups():
        """Explore the relationship between family size, passenger class, and ticket fare.
            - Create a family_size column by summing SibSp and Parch + 1 (for the passenger themselves).
            - Group by pclass and family_size, then calculate:
            - n_passengers
            - average fare
            - The minimum and maximum ticket fares (to capture variation in wealth), min_fare and max_fare
            - Sort the results by pclass and family_size for easier interpretation.

            returns:
                A DataFrame with columns: pclass, family_size, n_passengers, avg_fare, min_fare, max_fare
        """
        df["family_size"] = df["SibSp"] + df["Parch"] + 1

        grouped = (
            df.groupby(["Pclass", "family_size"], dropna=False, observed=False)
            .agg(
                n_passengers=("PassengerId", "size"),
                avg_fare=("Fare", "mean"),
                min_fare=("Fare", "min"),
                max_fare=("Fare", "max"),
            )
            .reset_index()
            .rename(columns={"Pclass": "pclass"})
            .sort_values(["pclass", "family_size"])
            .reset_index(drop=True)
        )

        return grouped
    
def last_names():
        """
        Extract last names from the Name column and return counts of each last name.

        Returns:
            A pandas Series where index is last name and value is count.
        """
        last_name_series = df["Name"].str.split(",", n=1).str[0].str.strip()
        return last_name_series.value_counts()
    
def visualize_families():
    """
    Visualize whether large 3rd-class families (family_size >= 5) ever paid fares
    comparable to (or higher than) the average 1st-class fare, and how often.

    Approach:
    - Compute the overall average fare for 1st class (baseline).
    - For 3rd class and family_size >= 5, plot each family's max_fare vs family_size.
    - Add a horizontal reference line at the 1st-class average fare.
    - Highlight which (family_size, class) groups meet/exceed the baseline and count them.

    Returns:
        A Plotly figure.
    """
    results = family_groups()

    # Baseline: average 1st-class fare (overall, from raw df)
    first_class_avg_fare = float(df.loc[df["Pclass"] == 1, "Fare"].mean())

    # Focus: 3rd class, large families
    large_third = results[(results["pclass"] == 3) & (results["family_size"] >= 5)].copy()
    large_third["meets_or_exceeds_1st_avg"] = large_third["max_fare"] >= first_class_avg_fare

    n_groups_total = int(len(large_third))
    n_groups_meeting = int(large_third["meets_or_exceeds_1st_avg"].sum())

    fig = px.scatter(
        large_third,
        x="family_size",
        y="max_fare",
        color="meets_or_exceeds_1st_avg",
        size="n_passengers",
        hover_data={
            "pclass": True,
            "family_size": True,
            "n_passengers": True,
            "avg_fare": ":.2f", 
            "min_fare": ":.2f",
            "max_fare": ":.2f",
            "meets_or_exceeds_1st_avg": True,
        },
        title=(
            "Large 3rd-Class Families: Max Fare vs Family Size\n"
            f"| Baseline = Avg 1st-Class Fare ({first_class_avg_fare:.2f})"
            # f"Groups meeting/exceeding baseline: {n_groups_meeting}/{n_groups_total}"
        ),
        labels={
            "family_size": "Family Size (3rd class only, 5+)",
            "max_fare": "Max Fare within Group",
            "meets_or_exceeds_1st_avg": "Meets/Exceeds Avg 1st-Class Fare?",
            "n_passengers": "Passengers in Group",
        },
    )

    fig.update_yaxes(range=[0, 120])

    # Reference line: avg 1st-class fare
    fig.add_hline(
        y=first_class_avg_fare,
        line_dash="dash",
        line_color="orange",
        annotation_text="Avg 1st-class fare",
        annotation_position="top left",
    )

    fig.update_layout(margin=dict(t=80, b=60))
    return fig
