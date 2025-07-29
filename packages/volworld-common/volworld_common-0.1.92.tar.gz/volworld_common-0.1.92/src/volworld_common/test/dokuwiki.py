from datetime import datetime


def print_dokuwiki_test_page_header(name: str):
    print("\n\n\n\n\n")
    print("########################################################################")
    print("########################################################################")
    print("########################################################################")
    print("\n\n\n\n\n~~stoggle_buttons~~")
    print("<WRAP roottitle centeralign>")
    print(name)
    print("</WRAP>")
    print(f"  * @{datetime.now()}")
    print("\n\n")


def print_dokuwiki_test_page_footer():
    print("\n\n\n\n\n")
    print("########################################################################")
    print("########################################################################")
    print("########################################################################")
    print("\n\n\n\n\n")
