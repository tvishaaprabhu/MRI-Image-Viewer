import streamlit as st
import pandas as pd
import auth # Imports your database helper

def show_admin_dashboard():
    """Renders the Admin Dashboard."""
    
    # 1. DOUBLE-CHECK SECURITY
    # If a non-admin somehow gets here, stop them immediately.
    if not st.session_state.get("authenticated") or st.session_state.get("role") != "Admin":
        st.error("⛔ Unauthorized Access. You do not have admin privileges.")
        st.stop()

    st.title("⚙️ System Administration")
    st.write("Manage system users, roles, and access.")
    st.divider()

    col1, col2 = st.columns([1, 1.5])

    # --- LEFT COLUMN: ADD NEW USER ---
    with col1:
        st.header("Add New User")
        st.write("Create credentials for new staff.")
        
        with st.form("add_user_form"):
            new_email = st.text_input("Email Address")
            new_password = st.text_input("Temporary Password", type="password")
            new_role = st.selectbox("Role", ["User", "Admin"])
            
            submit_add = st.form_submit_button("Create Account")
            
            if submit_add:
                if new_email and new_password:
                    success, message = auth.create_user(new_email, new_password, new_role)
                    if success:
                        st.success(f"User {new_email} created successfully!")
                    else:
                        st.error(message)
                else:
                    st.warning("Please fill out all fields.")

    # --- RIGHT COLUMN: MANAGE EXISTING USERS ---
    with col2:
        st.header("Manage Users")
        
        # Fetch all users directly from Firestore
        users_ref = auth.db.collection("users").stream()
        user_list = [doc.to_dict() for doc in users_ref]
        
        if not user_list:
            st.info("No users found in the database.")
        else:
            # Display users in a nice table (hiding the password hashes!)
            df = pd.DataFrame(user_list)
            display_df = df[["email", "role", "status"]] # Reorder and hide password
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            st.subheader("Modify Account Access")
            with st.form("modify_user_form"):
                # Create a dropdown of all emails
                target_email = st.selectbox("Select User", df["email"].tolist())
                action = st.radio("Action", ["Block Account", "Unblock Account", "Delete Account"], horizontal=True)
                
                submit_modify = st.form_submit_button("Apply Changes")
                
                if submit_modify:
                    # Prevent admins from deleting themselves
                    if target_email == st.session_state.current_user and action != "Unblock Account":
                        st.error("You cannot block or delete your own account!")
                    else:
                        user_doc = auth.db.collection("users").document(target_email)
                        
                        if action == "Block Account":
                            user_doc.update({"status": "Blocked"})
                            st.success(f"Account {target_email} blocked.")
                        
                        elif action == "Unblock Account":
                            user_doc.update({"status": "Active"})
                            st.success(f"Account {target_email} is active again.")
                            
                        elif action == "Delete Account":
                            user_doc.delete()
                            st.success(f"Account {target_email} permanently deleted.")
                        
                        # Rerun to update the table above
                        st.rerun()
