import os, datetime, re

class Rename() :
  def __init__(self, base_directory_path):
    self.base_path = base_directory_path

  def rename_files(self, product_name_folder_path, product_name):
    """ 문서번호_제품명_용량_상위폴더명_최종수정일 형식으로 변경 """

    def extract_volume_info(file_name):
        """ 파일명에서 '100ml', '200g' 같은 정보를 추출 """
        match = re.search(r'(\d+(?:ml|g))', file_name)
        return match.group(1) if match else ""

    file_dates = {}  # 중복 방지용 딕셔너리

    for root, _, files in os.walk(product_name_folder_path):
        folder_name = os.path.basename(root)

        for file in sorted(files):
            src_path = os.path.join(root, file)
            mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(src_path)).strftime('%Y%m%d')

            # 기존 파일명에서 DOCx_ 문서번호 추출
            doc_match = re.match(r'(DOC\d+)_', file)
            doc_number = doc_match.group(1) if doc_match else "DOC0"

            # 파일명에서 용량 정보 추출
            volume_info = extract_volume_info(file)
            volume_suffix = f"_{volume_info}" if volume_info else ""

            # 새로운 파일명 생성
            new_name = f"{doc_number}_{product_name}_{volume_suffix}_{folder_name}_{mod_time}"

            ext = os.path.splitext(file)[1]
            count = file_dates.get(new_name, 0) + 1
            file_dates[new_name] = count
            new_file_name = f"{new_name}_{count}{ext}" if count > 1 else f"{new_name}{ext}"

            new_path = os.path.join(root, new_file_name)
            os.rename(src_path, new_path)
  
  def rename_all_product_folders(self):
    for brand_line in os.listdir(self.base_directory_path):
        brand_line_path = os.path.join(self.base_directory_path, brand_line)

        # "0_BrandAsset" 폴더는 건너뛰기
        if brand_line == "0_BrandAsset":
            print(f"Skipping brand asset folder: {brand_line}")
            continue

        # BrandLine 폴더 내 BrandName 폴더 찾기
        if os.path.isdir(brand_line_path):
            for product_name in os.listdir(brand_line_path):
                product_name_path = os.path.join(brand_line_path, product_name)
                print(f"Renaming: {product_name}")
                self.rename_files(product_name_path, product_name)
