from functions.get_files_info import get_files_info, get_file_content


def main():
    # print('Test 1: get_files_info("calculator", ".")')
    # print(get_files_info("calculator", "."), end="\n\n")

    # print('Test 2: get_files_info("calculator", "pkg")')
    # print(get_files_info("calculator", "pkg"), end="\n\n")

    # print('Test 3: get_files_info("calculator", "/bin")')
    # print(get_files_info("calculator", "/bin"), end="\n\n")

    # print('Test 4: get_files_info("calculator", "../")')
    # print(get_files_info("calculator", "../"), end="\n\n")

    # print('Test 5: get_file_content("calculator", "lorem.txt")')
    # print(get_file_content("calculator", "lorem.txt"), end="\n\n")

    print('Test 6: get_file_content("calculator", "main.py")')
    print(get_file_content("calculator", "main.py"), end="\n\n")

    print('Test 7: get_file_content("calculator", "pkg/calculator.py")')
    print(get_file_content("calculator", "pkg/calculator.py"), end="\n\n")

    print('Test 8: get_file_content("calculator", "/bin/cat")')
    print(get_file_content("calculator", "/bin/cat"), end="\n\n")


if __name__ == "__main__":
    main()
