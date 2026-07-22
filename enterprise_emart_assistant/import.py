from services.knowledge import upload_knowledge


def www():
    print("www")


def main():
    upload_knowledge("./data/3.txt", id="1")
    # [upload_knowledge(path, id="1") for path in ["./data/1.txt", "./data/2.txt"]]

if __name__ == "__main__":
    main()
