from OpenSSL.crypto import load_crl, FILETYPE_ASN1
import datetime
import tkinter as tk
import requests
from tqdm import tqdm

url = 'http://uc.nalog.ru/cdp/fcb21945f2bb7670b371b03cee94381d4f975cd5.crl'

response = requests.get(url, stream=True)

# Get the total file size in bytes
file_size = int(response.headers.get('content-length', 0))

# Create a progress bar with the total file size
progress_bar = tqdm(total=file_size, unit='B', unit_scale=True)

# Iterate over the response content and update the progress bar
crl_data = b""
for chunk in response.iter_content(chunk_size=1024):
    progress_bar.update(len(chunk))
    crl_data += chunk

# Close the progress bar and the response
progress_bar.close()
response.close()

crl = load_crl(FILETYPE_ASN1, crl_data)
revoked= crl.get_revoked()

def search_crl():

    # Convert target serial number to bytes
    target_serial_number = entry.get().lower().encode()

    # Search for certificate by serial number
    for r in revoked:
        if r.get_serial().lower() == target_serial_number:
            serial_number = r.get_serial().decode()
            revocation_date = r.get_rev_date().decode()
            reason = r.get_reason()
            revocation_datetime = datetime.datetime.strptime(revocation_date, '%Y%m%d%H%M%SZ')
            formatted_datetime = revocation_datetime.strftime('%B %dth, %Y at %H:%M:%S UTC')
            result_label.config(text=f"Serial number: {serial_number}\nRevocation date: {formatted_datetime}\nReason: {reason}")
            break
    else:
        result_label.config(text="Certificate not found")

# Create GUI window
window = tk.Tk()
window.title("Search CRL")
window.geometry("600x300")



# Create input field for serial number
serial_label = tk.Label(window, text="Enter certificate serial number:", width=200)
serial_label.pack()
entry = tk.Entry(window)
entry.event_add('<<Paste>>', '<Control-igrave>')
entry.pack()


# Create button to search CRL
search_button = tk.Button(window, text="Search", command=search_crl)
search_button.pack()

# Create label to show search result
result_label = tk.Label(window)
result_label.pack()



window.mainloop()
