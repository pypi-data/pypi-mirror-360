class eicar_class:
    string = "X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"


def eicar_print():
    try:
        eicar=eicar_class()
        print(eicar.string)
        return True
    except Exception as e:
        print(f"Error while processing: {e}")
        return False

def write_eicar_in_file(file_path:str):
    try:
        eicar=eicar_class()
        with open(file=file_path, mode="a") as f:
            f.write(eicar.string)
        f.close()
        print(f"Successfully wrote Eicar string in {file_path}")
        return True
    except Exception as e:
        print(f"Error while processing: {e}")
        return False


