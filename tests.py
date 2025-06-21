from functions.get_files_info import get_files_info


def main():
    print('Test 1: get_files_info("calculator", ".")')
    print(get_files_info("calculator", "."), end="\n\n")

    print('Test 2: get_files_info("calculator", "pkg")')
    print(get_files_info("calculator", "pkg"), end="\n\n")

    print('Test 3: get_files_info("calculator", "/bin")')
    print(get_files_info("calculator", "/bin"), end="\n\n")

    print('Test 4: get_files_info("calculator", "../")')
    print(get_files_info("calculator", "../"), end="\n\n")


if __name__ == "__main__":
    main()
