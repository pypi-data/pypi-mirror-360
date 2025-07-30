import smbls


for host, scan in smbls.run_scan(
    targets=["10.0.0.1", "localhost"],
    creds_list=[
        {
            "domain": "localhost",
            "username": "Administrator",
            "password": "Password1!",
        }
    ],
    share_auth_only=False,
    share_write=False,
    share_list=True,
    share_list_ipc=False,
):
    print(host, scan)
