import streamlit as st

from apputil import *

# Load Titanic dataset
df = pd.read_csv('https://raw.githubusercontent.com/leontoddjohnson/datasets/main/data/titanic.csv')

# === DEBUG CODE (remove after checking) ===
st.write("DataFrame shape:", df.shape)
st.write("Columns:", df.columns.tolist())
st.write("Sample of 2nd class females:")
st.write(df[(df["Pclass"] == 2) & (df["Sex"] == "female")][["Pclass", "Sex", "Age"]].head(20))
st.write("Age distribution for 2nd class females:")
st.write(df[(df["Pclass"] == 2) & (df["Sex"] == "female")]["Age"].describe())

age_bins = [-1, 12, 19, 59, float("inf")]
age_labels = ["child", "teen", "adult", "senior"]
df["age_check"] = pd.cut(df["Age"], bins=age_bins, labels=age_labels, include_lowest=True)

seniors_2f = df[(df["Pclass"] == 2) & (df["Sex"] == "female") & (df["age_check"] == "senior")]
st.write("2nd class female seniors count:", len(seniors_2f))
st.write(seniors_2f[["Pclass", "Sex", "Age", "age_check"]])

# === END DEBUG CODE ===

st.write("Even with the 'women and children first' idea, in which passenger class did more men survive than children, and by how many survivors?")
# Generate and display the figure

out = survival_demographics()
st.write("Total rows:", len(out))
st.write("Zero-member rows:", int((out["n_passengers"] == 0).sum()))
st.write(out[(out["pclass"] == 2) & (out["sex"] == "female") & (out["age_group"] == "senior")])

fig1 = visualize_demographic()
st.plotly_chart(fig1, width="stretch")

st.write(
    "Yes, this agrees with the family size + fare table too. The most common last names likely "
    "represent families/groups traveling together, which aligns with the table showing multiple "
    "passengers in the same class and family-size categories (especially smaller family sizes)."
)
st.write(
    "In 3rd class, did any larger families (family size 5+) pay fares comparable to (or higher than) the average 1st class passenger—and how often does that happen?"
)
# Generate and display the figure
fig2 = visualize_families()
st.plotly_chart(fig2, width="stretch")

# st.write(
# '''
# # Titanic Visualization Bonus
# '''
# )
# # Generate and display the figure
# fig3 = visualize_family_size()
# st.plotly_chart(fig3, use_container_width=True)