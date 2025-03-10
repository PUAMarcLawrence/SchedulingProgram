import streamlit as st
import time
from utils.login_db_utils import check_old_password, change_password_to_new



def change_password():
    old_password = st.text_input("Old Password", type="password")
    column1, column2 = st.columns(2)
    new_password = column1.text_input("New Password", type="password")
    confirm_password = column2.text_input("Confirm Password", type="password")
    if st.button("Change Password"):
        if old_password and new_password and confirm_password:
            if new_password == confirm_password:
                if check_old_password(st.session_state['username'],old_password):
                    if change_password_to_new(st.session_state['username'],new_password):
                        st.success("Password changed successfully.")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("Password change failed. Please try again.")
                else:
                    st.error("Old password is incorrect.")
            else:
                st.error("Passwords do not match. Please try again.")
        else:
            st.error("All fields are required.")

option = st.selectbox("Settings", ["Change Password"])
if option == "Change Password":
    change_password()

# def help(label: str, url: str):

#      try:
#         st.link_button(label, url)
#      except AttributeError:
#          if st.button(label):
#              webbrowser.open_new_tab(url)

# help("Go to google", "https://www.google.com")
# 
def userManual():
    with st.expander("USER MANUAL"):
        st.markdown("<h1 style= 'text-align: center;'>USER MANUAL</h1>", unsafe_allow_html=True)
        st.markdown("<p style= 'text-align: center;'>This is the user manual on how to use the Scheduling Tools program</p>", unsafe_allow_html=True)
        st.markdown("<h2 style= 'text-align: center;'>ACCOUNT CREATION</h2>", unsafe_allow_html=True)

        st.markdown("1.	When you first access the Scheduling Tools website, it will lead the user to the login page")
        st.image("images/usermanual_images/Picture1.png")

        st.markdown("2.	If the user already has an account registered, he can use this credentials to login to the system, if not, Click on the Register New User to create an account. It will lead the user to the account creation window.")
        st.image("images/usermanual_images/Picture2.png")

        st.markdown("3.	The use must input the required details on the text boxes (e.g. Username, Password.)")
        st.markdown("4.	The user can select his role on the system if he is a Dean or a Subject Chair.")
        st.image("images/usermanual_images/Picture3.png")

        st.markdown("5.	Next is selecting their program.")
        st.markdown("6.	Lastly, The dean or subject chair can select their color for their identification in schedule making.")
        st.image("images/usermanual_images/Picture4.png")

        st.markdown("7.	After registering, the user will be lead to the login page where he can use his newly created account to access the system")
        st.image("images/usermanual_images/Picture5.png")

        st.markdown("<h2 style= 'text-align: center;'>ACCOUNT CREATION</h2>", unsafe_allow_html=True)

        st.markdown("1.	The side bar shows the features that can be utilized by the user while using the Scheduling Tools program")
        st.image("images/usermanual_images/Picture6.png")

        st.markdown(
            """
            <p>a.	The Log out button signs out the user from the program and leads him to the login page again.</p>
            <p>b.	The Settings button leads the user to the Settings page where the user can change his password</p>
            """,
            unsafe_allow_html=True
        )
        st.image("images/usermanual_images/Picture7.png")

        st.markdown(
            """
            <p>c.	The Subject Chair Management allows the user, specially the Dean to add programs and the names of the subjects chairs</p>
            <p>d.	The Upload Curriculum button allows the user to upload an excel (.xlsx) file in a fixed format to be displayed, reviewed, and edited</p>
            """,
            unsafe_allow_html=True
        )
        st.image("images/usermanual_images/Picture8.png")

        st.markdown("If the user chooses to upload an excel file, the file will be automatically read and displayed on the same page ")
        st.image("images/usermanual_images/Picture9.png")

        st.markdown("After viewing and reviewing the displayed curriculum, the user can choose a program to upload it to and then scroll down the page to click the upload curriculum to insert the curriculum on the database")
        st.image(["images/usermanual_images/Picture10.png", "images/usermanual_images/Picture11.png"])

        st.markdown(
            """
            <h4> Note: Every cell in the displayed curriculum can be modified</h4>
            <p>The Download Template Excel File button downloads an formatted empty excel file for the user to use if he decides to create or edit a curriculum.</p>
            <p>e.	The Quick View Button asks the user to choose a program to display its curriculum</p>
            """,
            unsafe_allow_html=True
        )
        st.image("images/usermanual_images/Picture12.png")

        st.markdown("When a curriculum is chosen, the curriculum’s program tree will be displayed. The Program Tree displays all courses in the curriculum connected by their pre-requisites or co-requisites.")
        st.image("images/usermanual_images/Picture13.png")


    st.markdown(
        """
        <p>The window of the Program Tree can be zoomed in for a more clearer readability and navigation</p>
        <p>The user can click and hover on any node to see the information of the course and the courses it is connected to</p>    
        """, unsafe_allow_html=True
    )
    st.image("images/usermanual_images/Picture14.png")

    st.markdown("f.	The Sandbox button leads the user to the sandbox curriculum creation menu. It allows the user to create a curriculum from scratch or modify an existing curriculum and save it as a new one")
    st.image("images/usermanual_images/Picture15.png")

    st.markdown("After creating a sandbox, the user can select the sandbox from the dropdown menu")
    st.image(["images/usermanual_images/Picture16.png","images/usermanual_images/Picture17.png"])

    st.markdown(
        """
        <p>The user can modify any cell in the display curriculum</p>
        <p>After modifying, the user can press the save button to apply the changes.</p>
        <p>g.	The School Scheduling Button leads the user to a new page that allows him to create a schedule that is shared and can be seen by all users</p>
        """, unsafe_allow_html=True
    )
    st.image(["images/usermanual_images/Picture18.png", "images/usermanual_images/Picture19.png"])

    st.markdown("The user can fill in all the blanks and choose all needed options to create a class he desires")
    st.image(["images/usermanual_images/Picture20.png", "images/usermanual_images/Picture21.png"])

    st.markdown(
        """
        <p>After filling all blanks and selecting needed options, the user can click on Add Class to create the class.</p>
        <p>The user then can click on the drop down menu on the side bar of the website and select show schedule to see the class he created.</p>
        """, unsafe_allow_html=True
    )
    st.image(["images/usermanual_images/Picture22.png", "images/usermanual_images/Picture23.png"])

    st.markdown("h.	On the sidebar, the user can also export the schedules selected from specific Curriculums, Batch, and Terms")
    st.image("images/usermanual_images/Picture24.png")

    st.markdown("i.	On the sidebar, the user can select Delete classes to be able to remove classes")
    st.image("images/usermanual_images/Picture25.png")


    st.markdown(
        """
        <p>They can select a class from a curriculum, batch, and Term to delete</p>
        <p>j.	Lastly, the user can select the edit a class from the sidebar to be able to modify classes</p>
        """, unsafe_allow_html=True
    )
    st.image("images/usermanual_images/Picture26.png")
    
userManual()