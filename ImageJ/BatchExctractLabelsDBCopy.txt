macro "Batch Convert to Binary" {
      dir = getDirectory("Choose a Directory ");
      list = getFileList(dir);
      //setBatchMode(true);
      for (i=0; i<list.length; i++) {
          path = dir+list[i];
          open(path);
          run("root analysis QR");
		  if (isOpen("ROI Manager")) { 
				selectWindow("ROI Manager"); 
				run("Close"); 
				}
		  //run("Close"); 	


          open(path);
          run("root analysis bounds");
		  if (isOpen("ROI Manager")) { 
				selectWindow("ROI Manager"); 
				run("Close"); 
				}
		  
	 
//		  dotIndex = lastIndexOf(path, ".");
//          if (dotIndex!=-1)
//              path = substring(path, 0, dotIndex); // remove extension
//          close();
      }
  }
 

