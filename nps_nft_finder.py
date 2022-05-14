# Find a NFT to Support the NPS

################################################################################

# Imports/Dependencies 
import streamlit as st
from dataclasses import dataclass
from typing import Any, List
from web3 import Web3
w3 = Web3(Web3.HTTPProvider('HTTP://127.0.0.1:7545'))
video_file = open('video/parks.mp4', 'rb')
video_bytes = video_file.read()
from crypto_wallet import generate_account, get_balance, send_transaction
from pinata import pin_file_to_ipfs, pin_json_to_ipfs, convert_data_to_json

################################################################################
# NFTs for NPS Information

# Database of NFTs for the NPS.
park_database = {
    "Everglades": ["Everglades", "0x7e2576715d041B8bD21474def284f4467eC77bDD", "4.4", .29, "NFTs/gator.png"],
    "Bryce Canyon": ["Bryce Canyon", "0xA3f65fD3dC32b9009eB550200819FaAF57b70acb", "5.0", .35, "NFTs/prairie_dog.png"],
    "Dry Tortugas": ["Dry Tortugas", "0x0a65b1Ea1faB2813F0F2C1218Fe1514785d9ead7", "4.7", .33, "NFTs/sea_turtle.jpg"],
    "Yellowstone": ["Yellowstone", "0x404DB0bbF61466aC8cd5f2e37aFb737a6dbC03ad", "4.4", .31, "NFTs/wolf.png"],
    "Yosemite" : ["Yosemite", "0xC85ea9fA314D205FBC2ca887cCA5329B6592A4eF", "4.6", .32, "NFTs/bighorn_sheep.jpg" ],
    "Zion" : ["Zion","0xC4e3b40A262DE9A6D0b1A0ca2f8D688B8106b3FB", "5.0", .35, "NFTs/cougar.png" ]
    }

# A list of the NPS
parks = ["Everglades", "Bryce Canyon", "Dry Tortugas", "Yellowstone", "Yosemite", "Zion"]
x = len(parks)
def get_parks():
    """Display the database of NFTs for NPS information."""
    db_list = list(park_database.values())
    for number in range(x):
        st.image(db_list[number][4], width=400)
        st.write("Park Name: "," ", db_list[number][0])
        st.write("Ehtereum Account Address: ", " ", db_list[number][1])    
        st.write("Park Yelp Rating: ", " ", db_list[number][2])
        st.write("Donation of Ether: ", " ", db_list[number][3], "ETH")
        st.text(" \n")

def pin_artwork(artwork_name, artwork_file):
    # Pin the file to IPFS with Pinata
    ipfs_file_hash = pin_file_to_ipfs(artwork_file.getvalue())

    # Build a token metadata file for the artwork
    token_json = {
        "name": artwork_name,
        "image": ipfs_file_hash
    }
    json_data = convert_data_to_json(token_json)

    # Pin the json to IPFS with Pinata
    json_ipfs_hash = pin_json_to_ipfs(json_data)

    return json_ipfs_hash
################################################################################
# Streamlit Code

# Streamlit application headings
st.set_page_config(
    page_title="NFTs for the NPS!",
    page_icon=":park:",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help' : 'https://github.com/mikecordes/Project3',
        'About' : "Project Team is Griselda, Chris, Bobby, John, Troy, and Michael"

    }
)
st.title('🏞️ NFTs for the NPS!🏞️' , anchor=None)
st.video(video_bytes)
st.subheader('Donate to a National Park and own NFTs!')
st.text(" \n")


################################################################################
# Streamlit Sidebar Code - Start

st.sidebar.markdown("# Your Wallet and Balance in Ether")

#  Call the `generate_account` function 
account = generate_account()

##########################################

# Write the user's Ethereum account address to the sidebar
st.sidebar.write(account.address)

##########################################

# Calls the `get_balance` function and pass it your account address and writes the returned ether balance to the sidebar
ether_balance = get_balance(w3, account.address)
st.sidebar.write("Your ETH Balance",ether_balance)

##########################################

# Create a select box to chose a Park to donoate to
parks = st.sidebar.selectbox('Select a Park to Suppot', parks)

# sliding bar for quantity of NFTs
NFTs = st.sidebar.slider("Number of NFTs to Buy")

st.sidebar.markdown("## Park Name, Number of NFTs, and Ethereum Address")

# Identify the Park to donate to 
parks = park_database[parks][0]

# Write the Park to the sidebar
st.sidebar.write(parks)

# Identify the park's donation rate
donation = park_database[parks][3]

# Write tthe park's donation rate to the sidebar
st.sidebar.write(donation)

# Identify the park's Ethereum Address
park_address = park_database[parks][1]

# Write the park's Ethereum Address to the sidebar
st.sidebar.write(park_address)
st.sidebar.markdown("## Total Donation in Ether")

################################################################################

# Calculate total total donation 
total_donation = park_database[parks][3] * NFTs

# Write the total donation calculation to the Streamlit sidebar
st.sidebar.write(total_donation)

##########################################

if st.sidebar.button("Send Transaction 🏞️"):
    transaction_hash = send_transaction(w3, account, park_address, total_donation)

    # Markdown for the transaction hash
    st.sidebar.markdown("#### Validated Transaction Hash")

    # Write the returned transaction hash to the screen
    st.sidebar.write(transaction_hash)

    # Celebrate your successful payment
    st.snow()

st.sidebar.markdown("## Register New Artwork")
artwork_name = st.sidebar.text_input("Enter the name of the park")
artist_name = st.sidebar.text_input("Enter the artist name")
initial_appraisal_value = st.sidebar.text_input("Enter the initial appraisal amount")

# Use the Streamlit `file_uploader` function create the list of digital image file types(jpg, jpeg, or png) that will be uploaded to Pinata.
file = st.sidebar.file_uploader("Upload Artwork", type=["jpg", "jpeg", "png"])

if st.sidebar.button("Register Artwork"):
    # Use the `pin_artwork` helper function to pin the file to IPFS
    artwork_ipfs_hash = pin_artwork(artwork_name, file)

    artwork_uri = f"ipfs://{artwork_ipfs_hash}"

    tx_hash = contract.functions.registerArtwork(
        address,
        artwork_name,
        artist_name,
        int(initial_appraisal_value),
        artwork_uri
    ).transact({'from': address, 'gas': 1000000})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    st.sidebar.write("Transaction receipt mined:")
    st.sidebar.write(dict(receipt))
    st.sidebar.write("You can view the pinned metadata file with the following IPFS Gateway Link")
    st.sidebar.markdown(f"[Artwork IPFS Gateway Link](https://ipfs.io/ipfs/{artwork_ipfs_hash})")
st.sidebar.markdown("---") 

# The function that starts the Streamlit application
# Writes NFTs for the NPS the Streamlit page
get_parks()

################################################################################
