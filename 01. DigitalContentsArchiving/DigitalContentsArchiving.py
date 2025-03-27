import pandas as pd
import os, datetime, re, csv

class DigitalContentsArchiving() :
  def __init__(self, brandname_directory_path):
    self.base_path = brandname_directory_path
  
  # 1. 네이버 드라이브 파일 - 파일명 변환
  # 문서 번호_파일명
  def renamelocal_withDocNum(self, naver_drive_csv_path, naver_drive_directory):
      """
      CSV에 정의된 파일명 및 확장자와 로컬 파일을 비교해,
      일치하는 경우 해당 파일에 문서번호를 붙여서 로컬 파일의 이름을 변경함.

      Parameters:
      - csv_path : naver_drive 리스트인 csv 파일 경로
      - naver_drive_directory : 로컬 파일들이 존재하는 폴더 경로
      """
      df = pd.read_csv(naver_drive_csv_path, encoding= 'cp949')

      for idx, row in df.iterrows():
          doc_id = str(row['문서 번호']).strip() if pd.notnull(row['문서 번호']) else ''
          file_name = str(row['(구)파일명']).strip() if pd.notnull(row['(구)파일명']) else ''

          expected_filename = file_name

          for root, dirs, files in os.walk(naver_drive_directory):
              for f in files:
                  if f.strip() == expected_filename:
                      original_path = os.path.join(root, f)
                      new_filename = f"{doc_id}_{f}"
                      new_path = os.path.join(root, new_filename)

                      if not os.path.exists(new_path):
                          os.rename(original_path, new_path)
                          print(f"✅ Renamed: {original_path} -> {new_path}")
                      else:
                          print(f"⚠️ Skipped (already exists): {new_path}") # 이름이 동일한 경우
  
  # 2. 로컬 이사 완료 후 폴더트리 내 변수명 변경
  # 문서 번호_제품명_용량_상위 폴더명_최종 수정일

  def __renamefoldertreeHelp(self, product_name_folder_path, product_name):
      def extract_volume_info(file_name):
          """ 파일명에서 '100ml', '200g' 같은 정보를 추출 """
          match = re.search(r'(\d+(?:ml|g))', file_name)
          return match.group(1) if match else ""

      def extract_country_keyword(file_name):
              """ 파일명에서 사용 국가 키워드 추출 """
              keywords = ['국내', '국내용', '중국', '중국용', '국내중국겸용', 
                          '북미용', '북미', '유럽', '유럽용', '베트남', '베트남용']  # 우선순위 높은 순서로 정렬
              for keyword in keywords:
                  if keyword in file_name:
                      return f"_{keyword}"
              return ""
      
      def extract_dozen_keyword(file_name) :
              keywords= ['복수']
              for keyword in keywords :
                if keyword in file_name :
                  return f"_{keyword}"
              return ''
          
      file_dates = {}  # 중복 방지용 딕셔너리

      for root, _, files in os.walk(product_name_folder_path):
          folder_name = os.path.basename(root)

          for file in sorted(files):
              src_path = os.path.join(root, file)
              mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(src_path)).strftime('%Y%m%d')

              # 기존 파일명에서 DOCx_ 문서번호 추출
              doc_match = re.match(r'(DOC\d+)_', file)
              doc_number = doc_match.group(1) if doc_match else ""

              # 파일명에서 용량 정보 추출
              volume_info = extract_volume_info(file)
              volume_suffix = f"_{volume_info}" if volume_info else ""

              # 사용 국가 키워드 추출
              country_suffix = extract_country_keyword(file)

              # 복수 제품 키워드 추출
              dozen_suffix = extract_dozen_keyword(file)

              # 새로운 파일명 생성
              new_name = f"{doc_number}_{product_name}{volume_suffix}_{folder_name}_{mod_time}{country_suffix}{dozen_suffix}"

              ext = os.path.splitext(file)[1]
              count = file_dates.get(new_name, 0) + 1
              file_dates[new_name] = count
              new_file_name = f"{new_name}_{count}{ext}" if count > 1 else f"{new_name}{ext}"

              new_path = os.path.join(root, new_file_name)
              os.rename(src_path, new_path)
  
  def renamefoldertree(self):
    for product_line in os.listdir(self.base_path):
        product_line_path = os.path.join(self.base_path, product_line)
  
        # "0_BrandAsset" 폴더는 건너뛰기
        if product_line == "0_BrandAsset":
            print(f"Skipping brand asset folder: {product_line}")
            continue
          
        # ProductLine 폴더 내 ProductName 폴더 찾기
        if os.path.isdir(product_line_path):
            for product_name in os.listdir(product_line_path):
                product_name_path = os.path.join(product_line_path, product_name)
                print(f"Renaming: {product_name}")
                self.__renamefoldertreeHelp(product_name_path, product_name)

  def __removeDocNumHelp(self, root_dir):
     """
     파일명 앞의 문서번호 (예: DOC001_) 를 제거하고
     같은 이름 존재 시 _(1), _(2) ... 붙여 중복 방지
     """
     renamed_count = 0
     
     for folder_path, _, files in os.walk(root_dir):
         for file in files:
            # 정규표현식으로 DOCxxx_ 패턴 추출
            match = re.match(r'^(DOC\d+_)(.+)', file)
            if match:
                doc_prefix, rest_of_name = match.groups()
                old_path = os.path.join(folder_path, file)
                
                base_name, ext = os.path.splitext(rest_of_name)
                new_path = os.path.join(folder_path, rest_of_name)
                counter = 1

                # 파일명이 이미 존재하면 _(1), _(2) 붙여서 충돌 방지
                while os.path.exists(new_path):
                    new_name = f"{base_name}_({counter}){ext}"
                    new_path = os.path.join(folder_path, new_name)
                    counter += 1

                os.rename(old_path, new_path)
                renamed_count += 1
                print(f"🔁 Renamed: {file} → {os.path.basename(new_path)}")
     print(f"✅ 문서번호 제거 완료: 총 {renamed_count}개 파일 이름 변경됨")


  def removeDocNum(self): # DocNum 제거 후 파일명 동일한 경우 (1) (2)
      for product_line in os.listdir(self.base_path):
        product_line_path = os.path.join(self.base_path, product_line)
        
        # "0_BrandAsset" 폴더는 건너뛰기
        if product_line == "0_BrandAsset":
            print(f"Skipping brand asset folder: {product_line}")
            continue
        
        # ProductLine 폴더 내 ProductName 폴더 찾기
        if os.path.isdir(product_line_path):
            for product_name in os.listdir(product_line_path):
                product_name_path = os.path.join(product_line_path, product_name)
                print(f"Removing_DocNum: {product_name}")
                self.__removeDocNumHelp(product_name_path)
