from turtle import onclick
import streamlit as st
import json
import urllib.request
from PIL import Image
from pathlib import Path
from dataclasses import dataclass
from typing import Any, List
from web3 import Web3
w3 = Web3(Web3.HTTPProvider('HTTP://127.0.0.1:7545'))
video_file = open('video/parks.mp4', 'rb')
video_bytes = video_file.read()
from crypto_wallet import generate_account, get_balance, send_transaction
from pinata import pin_file_to_ipfs, pin_json_to_ipfs, convert_data_to_json

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

st.header("Gallery")
park_database = {
"Everglades": ["Everglades", "0x9553901b1449bA6c711f1C21D2FB9737542816B2", "4.4", .29, "NFTs/gator.png"],
"Bryce Canyon": ["Bryce Canyon", "0xaF571cA474f5C381969991fa996f864Ca06D6B73", "5.0", .35, "NFTs/prairie_dog.png"],
"Dry Tortugas": ["Dry Tortugas", "0xDe3771F05deAe03a997cbbBFA573003BB1E36cC7", "4.7", .33, "NFTs/sea_turtle.jpg"],
"Yellowstone": ["Yellowstone", "0x88B54e78De038C03C29879e4dfdc920a361610bE", "4.4", .31, "NFTs/wolf.png"],
"Yosemite" : ["Yosemite", "0x3355Be2F5393c71468e4db5e45965Cf17A8b476b", "4.6", .32, "NFTs/bighorn_sheep.jpg" ],
"Zion" : ["Zion","0xd885b1fe830Ef6032f381752cf35e34C99dDb98b", "5.0", .35, "NFTs/cougar.png" ]
}

# A list of the NPS
global parks
parks = list(park_database.keys())
x = len(parks)
def get_parks():
    """Display the database of NFTs for NPS information."""
    db_list = list(park_database.values())
    for number in range(x):
        st.image(db_list[number][4], output_format="JPEG", width=400)
        st.write("Park Name: "," ", db_list[number][0])
        st.write("Ethereum Account Address: ", " ", db_list[number][1])    
        st.write("Park Yelp Rating: ", " ", db_list[number][2])
        st.write("Donation of Ether: ", " ", db_list[number][3], "ETH")
        st.text(" \n")
def pin_artwork(artwork_name, artwork_file):
    # Pin the file to IPFS with Pinata
    global ipfs_file_hash
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
if 'count' not in st.session_state:
    st.session_state.count = 0
if 'artz' not in st.session_state:
    st.session_state.artz = []
st.title('🏞️ NFTs for the NPS!🏞️' , anchor=None)
st.video(video_bytes)
st.subheader('Donate to a National Park and own NFTs!')
st.text(" \n")
@st.cache(allow_output_mutation=True)
def load_contract():

    # Load the contract ABI
    with open(Path('./artregistry_abi.json')) as f:
        contract_abi = json.load(f)

    # Set the contract address (this is the address of the deployed contract)
    contract_address = "0xd9145CCE52D386f254917e481eB44e9943F39138"
    address=contract_address
    # Get the contract
    contract = w3.eth.contract(
        address=contract_address,
        abi=contract_abi
    )

    return contract


# Load the contract
contract = load_contract()
################################################################################
# Streamlit Code



################################################################################
# Streamlit Sidebar Code - Start

st.sidebar.markdown("# Your Wallet")

#  Call the `generate_account` function 
account = generate_account()

##########################################

# Write the user's Ethereum account address to the sidebar
st.sidebar.write(account.address)

##########################################

# Calls the `get_balance` function and pass it your account address and writes the returned ether balance to the sidebar
ether_balance = get_balance(w3, account.address)
st.sidebar.write("ETH Balance:", ether_balance)
st.sidebar.markdown("---")     

##########################################

st.sidebar.markdown("## Register New Artwork")
if st.sidebar.checkbox("Yes"):
    artwork_name = st.sidebar.text_input("Enter the name of the park")
    artist_name = st.sidebar.text_input("Enter the artist name")
    initial_appraisal_value = st.sidebar.text_input("Enter the initial appraisal amount")

    # Use the Streamlit `file_uploader` function create the list of digital image file types(jpg, jpeg, or png) that will be uploaded to Pinata.
    file = st.sidebar.file_uploader("Upload Artwork", type=["jpg", "jpeg", "png"])

    if st.sidebar.button("Register Artwork"):
        # Use the `pin_artwork` helper function to pin the file to IPFS
        artwork_ipfs_hash = pin_artwork(artwork_name, file)

        artwork_uri = f"ipfs://{artwork_ipfs_hash}"
        address="0xBc1c09B4B4E2068074757c72f182a4788c676030"
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
        zz = st.session_state.count
        urllib.request.urlretrieve(f"https://ipfs.io/ipfs/{ipfs_file_hash}",f"NFTs/uploaded{zz}.png")
        img = Image.open(f"NFTs/uploaded{zz}.png")
        park_database[f"{artwork_name}{zz}"] = [artwork_name, "0x9553901b1449bA6c711f1C21D2FB9737542816B2", "4.4", .29, f"NFTs/uploaded{zz}.png"]
        parks = list(park_database.keys())
        x = len(parks)
        st.session_state.count += 1
        st.session_state.artz.append(artwork_name)


if  st.session_state.count > 0:
    z = st.session_state.count
    xz = st.session_state.artz
    for zz in range(z):
        img = Image.open(f"NFTs/uploaded{zz}.png")
        park_database[f"{xz[zz]}{zz}"] = [f"{xz[zz]}{zz}", park_database.get(xz[zz])[1], park_database.get(xz[zz])[2], park_database.get(xz[zz])[3], f"NFTs/uploaded{zz}.png"]
        parks = list(park_database.keys())
        x = len(parks)
get_parks()
st.sidebar.markdown("---")     
st.sidebar.markdown("## Support the Parks")

# Create a select box to chose a FinTech Hire candidate
parks1 = st.sidebar.selectbox('Select a Park to Support', parks)

# Create a input field to record the number of hours the candidate worked
NFTs = st.sidebar.slider("Number of NFTs to Buy")

st.sidebar.markdown("## Park Name, Number of NFTs, and Ethereum Address")

# Identify the Park to donate to 
parks2 = park_database[parks1][0]

# Write the Fintech Finder candidate's name to the sidebar
st.sidebar.write(parks2)

# Identify the FinTech Finder candidate's hourly rate
donation = park_database[parks1][3]

# Write the inTech Finder candidate's hourly rate to the sidebar
st.sidebar.write(donation)

# Identify the FinTech Finder candidate's Ethereum Address
park_address = park_database[parks1][1]

# Write the inTech Finder candidate's Ethereum Address to the sidebar
st.sidebar.write(park_address)
st.sidebar.markdown("## Total Donation in Ether")

################################################################################

# Calculate total total donation 
total_donation = park_database[parks1][3] * NFTs

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
# The function that starts the Streamlit application
# Writes NFTs for the NPS the Streamlit page


