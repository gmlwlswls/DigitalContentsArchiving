import pandas as pd
import os, datetime, re

class DigitalContentsArchiving() :
  def __init__(self, brandname_directory_path):
    self.base_path = brandname_directory_path

  # 1. 네이버 드라이브 파일 - 파일명 변환 & 데이터프레임 생성
  # 문서 번호 | (구)파일명 | 확장자 | 최종 업로드일 | 용량(MB) | 폴더 경로   
  def assign_DocNum_Help(self, naver_drive_path, start_doc_number):
    """ 동일한 파일명, 확장자, 최종 수정일 기준으로 동일한 DOC 번호 부여 """
    doc_counter = start_doc_number
    seen_files = dict()  # {(파일명, 확장자, 수정일): DOC 번호}
    allowed_exts = {'.jpg', '.psd', '.png', '.ai', '.mp4', '.pdf', '.ssg', '.gif', '.fig'}
    data = []

    # 네이버 드라이브 내 문서 번호 부여
    for root, _, files in os.walk(naver_drive_path):
        for file in sorted(files):
             # 이미 DOCx_ 형식이면 건너뜀
            if re.match(r'DOC\d+_', file):
                continue

            file_path = os.path.join(root, file)
            file_name, ext = os.path.splitext(file)
            ext = ext.lower()
            if ext not in allowed_exts :
                continue
            mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d')
            file_size_mb = os.path.getsize(file_path) / (1024 ** 2)
            file_size_str = f"{file_size_mb:.2f}"

            file_key = (file_name, ext, mod_time) # (파일명, 확장자, 최종 업로드일)

            if file_key in seen_files:
                doc_num = seen_files[file_key]
            else:
                doc_num = doc_counter
                seen_files[file_key] = doc_num
                doc_counter += 1

            new_file_name = f"DOC{doc_num:05d}_{file}"
            new_path = os.path.join(root, new_file_name)

            os.rename(file_path, new_path)

            data.append({
                "문서 번호": new_file_name,
                '(구)파일명' : file,
                '확장자' : ext,
                '최종 업로드일' : mod_time,
                '용량(MB)' : file_size_mb,
                '폴더 경로' : root
            })

    # 데이터 프레임 반환
    df = pd.DataFrame(data)
    return df

  
  # 2. 네이버 드라이브 폴더 내 파일명 변환
  # 문서 번호_파일명
  def rename_files_with_docnum(self, naver_drive_csv_path , naver_drive_directory):
    """
    주어진 데이터프레임을 기준으로 파일명을 '문서번호_파일명' 형식으로 변경

    Parameters:
    - naver_drive_csv_path : csv파일이 존재하는 경로 
    - naver_drive_directory (str): 변경할 파일이 존재하는 폴더 경로
    """
    
    df = pd.read_csv(naver_drive_csv_path, encoding= 'cp949')

    for idx, row in df.iterrows():
        doc_num = str(row['문서 번호']).strip() if pd.notnull(row['문서 번호']) else ''
        file_name = str(row['(구)파일명']).strip() if pd.notnull(row['(구)파일명']) else ''
        expected_filename = file_name

        for root, dirs, files in os.walk(naver_drive_directory):
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

  # 3. 로컬 이사 완료 후 폴더트리 내 변수명 변경
  # 문서 번호_제품명_용량_상위 폴더명_최종 수정일
  def __renamefoldertreeHelp(self, product_name_folder_path, product_name):
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

              # 새로운 파일명 생성
              new_name = f"{doc_number}_{product_name}{volume_suffix}_{folder_name}_{mod_time}{country_suffix}"

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
                self.__renamefoldertreeHelp(product_name_path, product_name)\


  # 4. 기존 csv파일과 문서 번호 매치한 병합 csv파일 생성
  # - 이사한 데이터 문서 번호 / 파일명 / 폴더 경로 로 csv 파일 생성
  # ** 매치되지 않은 파일은 그대로 > 이사 제외 사유 기입
  def foldertree_to_xlsx_merge_by_doc(self, existing_csv_path, output_xlsx_path_filename =None):
    """
    기존 CSV 파일과 폴더 정보(문서번호/파일명/폴더경로)를 '문서번호' 기준으로 병합하여 저장

    """
    # 기존 CSV 불러오기
    existing_csv = pd.read_csv(existing_csv_path, encoding= 'cp949')
    root_dir = self.base_path
    
    file_data = []
    for product_line in os.listdir(root_dir):
        product_line_path = os.path.join(root_dir, product_line)
        if os.path.isdir(product_line_path):
            for product_name in os.listdir(product_line_path):
                product_name_path = os.path.join(product_line_path, product_name)
                for folder_path, _, files in os.walk(product_name_path):
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
    df_merged = pd.merge(existing_csv, df_folder, left_on="문서 번호", right_on= '문서 번호_구글', how="left")
    
    # 저장 경로 지정
    if not output_xlsx_path_filename:
        output_xlsx_path_filename = os.path.join(root_dir, "merged_naver_google.csv")

    df_merged.to_excel(output_xlsx_path_filename, index=False)
    print(f"✅ 병합된 xlsx 파일 생성 완료: {output_xlsx_path_filename}")

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

  # 5. 이사한 파일에서 문서 번호 제거
  
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
