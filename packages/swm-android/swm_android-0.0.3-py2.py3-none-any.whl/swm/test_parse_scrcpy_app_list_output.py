from swm.cli import parse_scrcpy_app_list_output_single_line

def test():
    text = " - 闲鱼                             com.taobao.idlefish"
    result = parse_scrcpy_app_list_output_single_line(text)
    print(result)
    
if __name__ == "__main__":
    test()