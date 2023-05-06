import pyotp

totp = pyotp.TOTP('733SF4CUBDJIS7HKRA4LJWGM4HNIH5KB')
print(totp.now())
