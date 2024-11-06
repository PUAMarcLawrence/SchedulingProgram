import streamlit as st

#import streamlit as st

# Set page config for layout and title
st.set_page_config(page_title="My Simple Homepage", layout="centered")

# Title and subtitle
st.title("Welcome to My Homepage")
st.subheader("Explore our features and learn more about what we offer.")

# Introduction text
st.write(
    """
    This is a simple homepage created with Streamlit. Here you can learn more about our features,
    see some examples, and get started on your journey with us. 
    Whether you’re here to learn or to explore, we have something for everyone!
    """
)

# Create columns for layout
col1, col2, col3 = st.columns(3)

# Example buttons for navigation
with col1:
    if st.button("About Us"):
        st.write("Here, you would provide information about your company or project.")

with col2:
    if st.button("Features"):
        st.write("Showcase the main features of your application or product here.")

with col3:
    if st.button("Get Started"):
        st.write("Provide a link or instructions to get users started.")

# Add an image or any additional content
st.image("https://via.placeholder.com/400", caption="A sample image to enhance the homepage")

# Footer
st.markdown("---")
st.write("© 2024 My Homepage. All rights reserved.")

#pg = st.navigation([st.Page("school_scheduling.py"), st.Page("app.py")])
#pg.run()