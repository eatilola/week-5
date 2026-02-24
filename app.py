import streamlit as st

from apputil import *

# Load Titanic dataset
df = pd.read_csv('https://raw.githubusercontent.com/leontoddjohnson/datasets/main/data/titanic.csv')

st.write("Even with the 'women and children first' idea, in which passenger class did more men survive than children, and by how many survivors?")
# Generate and display the figure
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
st.plotly_chart(fig2, use_container_width=True)

# st.write(
# '''
# # Titanic Visualization Bonus
# '''
# )
# # Generate and display the figure
# fig3 = visualize_family_size()
# st.plotly_chart(fig3, use_container_width=True)