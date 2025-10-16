# streamlit_app.py
import streamlit as st
import requests
import pandas as pd

API_URL = "http://web:8000"  # Change if FastAPI runs elsewhere

st.title("📦 Inventory Management Dashboard")

# -------------------------
# Sidebar Navigation
# -------------------------
page = st.sidebar.radio(
    "Select a page:",
    [
        "View Tables",
        "Add Part",
        "Add Location",
        "Add Inventory",
        "Adjust Inventory",
        "Move Inventory",
    ],
)

# -------------------------
# Helper Function
# -------------------------
def get_data(endpoint):
    """Utility function for GET requests."""
    try:
        res = requests.get(f"{API_URL}/{endpoint}")
        res.raise_for_status()
        return pd.DataFrame(res.json())
    except Exception as e:
        st.error(f"Error fetching {endpoint}: {e}")
        return pd.DataFrame()

# -------------------------
# View Tables
# -------------------------
if page == "View Tables":
    st.header("📋 View Database Tables")
    table = st.selectbox("Select Table", ["parts", "locations", "full inventory", "inventory aggregated"])

    if st.button("Load Data"):
        df = get_data(table)
        if not df.empty:
            st.dataframe(df)
        else:
            st.info("No data found.")

# -------------------------
# Add New Part
# -------------------------
elif page == "Add Part":
    st.header("🧩 Add New Part")

    with st.form("add_part_form", clear_on_submit=True):
        name = st.text_input("Part Name", key="name_input")
        manufacturer = st.text_input("Manufacturer", key="manufacturer_input")
        category = st.text_input("Category", key="category_input")
        supplier = st.text_input("Supplier", key="supplier_input")
        sku = st.text_input("SKU", key="SKU_input")
        description = st.text_area("Description", key="description_input")

        submitted = st.form_submit_button("Add Part")

    if submitted:
        if not name:
            st.error("Part name is required.")
        else:
            payload = {
                "name": name,
                "manufacturer": manufacturer,
                "category": category,
                "supplier": supplier,
                "sku": sku,
                "description": description,
            }

            try:
                res = requests.post(f"{API_URL}/parts/", json=payload)
                data = res.json()
            except Exception as e:
                st.error(f"Error connecting to API: {e}")
                st.stop()

            # --- Handle potential duplicates ---
            if "duplicates" in data and data["duplicates"]:
                st.warning("⚠️ Potential duplicates found. Review before confirming:")
                with st.expander("View Potential Duplicates"):
                    st.dataframe(pd.DataFrame(data["duplicates"]))

                # Store payload temporarily so user can confirm addition
                st.session_state["pending_part_payload"] = payload

                if st.button("Confirm Add Anyway"):
                    confirm_res = requests.post(
                        f"{API_URL}/parts/?force=true",
                        json=st.session_state["pending_part_payload"],
                    )
                    if confirm_res.ok:
                        st.success("✅ Part added successfully despite duplicates.")
                        st.session_state.pop("pending_part_payload", None)
                    else:
                        st.error(confirm_res.text)

            elif res.ok:
                st.success(f"✅ Part '{name}' added successfully!")
            else:
                st.error(data.get("detail", "Failed to add part."))

# -------------------------
# Add New Location
# -------------------------
elif page == "Add Location":
    st.header("🏠 Add New Location")

    with st.form("add_location_form", clear_on_submit=True):
        location_name = st.text_input("Location Name", key="location_input")
        submitted = st.form_submit_button("Add Location")

        if submitted:
            if not location_name:
                st.error("Location name is required.")
            else:
                payload = {"name": location_name}
                res = requests.post(f"{API_URL}/locations/", json=payload)
                if res.ok:
                    st.success(f"✅ Location '{location_name}' added successfully!")
                else:
                    st.error(res.text)

# -------------------------
# Add New Inventory
# -------------------------
elif page == "Add Inventory":
    st.header("📦 Add New Inventory")

    parts_df = get_data("parts")
    locations_df = get_data("locations")

    if parts_df.empty or locations_df.empty:
        st.warning("You need at least one part and one location to add inventory.")
    else:
        part_id = st.selectbox("Select Part", parts_df["id"], format_func=lambda x: parts_df.loc[parts_df["id"] == x, "name"].values[0])
        location_id = st.selectbox("Select Location", locations_df["id"], format_func=lambda x: locations_df.loc[locations_df["id"] == x, "name"].values[0])
        quantity = st.number_input("Quantity", min_value=1)

    if st.button("Add Inventory"):
        if not part_id or not location_id or not quantity:
            st.error("Part ID, Location ID, Quantity is required.")
        else:
            payload = {
                "part_id": part_id,
                "location_id": location_id,
                "quantity": quantity,
            }
            res = requests.post(f"{API_URL}/inventory/", json=payload)
            if res.ok:
                part_name = parts_df.loc[parts_df["id"] == part_id, "name"].values[0]
                location_name = locations_df.loc[locations_df["id"] == location_id, "name"].values[0]
                st.success(f"✅ {quantity} of '{part_name}' added successfully at '{location_name}'!")

                #st.success(f"✅ {quantity} of Part '{part_id}' added successfully at {location_id}!")
            else:
                st.error(res.text)

# -------------------------
# Adjust Inventory
# -------------------------
elif page == "Adjust Inventory":
    st.header("⚙️ Adjust Inventory Quantity")

    # Fetch data
    parts_df = get_data("parts")
    locations_df = get_data("locations")
    inventory_df = get_data("full inventory")

    if parts_df.empty or locations_df.empty or inventory_df.empty:
        st.warning("You need existing parts, locations, and inventory records to adjust.")
    else:
        # --- Select part and location ---
        part_id = st.selectbox(
            "Select Part",
            parts_df["id"],
            format_func=lambda x: parts_df.loc[parts_df["id"] == x, "name"].values[0]
        )
        location_id = st.selectbox(
            "Select Location",
            locations_df["id"],
            format_func=lambda x: locations_df.loc[locations_df["id"] == x, "name"].values[0]
        )

        # --- Get current inventory record for this part-location pair ---
        current_record = inventory_df[
            (inventory_df["part_name"] == parts_df.loc[parts_df["id"] == part_id, "name"].values[0]) &
            (inventory_df["location_name"] == locations_df.loc[locations_df["id"] == location_id, "name"].values[0])
        ]

        if current_record.empty:
            st.info("No inventory found for this part at this location.")
        else:
            current_qty = int(current_record["quantity"].values[0])
            current_version = int(current_record["version"].values[0])

            st.write(f"**Current Quantity:** {current_qty}")
            st.write(f"**Current Version:** {current_version}")

            quantity_change = st.number_input("Quantity Change (+/-)", step=1)

            if st.button("Submit Adjustment"):
                payload = {
                    "part_id": int(part_id),
                    "location_id": int(location_id),
                    "quantity_change": int(quantity_change),
                    "version": current_version,  # <-- send version for concurrency check
                }

                res = requests.post(f"{API_URL}/inventory/adjust/", json=payload)

                if res.status_code == 200:
                    st.success(res.json()["message"])
                    st.rerun()

                elif res.status_code == 409:
                    st.error(
                        "⚠️ Version conflict: the record was modified by another user.\n"
                        "Please refresh the page to get the latest data before retrying."
                    )

                else:
                    st.error(f"Error: {res.text}")

# -------------------------
# Move Inventory
# -------------------------
elif page == "Move Inventory":
    st.header("🚚 Move Inventory Between Locations")

    parts_df = get_data("parts")
    locations_df = get_data("locations")

    if parts_df.empty or locations_df.empty:
        st.warning("You need at least one part and one location to move inventory.")
    else:
        part_id = st.selectbox("Select Part", parts_df["id"], format_func=lambda x: parts_df.loc[parts_df["id"] == x, "name"].values[0])
        from_location_id = st.selectbox("From Location", locations_df["id"], format_func=lambda x: locations_df.loc[locations_df["id"] == x, "name"].values[0])
        to_location_id = st.selectbox("To Location", locations_df["id"], format_func=lambda x: locations_df.loc[locations_df["id"] == x, "name"].values[0])
        quantity = st.number_input("Quantity to Move", value=0, step=1)

        if st.button("Move"):
            if from_location_id == to_location_id:
                st.warning("Source and destination cannot be the same.")
            elif quantity <= 0:
                st.warning("Quantity must be positive.")
            else:
                payload = {
                    "part_id": part_id,
                    "location_id": from_location_id,
                    "to_location_id": to_location_id,
                    "quantity": quantity,
                }
                res = requests.post(f"{API_URL}/inventory/move/", json=payload)
                if res.ok:
                    part_name = parts_df.loc[parts_df["id"] == part_id, "name"].values[0]
                    from_location_name = locations_df.loc[locations_df["id"] == from_location_id, "name"].values[0]
                    to_location_name = locations_df.loc[locations_df["id"] == to_location_id, "name"].values[0]
                    st.success(f"✅ Moved {quantity} units of {part_name} from {from_location_name} → {to_location_name}.")
                else:
                    st.error(res.text)
