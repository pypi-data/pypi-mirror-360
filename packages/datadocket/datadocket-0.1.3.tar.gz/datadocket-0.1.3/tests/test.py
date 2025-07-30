import os
import datadocket as dd

test_dir = os.path.join(os.path.dirname(__file__), 'data')

def test_txt():
    txt_path = os.path.join(test_dir, 'test.txt')
    data = dd.load.Txt(txt_path)    
    print('Loaded TXT:', repr(data))
    save_path = os.path.join(test_dir, 'test_out.txt')
    dd.save.Txt(save_path, data)
    assert dd.load.Txt(save_path) == data
    print('TXT save/load round-trip successful.')
    dd.utils.Delete(save_path)
    assert not os.path.exists(save_path)
    print('TXT file deleted successfully.')

def test_json():
    json_path = os.path.join(test_dir, 'test.json')
    data = dd.load.Json(json_path)
    print('Loaded JSON:', data)
    save_path = os.path.join(test_dir, 'test_out.json')
    dd.save.Json(save_path, data, indent=2)
    assert dd.load.Json(save_path) == data
    print('JSON save/load round-trip successful.')
    dd.utils.Delete(save_path)
    assert not os.path.exists(save_path)
    print('JSON file deleted successfully.')

def test_csv():
    csv_path = os.path.join(test_dir, 'test.csv')
    data = dd.load.Csv(csv_path)
    print('Loaded CSV:', data)
    save_path = os.path.join(test_dir, 'test_out.csv')
    dd.save.Csv(save_path, data)
    assert dd.load.Csv(save_path) == data
    print('CSV save/load round-trip successful.')
    dd.utils.Delete(save_path)
    assert not os.path.exists(save_path)
    print('CSV file deleted successfully.')

def main():
    test_txt()
    test_json()
    test_csv()
    print('All tests passed!')

if __name__ == '__main__':
    main() 