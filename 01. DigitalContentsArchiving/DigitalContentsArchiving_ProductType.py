# 제품 타입 결정되면 수정되야할 사항
# 1,2,3과 4,5,6 나눈 별도의 파일명 변경 함수 필요

import pandas as pd
import os, datetime, re

class DigitalContentsArchiving() :
  def __init__(self, brandname_directory_path):
    self.base_path = brandname_directory_path
  
  # 1. 네이버 드라이브 파일 - 파일명 변환
  # 문서 번호_(구)파일명
  def rename_naver_with_DocNum(self, naver_drive_xlsx_path, naver_drive_path):
    """
    주어진 데이터프레임을 기준으로 파일명을 '문서번호_파일명' 형식으로 변경

    Parameters:
    - naver_drive_xlsx_path : xlsx파일이 존재하는 경로 
    - naver_drive_directory (str): 변경할 파일이 존재하는 폴더 경로
    """
    df = pd.read_excel(naver_drive_xlsx_path)
 
    for idx, row in df.iterrows():
       doc_num = str(row['문서 번호']).strip() if pd.notnull(row['문서 번호']) else ''
       file_name = str(row['(구)파일명']).strip() if pd.notnull(row['(구)파일명']) else ''
       expected_filename = file_name

       for root, dirs, files in os.walk(naver_drive_path):
           for f in files:
               if f.strip() == expected_filename:
                   original_path = os.path.join(root, f)
                   new_filename = f"{doc_num}_{f}"
                   new_path = os.path.join(root, new_filename)

                   if not os.path.exists(new_path):
                       os.rename(original_path, new_path)
                       print(f"✅ Renamed: {original_path} -> {new_path}")
                   else:
                       print(f"⚠️ Skipped (already exists): {new_path}") # 이름이 동일한 경우


  # 2. 로컬 이사 완료 후 폴더트리 내 변수명 변경
  # 문서 번호_제품명_용량_상위 폴더명_최종 수정일
  def __renameHelp(self, product_type_path, product_name):
      def extract_volume_info(file_name):
          """ 파일명에서 '100ml', '200g' 같은 정보를 추출 """
          match = re.search(r'(\d+(?:ml|g))', file_name)
          return match.group(1) if match else ""

      def extract_country_keyword(file_name):
              """ 파일명에서 사용 국가 키워드 추출 """
              keywords = ['국내', '국내용', '중국', '중국용', '국내중국겸용', '일본', '일본용'
                          '미국', '북미', '북미용', '유럽', '유럽용', '베트남', '베트남용',
                          '동남아', '동남아시아', '동남아시아용']  # 우선순위 높은 순서로 정렬
              
              country_found = [f"_{kw}" for kw in keywords if kw in file_name]

              return ''.join(country_found) if country_found else ''
          
      file_dates = {}  # 중복 방지용 딕셔너리

      for root, _, files in os.walk(product_type_path):
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

              # 새로운 파일명 생성
              new_name = f"{doc_number}_{product_name}{volume_suffix}_{folder_name}_{mod_time}{country_suffix}"

              ext = os.path.splitext(file)[1]
              count = file_dates.get(new_name, 0) + 1
              file_dates[new_name] = count
              new_file_name = f"{new_name}_{count}{ext}" if count > 1 else f"{new_name}{ext}"

              new_path = os.path.join(root, new_file_name)
              os.rename(src_path, new_path)
  
  def rename(self):
    for product_line in os.listdir(self.base_path):
        product_line_path = os.path.join(self.base_path, product_line)
  
        # "0_BrandAsset" 폴더 & "1_EditionSet"는 건너뛰기
        if product_line == "0_BrandAsset_브랜드자산":
            # print(f"Skipping brand asset folder: {product_line}")
            # continue
            for content_type in os.listdir(product_line_path) :
                content_type_path = os.path.join(product_line_path, content_type)
                self.__renameProductHelp(content_type_path, content_type)
                print(f"Renaming : 0_BrandAsset - {content_type}")    

        if product_line == '1_EditionSet_기획세트' :
            if os.path.isdir(product_line_path):
                for year in os.listdir(product_line_path):
                    year_path = os.path.join(product_line_path, year)
                    if os.path.isdir(year_path) :
                        for plan_type in os.listdir(year_path) : # 채널 / 시즌
                            plan_type_path = os.path.join(year_path, plan_type)
                            if os.path.isdir(plan_type_path) :
                                for edition_type in os.listdir(plan_type_path) :
                                    edition_type_path = os.path.join(plan_type_path, edition_type)
                                    self.__renameHelp(edition_type_path, edition_type)
                                    print(f"Renaming: {edition_type}") 
          
        # ProductLine 폴더 내 ProductName 폴더 찾기
        if os.path.isdir(product_line_path):
            for product_name in os.listdir(product_line_path):
                product_name_path = os.path.join(product_line_path, product_name)
                if os.path.isdir(product_name_path) :
                    for product_type in os.listdir(product_name_path) :
                        product_type_path = os.path.join(product_name_path, product_type)
                        print(f"Renaming: {product_name}")                        
                        self.__renameHelp(product_type_path, product_name)


  # 3. 기존 csv파일과 문서 번호 매치한 병합 csv파일 생성
  # - 이사한 데이터 문서 번호 / 파일명 / 폴더 경로 로 csv 파일 생성
  # ** 매치되지 않은 파일은 그대로 > 이사 제외 사유 기입
  def foldertree_to_xlsx_merge_by_doc(self, existing_xlsx_path, output_xlsx_path_filename =None): 
    """
    기존 xlsx 파일과 폴더 정보(문서번호/파일명/폴더경로)를 '문서번호' 기준으로 병합하여 저장

    """
    # 기존 xlsx 불러오기
    existing_xlsx = pd.read_excel(existing_xlsx_path)
    root_dir = self.base_path
    
    file_data = []
    for product_line in os.listdir(root_dir): 
        product_line_path = os.path.join(root_dir, product_line)
        if os.path.isdir(product_line_path):
            for depth_1st in os.listdir(product_line_path): # depth_1st
                depth_1st_path = os.path.join(product_line_path, depth_1st)
                for folder_path, _, files in os.walk(depth_1st_path):
                    for file in files:
                        file_name, ext = os.path.splitext(file)
                        parts = file_name.split("_", 1)
                        if len(parts) >= 2:
                            doc_number = parts[0]
                            real_name = "_".join(parts[1:]) + ext
                        else:
                            doc_number = ""
                            real_name = file
                        file_data.append([doc_number, real_name, folder_path])
    
    df_folder = pd.DataFrame(file_data, columns=["문서 번호_구글", "(신)파일명", "폴더 경로"])

    # 병합: 문서번호 기준으로 left join
    df_merged = pd.merge(existing_xlsx, df_folder, left_on="문서 번호", right_on= '문서 번호_구글', how="left")
    
    # 저장 경로 지정
    if not output_xlsx_path_filename:
        output_xlsx_path_filename = os.path.join(root_dir, "merged_naver_google.csv")

    df_merged.to_excel(output_xlsx_path_filename, index=False)
    print(f"✅ 병합된 xlsx 파일 생성 완료: {output_xlsx_path_filename}")
  
  # 5. 최종 업로드 전 문서 번호 제거
  def __removeDocNumHelp(self, root_dir):
     """
     파일명 앞의 문서번호 (예: DOC00001_) 를 제거하고
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
        
        if product_line == "0_BrandAsset_브랜드자산":
            for content_type in os.listdir(product_line_path) :
                content_type_path = os.path.join(product_line_path, content_type)
                print(f"Renaming : 0_BrandAsset - {content_type}")    
                self.__removeDocNumHelp(content_type_path)

        if product_line == '1_EditionSet_기획세트' :
            if os.path.isdir(product_line_path):
                for year in os.listdir(product_line_path):
                    year_path = os.path.join(product_line_path, year)
                    if os.path.isdir(year_path) :
                        for plan_type in os.listdir(year_path) : # 채널 / 시즌
                            plan_type_path = os.path.join(year_path, plan_type)
                            if os.path.isdir(plan_type_path) :
                                for edition_type in os.listdir(plan_type_path) :
                                    edition_type_path = os.path.join(plan_type_path, edition_type)
                                    print(f"Renaming: {edition_type}")                 
                                    self.__removeDocNumHelp(edition_type_path, edition_type)

        # ProductLine 폴더 내 ProductName 폴더 찾기
        if os.path.isdir(product_line_path):
            for product_name in os.listdir(product_line_path):
                product_name_path = os.path.join(product_line_path, product_name)
                print(f"Removing_DocNum: {product_name}")
                self.__removeDocNumHelp(product_name_path)

#   # 문서 번호 복원 원할 경우 - 테스트 필요
# def restore_original_filenames(self, merged_naver_google_xlsx_path):
#     """
#     문서번호 제거 및 원래 파일명 복원
#     mapping_csv_path: (문서 번호, (구)파일명, 폴더 경로) 정보가 담긴 csv
#     """
#     df = pd.read_excel(merged_naver_google_xlsx_path, index = False)
#     restored_count = 0

#     for _, row in df.iterrows():
#         doc_num = str(row['문서 번호']).strip()
#         old_name = str(row['(구)파일명']).strip()
#         folder_path = row['폴더 경로'].strip()
        
#         # 현재 파일명 (문서번호로 시작하는 파일)
#         current_file_pattern = f"{doc_num}_{old_name}"
#         current_path = os.path.join(folder_path, current_file_pattern)

#         if os.path.exists(current_path):
#             new_path = os.path.join(folder_path, old_name)
#             counter = 1

#             # 중복 방지용 이름 만들기
#             while os.path.exists(new_path):
#                 base, ext = os.path.splitext(old_name)
#                 new_name = f"{base}_({counter}){ext}"
#                 new_path = os.path.join(folder_path, new_name)
#                 counter += 1

#             os.rename(current_path, new_path)
#             restored_count += 1
#             print(f"🔁 Restored: {current_file_pattern} → {os.path.basename(new_path)}")
#         else:
#             print(f"⚠️ 파일 없음: {current_file_pattern}")

#     print(f"✅ 원래 파일명 복원 완료: 총 {restored_count}개 파일 변경됨")
