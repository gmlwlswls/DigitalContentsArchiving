function get_filelist_with_subfolder() {						
  // get This Folder						
  var thisFile = DriveApp.getFileById(SpreadsheetApp.getActive().getId());						
  var folders = thisFile.getParents()						
  var folderId;						
  while (folders.hasNext()) {						
  var folder = folders.next();						
  folderId = folder.getId();						
  break;						
  }						
  // get ID of This Folder						
  var daforder = DriveApp.getFolderById(folderId);						
  // clear this sheet						
  var sheet = SpreadsheetApp.getActiveSheet();						
  sheet.clear();						
  var srow = 1;						
  // Set Header						
  sheet.getRange(srow, 1).setValue("(신)파일명");						
  sheet.getRange(srow, 2).setValue("구글드라이브 경로");						
  sheet.getRange(srow, 3).setValue("만들어진 날짜(이동일)");						
  sheet.getRange(srow, 4).setValue("소유자");						
  sheet.getRange(srow, 5).setValue("설명");						
  // Set Header Color						
  var range = sheet.getRange("A1:H1");						
  range.setBackground("#d9d9d9");						
  // Set Format of URL link						
  range = sheet.getRange("H:H");						
  range.setWrapStrategy(SpreadsheetApp.WrapStrategy.CLIP);						
  // write file list from This Folder						
  var name_thisfolder = daforder.getName();						
  _write_file_from_folder(daforder, sheet, name_thisfolder);						
  // sub folders						
  var depth1_folders = daforder.getFolders();						
  while(depth1_folders.hasNext()){						
  var depth1_folder = depth1_folders.next();						
  // Logger.log(" this: " + name_thisfolder + " sub: " + subfolder.getName());						
  name_folder = name_thisfolder + ">" + depth1_folder.getName();						
  _write_file_from_folder( depth1_folder, sheet, name_folder )						
  var depth2_folders = depth1_folder.getFolders();						
  while(depth2_folders.hasNext()){						
  var depth2_folder = depth2_folders.next();						
  name_folder = name_thisfolder + ">" + depth1_folder.getName() + ">" + depth2_folder.getName();						
  _write_file_from_folder( depth2_folder, sheet, name_folder )						
  var depth3_folders = depth2_folder.getFolders();						
  while(depth3_folders.hasNext()){						
  var depth3_folder = depth3_folders.next();						
  name_folder = name_thisfolder + ">" + depth1_folder.getName() + ">"						
  #ERROR!						
  _write_file_from_folder( depth3_folder, sheet, name_folder )						
  } // end while depth3						
  } // end while depth2						
  } // end while depth1						
  }						
  /**						
  * 폴더 내 파일 리스트를 시트에 쓰기						
  */						
  function _write_file_from_folder(ifolder, isheet, ifolder_name){						
  var dafiles = ifolder.getFiles();						
  // write folder info						
  var srow = isheet.getLastRow() + 1;						
  isheet.getRange(srow, 2).setValue(ifolder_name);						
  isheet.getRange(srow, 3).setValue(ifolder.getDateCreated());						
  var range = isheet.getRange("A"+srow+":H"+srow);						
  range.setBackground("#f3f3f3");						
  // write file list 파일 리스트 쓰기						
  while(dafiles.hasNext()){						
  var dafile = dafiles.next();						
  var file_name = dafile.getName();						
  srow = srow + 1;						
  // Write file info						
  isheet.getRange(srow, 1).setValue(file_name); // 파일 이름						
  isheet.getRange(srow, 2).setValue(ifolder_name); // 폴더 경로						
  isheet.getRange(srow, 3).setValue(dafile.getDateCreated()); // 만들어진 날짜(이동일)						
  isheet.getRange(srow, 4).setValue(dafile.getOwner().getName()); // 소유자						
  isheet.getRange(srow, 5).setValue(dafile.getDescription())						
  }						
  }						